#!/usr/bin/env python3
"""preprint.py — bambufy pre-print gcode processor.

Injects an _IFS_COLORS header and MD5 checksum into a gcode file using a
two-pass streaming algorithm so that peak memory is O(longest line), not
O(file size).  This makes the script safe to run on printers with very
limited RAM (e.g. FlashForge AD5X: 485 MB RAM, no swap).

Algorithm
---------
Pass 1 (bounded scan, at most DEFINE_SCAN_LINES lines):
    Read lines until EXCLUDE_OBJECT_DEFINE entries stop appearing or the
    scan limit is reached.  Collect all header metadata needed to build the
    _IFS_COLORS line.  If the _IFS_COLORS marker is already present at
    line 2 (index 1), return immediately — file is already processed.

MD5 pass (streaming binary):
    Compute the MD5 checksum over the header + original file content +
    optional Bambu Studio metadata trailer.

Pass 2 (streaming binary write):
    Open a temp file in the same directory as the original.  Write the new
    MD5 line (line 1) and _IFS_COLORS header (line 2), then stream all
    original lines through unchanged (dropping a stale MD5 line at position
    0 if one exists).  On success, atomically rename temp → original.  On
    failure, delete the temp file and leave the original untouched.

Implementation notes
--------------------
Risk 1 — EXCLUDE_OBJECT_DEFINE location:
    Controlled by DEFINE_SCAN_LINES (default 200).  If no entries are found
    within the limit, processing continues with an empty object list.

Risk 2 — Temp file disk space:
    The temp file is deleted in the except handler before re-raising, so a
    partial temp file is never left alongside the original.

Risk 3 — Line endings:
    All file I/O uses binary mode ('rb'/'wb') to preserve \\r\\n vs \\n exactly.

Risk 4 — Atomic rename:
    os.replace() is atomic on POSIX (both paths on the same filesystem,
    which is guaranteed because the temp file is in the same directory).
"""
import sys
import os
import re
import hashlib
from typing import List, Optional
from pathlib import Path

PRINTER_PATH = "/tmp/printer"

# Maximum number of lines to scan in Pass 1.  OrcaSlicer and Bambu Studio
# both emit all relevant header comments (filament colours, types, feedrates,
# EXCLUDE_OBJECT_DEFINE entries, version tag) within the first ~100 lines.
# 200 provides a comfortable safety margin.
DEFINE_SCAN_LINES = 200


def write_to_file(path: str, content: str) -> None:
    """Append text content to a file (typically the Klipper printer pipe)."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        print(f"Error when writing in {path}: {e}")


def parse_list_from_line(line: str, separator: str = ";") -> List[str]:
    """Parse a separated list from a slicer comment line (e.g. '; key = a;b;c')."""
    match = re.search(r"=\s*(.+)$", line)
    if match:
        return [item.strip() for item in match.group(1).split(separator) if item.strip()]
    return []


def main() -> None:  # noqa: C901 — complexity is inherent; keep flat
    if len(sys.argv) < 2:
        print("Use: preprint.py <file.gcode>")
        sys.exit(1)

    tool_re = re.compile(r"^\s*T(\d+)")
    color_re = re.compile(r";\s*filament_colour\s*=")
    feedrate_re = re.compile(r"; filament_max_volumetric_speed =")
    type_re = re.compile(r";\s*filament_type\s*=")
    version_re = re.compile(r";\s*Bambufy:\s*v*([\d.]+)")
    bambu_re = re.compile(r";.*BambuStudio")
    orca_re = re.compile(r";.*OrcaSlicer")
    already_processed_re = re.compile(r"^;\s*_IFS_COLORS.*$")
    exclude_define_re = re.compile(r"^EXCLUDE_OBJECT_DEFINE\s+")
    md5_line_re = re.compile(rb";\s*MD5\s*[:=]", re.IGNORECASE)

    tools: set = set()
    colors: Optional[List[str]] = None
    types: Optional[List[str]] = None
    feedrates: List[str] = []
    exclude_defines: List[str] = []  # EXCLUDE_OBJECT_DEFINE lines from gcode header
    version: Optional[str] = None
    slicer: str = ""

    # Bambu Studio-specific header metadata (empty for OrcaSlicer gcode)
    nozzle_temperature: str = ""
    hot_plate_temp: str = ""
    filament_colour: str = ""
    nozzle_diameter: str = ""
    filament_type_line: str = ""
    layer_height: str = ""
    estimated_printing_time: str = ""
    filament_settings_id: str = ""
    filament_used_mm: str = ""
    filament_used_g: str = ""
    total_filament_used_g_str: str = ""

    file_path = Path(sys.argv[1])

    # -------------------------------------------------------------------------
    # Pass 1: Early-exit scan — reads at most DEFINE_SCAN_LINES lines.
    #
    # Opened in binary mode so line endings are never normalised (Risk 3).
    # Each raw_line is decoded only for regex matching; no large buffer is
    # kept in memory.
    # -------------------------------------------------------------------------
    with open(file_path, "rb") as f:
        for line_num, raw_line in enumerate(f):
            if line_num >= DEFINE_SCAN_LINES:
                break

            # Decode for matching; errors='replace' keeps us going on binary noise.
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")

            # Already-processed guard: _IFS_COLORS lives at line 2 (index 1) in
            # a file that has already been run through preprint.py.
            if line_num == 1 and already_processed_re.match(line):
                print("Already post-processed")
                existing = line.lstrip("; ").rstrip() + "\n"
                print(existing)
                write_to_file(PRINTER_PATH, existing)
                sys.exit(0)

            # Slicer detection from the opening lines
            if line_num < 10:
                if bambu_re.search(line):
                    slicer = "bambu"
                elif orca_re.search(line):
                    slicer = "orca"

            # Filament colour list
            if colors is None and color_re.search(line):
                colors = parse_list_from_line(line)

            # Max volumetric feedrates
            if not feedrates and feedrate_re.search(line):
                feedrates = parse_list_from_line(line, ",")

            # Filament type list
            if types is None and type_re.search(line):
                types = parse_list_from_line(line)

            # Bambufy version tag
            if version is None:
                v_match = version_re.search(line)
                if v_match:
                    version = v_match.group(1)

            # Slicer-generated Klipper object-exclusion defines.
            # OrcaSlicer emits these near the top of the file when object
            # exclusion is enabled; they replace the previous approach of
            # computing a synthetic bounding box from first-layer G-code.
            if exclude_define_re.match(line):
                exclude_defines.append(line)

            # Tool references (Tx commands in the header region)
            t_match = tool_re.match(line)
            if t_match:
                tools.add(t_match.group(1))

            # Bambu Studio header metadata
            if slicer == "bambu" and line.startswith(";"):
                if line.startswith("; nozzle_temperature ="):
                    nozzle_temperature = line.split("=")[1].strip().split(",")[0]
                elif line.startswith("; hot_plate_temp ="):
                    hot_plate_temp = line.split("=")[1].strip().split(",")[0]
                elif line.startswith("; filament_colour ="):
                    filament_colour = line
                elif line.startswith("; nozzle_diameter ="):
                    nozzle_diameter = line
                elif line.startswith("; filament_type ="):
                    filament_type_line = line
                elif line.startswith("; layer_height ="):
                    layer_height = line
                elif line.startswith("; estimated printing time"):
                    estimated_printing_time = line
                elif line.startswith("; filament_settings_id = "):
                    filament_settings_id = line
                elif line.startswith("; total filament length"):
                    filament_used_mm = f"; filament used [mm] = {line.split(':')[1].strip()}"
                elif line.startswith("; total filament weight"):
                    fw = line.split(":")[1].strip()
                    filament_used_g = f"; filament used [g] = {fw}"
                    total_filament_used_g_str = (
                        f"; total filament used [g] = "
                        f"{sum(float(x) for x in fw.split(','))}"
                    )

    # -------------------------------------------------------------------------
    # Build the _IFS_COLORS header from Pass 1 data.
    # -------------------------------------------------------------------------
    tools_sorted = sorted(tools)
    feedrates_str = (
        ",".join(str(round(float(v) / 4 * 3 * 60)) for v in feedrates)
        if feedrates else ""
    )
    # Join multiple EXCLUDE_OBJECT_DEFINE entries with "; " as delimiter.
    # Falls back to the string "None" when none were found (preserving prior
    # behaviour where get_exclude_object_define() returned None).
    exclude_str: Optional[str] = "; ".join(exclude_defines) if exclude_defines else None

    from_slicer = any(k.startswith("SLIC3R_") for k in os.environ)

    bambu_metadata = ""
    if slicer == "bambu":
        bambu_metadata = (
            f"\n{filament_used_mm}\n"
            f"{filament_used_g}\n"
            f"{total_filament_used_g_str}\n"
            f"{estimated_printing_time}"
            f"{filament_type_line}"
            f"{filament_settings_id}"
            f"{layer_height}"
            f"{nozzle_diameter}"
            f"{filament_colour}"
            f"; first_layer_bed_temperature = {hot_plate_temp}\n"
            f"; first_layer_temperature = {nozzle_temperature}\n"
        )

    ifs_colors = (
        f"_IFS_COLORS START=1 "
        f"TYPES={','.join(types or [])} "
        f"E_FEEDRATES={feedrates_str} "
        f"COLORS={','.join(c[1:] for c in (colors or []))} "
        f"TOOLS={','.join(tools_sorted)} "
        f"VERSION={version or '1.2.2'} "
        f'EXCLUDE="{exclude_str}"\n'
    )
    print(ifs_colors)

    # -------------------------------------------------------------------------
    # MD5 computation — full streaming binary pass.
    # Hash covers: "; " + ifs_colors + all original lines (skipping a stale
    # MD5 line at position 0) + optional bambu_metadata trailer.
    # -------------------------------------------------------------------------
    md5 = hashlib.md5()
    md5.update(("; " + ifs_colors).encode("utf-8"))
    with open(file_path, "rb") as f:
        for line_num, raw_line in enumerate(f):
            if line_num == 0 and md5_line_re.search(raw_line):
                continue  # Exclude stale MD5 line from hash
            md5.update(raw_line)
    if bambu_metadata:
        md5.update(bambu_metadata.encode("utf-8"))
    md5_hex = md5.hexdigest()

    # -------------------------------------------------------------------------
    # Pass 2: Streaming binary write to temp, then atomic rename.
    #
    # Output structure:
    #   Line 1  — ; MD5:<hex>
    #   Line 2  — ; _IFS_COLORS ...
    #   Lines 3+ — original file content (stale MD5 line at index 0 dropped)
    #   [bambu_metadata appended at end, if any]
    #
    # Temp file lives in the same directory as the original so os.replace()
    # is always on the same filesystem (POSIX atomic guarantee, Risk 4).
    # Files opened in binary mode to preserve line endings exactly (Risk 3).
    # -------------------------------------------------------------------------
    tmp_path = file_path.parent / (file_path.name + ".tmp")
    try:
        with open(file_path, "rb") as f_in, open(tmp_path, "wb") as f_out:
            # New MD5 line (line 1) and _IFS_COLORS header (line 2)
            f_out.write(("; MD5:" + md5_hex + "\n").encode("utf-8"))
            f_out.write(("; " + ifs_colors).encode("utf-8"))

            # Stream original content, dropping the stale MD5 line if present
            for line_num, raw_line in enumerate(f_in):
                if line_num == 0 and md5_line_re.search(raw_line):
                    continue  # Strip stale MD5; new one was written above
                f_out.write(raw_line)

            if bambu_metadata:
                f_out.write(bambu_metadata.encode("utf-8"))

        # Atomic rename: temp → original.  Original is not touched until this
        # succeeds (Risk 4).
        os.replace(tmp_path, file_path)

    except Exception:
        # Best-effort cleanup: remove temp so no corrupt partial file is left
        # alongside the original (Risk 2).
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise

    # Notify the Klipper printer pipe when invoked by Klipper (not the slicer)
    if not from_slicer:
        write_to_file(PRINTER_PATH, ifs_colors + "\n")


if __name__ == "__main__":
    main()
