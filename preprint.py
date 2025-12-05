#!/usr/bin/env python3
import sys
import os
import re
import hashlib
from typing import List
from typing import Optional

PRINTER_PATH = "/tmp/printer"

def read_file(path: str) -> str:
    """Read the full content of a text file with UTF-8 encoding."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def detect_slicer(text: str) -> str:
    """Detect which slicer generated the file based on header content."""
    for line in text.splitlines()[:20]:
        if "BambuStudio" in line:
            return "bambu"
        elif "OrcaSlicer" in line:
            return "orca"
    return ""

def already_post_processed(text: str) -> Optional[str]:
    """Return the _IFS_COLORS line if the G-code was already post-processed."""
    match = re.search(r"^;\s*_IFS_COLORS.*$", text, re.MULTILINE)
    return match.group(0).lstrip("; ").rstrip() + "\n" if match else None

def find_metadata_line(text: str, key: str) -> str:
    """Extract the line value for a given metadata key."""
    start = text.find(key)
    if start == -1:
        return ""
    end = text.find("\n", start)
    return text[start:end].strip()

def extract_first_layer(text: str) -> str:
    """Return concatenated G-code for all first layers"""
    layer_height = find_metadata_line(text, "; initial_layer_print_height").split("=")[-1].strip()
    pattern = rf"\n;AFTER_LAYER_CHANGE\n;{re.escape(layer_height)}(.*?)\n;AFTER_LAYER_CHANGE"
    first_layers = []
    for layer in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
        first_layers.append(layer.group(1).strip())
    return "\n".join(first_layers)

def get_exclude_object_define(gcode: str) -> Optional[str]:
    """bounding box first layer"""
    lines = gcode.splitlines()
    minx = miny = float("inf")
    maxx = maxy = float("-inf")

    for line in lines:
        parts = line.split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd.startswith(("G1", "G2", "G3")):
            x = y = e = None
            for p in parts[1:]:
                if p.startswith("X"):
                    x = float(p[1:])
                elif p.startswith("Y"):
                    y = float(p[1:])
                elif p.startswith("E"):
                    e = float(p[1:])
            if e is None or e <= 0:
                continue  # Ignore movements without extrusion
            if x is not None:
                minx = min(minx, x)
                maxx = max(maxx, x)
            if y is not None:
                miny = min(miny, y)
                maxy = max(maxy, y)
    

    if minx == float("inf") or miny == float("inf"):
        return None

    center_x = (minx + maxx) / 2
    center_y = (miny + maxy) / 2
    exclude_str = (
        f"EXCLUDE_OBJECT_DEFINE NAME=First_Layer CENTER={center_x:.4f},{center_y:.4f} "
        f"POLYGON=[[{minx:.6f},{miny:.6f}],"
        f"[{maxx:.6f},{miny:.6f}],"
        f"[{maxx:.6f},{maxy:.6f}],"
        f"[{minx:.6f},{maxy:.6f}]]"
    )
    return exclude_str

def parse_list_from_comment(text: str, key: str) -> List[str]:
    """Parse a semicolon-separated list from a comment line."""
    start = text.find(key)
    if start == -1:
        return []
    end = text.find("\n", start)
    return [v.strip() for v in text[start + len(key):end].split(";") if v.strip()]

def parse_feedrates(text: str) -> str:
    """Extract and convert feedrates from filament_max_volumetric_speed."""
    start = text.find("; filament_max_volumetric_speed =")
    if start == -1:
        return ""
    end = text.find("\n", start)
    values = (float(v) for v in text[start + len("; filament_max_volumetric_speed ="):end].split(","))
    return ",".join(str(round(v / 4 * 3 * 60)) for v in values)

def parse_change_filament_gcode_version(text: str) -> str:
    """Extract version from change_filament_gcode"""
    match = re.search(r";\s*Bambufy:\s*v*([\d.]+)", text)
    version = match.group(1) if match else '1.2.2'
    return version

def extract_bambu_metadata(text: str) -> str:
    """Extract Bambu slicer-specific metadata and build the end G-code block."""
    def get_line_value(key: str) -> str:
        return find_metadata_line(text, key).split("=")[-1].split(",")[0].strip() if find_metadata_line(text, key) else ""

    nozzle_temp = get_line_value("; nozzle_temperature =")
    bed_temp = get_line_value("; hot_plate_temp =")
    filament_colour = find_metadata_line(text, "; filament_colour =")
    nozzle_diameter = find_metadata_line(text, "; nozzle_diameter =")
    filament_type = find_metadata_line(text, "; filament_type =")
    layer_height = find_metadata_line(text, "; layer_height =")
    est_time = find_metadata_line(text, "; estimated printing time")
    filament_id = find_metadata_line(text, "; filament_settings_id = ")
    used_mm_line = find_metadata_line(text, "; total filament length")
    filament_used_mm = f"; filament used [mm] = {used_mm_line.split(':')[1].strip()}" if used_mm_line else ""
    used_g_line = find_metadata_line(text, "; total filament weight")
    filament_used_g = ""
    total_filament_used_g = ""
    if used_g_line:
        weights = used_g_line.split(':')[1].strip()
        filament_used_g = f"; filament used [g] = {weights}"
        total_filament_used_g = f"; total filament used [g] = {sum(float(x) for x in weights.split(','))}"

    return (
        f"{filament_used_mm}\n"
        f"{filament_used_g}\n"
        f"{total_filament_used_g}\n"
        f"{est_time}\n"
        f"{filament_type}\n"
        f"{filament_id}\n"
        f"{layer_height}\n"
        f"{nozzle_diameter}\n"
        f"{filament_colour}\n"
        f"; first_layer_bed_temperature = {bed_temp}\n"
        f"; first_layer_temperature = {nozzle_temp}\n"
    )

def write_to_file(path: str, content: str):
    """Write text content to file."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        print(f"Error when writing in {path}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Use: preprint.py <file.gcode>")
        sys.exit(1)

    file_path = sys.argv[1]
    gcode = read_file(file_path)

    # Check if file already contains _IFS_COLORS header
    existing = already_post_processed(gcode)
    if existing:
        print("Already post-processed")
        print(existing)
        write_to_file(PRINTER_PATH, existing)
        sys.exit(0)
    
    slicer = detect_slicer(gcode)
    from_slicer = any(k.startswith("SLIC3R_") for k in os.environ)

    # Extract metadata
    tools = sorted({m.group(1) for m in re.finditer(r"^\s*T(\d+)", gcode, re.MULTILINE)})
    colors = parse_list_from_comment(gcode, "; filament_colour =")
    types = parse_list_from_comment(gcode, "; filament_type =")
    feedrates = parse_feedrates(gcode)
    first_layer = extract_first_layer(gcode)
    exclude = get_exclude_object_define(first_layer)
    bambu_metadata = ("\n" + extract_bambu_metadata(gcode)) if slicer == "bambu" else ""
    version = parse_change_filament_gcode_version(gcode)

    # _IFS_COLORS header
    ifs_colors = (
        f'_IFS_COLORS START=1 '
        f'TYPES={",".join(types)} '
        f'E_FEEDRATES={feedrates} '
        f'COLORS={",".join(c[1:] for c in colors)} '
        f'TOOLS={",".join(tools)} '
        f'VERSION={version} '
        f'EXCLUDE="{exclude}"'
    )
    print(ifs_colors + "\n")

    try:
        lines = gcode.splitlines(keepends=True)
        if lines and lines[0].startswith("; MD5:"):
            lines.pop(0)
            gcode = "".join(lines)
        new_gcode_str = "; " + ifs_colors + "\n" + gcode + bambu_metadata
        new_gcode_bytes = new_gcode_str.encode("utf-8")
        md5_hash = hashlib.md5(new_gcode_bytes).hexdigest()
        md5_line = b"; MD5:" + md5_hash.encode("ascii") + b"\n"
        final_gcode = md5_line + new_gcode_bytes
        with open(file_path, "wb") as f:
            f.write(final_gcode)
    except OSError as e:
        print(f"Error when writing in {file_path}: {e}")

    # Append to printer if not called from slicer
    if not from_slicer:
        write_to_file(PRINTER_PATH, ifs_colors + "\n")

if __name__ == "__main__":
    main()