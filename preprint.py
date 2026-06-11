#!/usr/bin/env python3
import sys
import os
import re
import hashlib
from typing import Optional
import shutil
from pathlib import Path
import tempfile

PRINTER_PATH = "/tmp/printer"

def write_to_file(path: str, content: str):
    """Write text content to file."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        print(f"Error when writing in {path}: {e}")

def get_exclude_object_define(lines) -> Optional[str]:
    """bounding box first layer"""
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

def parse_list_from_line(line, separator=";"):
    """Parse a list from a text"""
    match = re.search(r"=\s*(.+)$", line)
    if match:
        return [item.strip() for item in match.group(1).split(separator) if item.strip()]
    return []

def main():
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
    after_layer_change_re = re.compile(r"^;\s*AFTER_LAYER_CHANGE.*$")
    already_processed_re = re.compile(r"^;\s*_IFS_COLORS.*$")
    
    tools = set()
    colors = None
    types = None
    feedrates = []
    first_layer = []
    first_after_layer_change = False
    second_after_layer_change = False
    exclude = None
    bambu_metadata = ""
    version = None
    slicer = ""
    filament_used_g=""
    filament_used_mm=""
    estimated_printing_time=""
    total_filament_used_g=""
    filament_type=""
    filament_settings_id=""
    layer_height=""
    nozzle_diameter=""
    nozzle_diameter=""
    nozzle_diameter=""
    nozzle_temperature=""

    file_path = sys.argv[1]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):

            if line_num < 10:
                match = already_processed_re.search(line)
                if match:
                    print("Already post-processed")
                    existing = match.group(0).lstrip("; ").rstrip() + "\n"
                    print(existing)
                    write_to_file(PRINTER_PATH, existing)
                    sys.exit(0)
                
                if bambu_re.search(line):
                    slicer = "bambu"
                elif orca_re.search(line):
                    slicer = "orca"
            
            if colors is None and color_re.search(line):
                colors = parse_list_from_line(line)

            if not feedrates and feedrate_re.search(line):
                feedrates = parse_list_from_line(line,",")
                
            if types is None and type_re.search(line):
                types = parse_list_from_line(line)
                
            if version is None:
                v_match = version_re.search(line)
                if v_match:
                    version = v_match.group(1) if v_match else '1.2.2'
                
            if not first_after_layer_change:
                first_after_layer_change = bool(after_layer_change_re.search(line))
            elif not second_after_layer_change:
                second_after_layer_change = bool(after_layer_change_re.search(line))
                first_layer.append(line)

            t_match = tool_re.match(line)
            if t_match:
                tools.add(t_match.group(1))

            if slicer == "bambu" and line.startswith(";"):
                if line.startswith("; nozzle_temperature ="):
                    nozzle_temperature = line.split('=')[1].strip().split(',')[0]
                if line.startswith("; hot_plate_temp ="):
                    hot_plate_temp = line.split('=')[1].strip().split(',')[0]
                if line.startswith("; filament_colour ="):
                    filament_colour = line
                if line.startswith("; nozzle_diameter ="):
                    nozzle_diameter = line
                if line.startswith("; filament_type ="):
                    filament_type = line
                if line.startswith("; layer_height ="):
                    layer_height = line
                if line.startswith("; estimated printing time"):
                    estimated_printing_time = line
                if line.startswith("; filament_settings_id = "):
                    filament_settings_id = line
                if line.startswith("; total filament length"):
                    filament_used_mm = f"; filament used [mm] = {line.split(':')[1].strip()}"
                if line.startswith("; total filament weight"):
                    total_filament_weight = line.split(':')[1].strip()
                    filament_used_g = f"; filament used [g] = {total_filament_weight}"
                    total_filament_used_g = f"; total filament used [g] = {sum(float(x) for x in total_filament_weight.split(','))}"

    if version is None:
        version = '1.2.2'
    
    tools = sorted(tools)
    feedrates = ",".join(str(round(float(v) / 4 * 3 * 60)) for v in feedrates)
    exclude = get_exclude_object_define(first_layer)
    from_slicer = any(k.startswith("SLIC3R_") for k in os.environ)
    if slicer == "bambu":
        bambu_metadata = (f"\n{filament_used_mm}\n"
            f"{filament_used_g}\n"
            f"{total_filament_used_g}\n"
            f"{estimated_printing_time}"
            f"{filament_type}"
            f"{filament_settings_id}"
            f"{layer_height}"
            f"{nozzle_diameter}"
            f"{filament_colour}"
            f"; first_layer_bed_temperature = {hot_plate_temp}\n"
            f"; first_layer_temperature = {nozzle_temperature}\n")

    # _IFS_COLORS header
    ifs_colors = (
        f'_IFS_COLORS START=1 '
        f'TYPES={",".join(types)} '
        f'E_FEEDRATES={feedrates} '
        f'COLORS={",".join(c[1:] for c in colors)} '
        f'TOOLS={",".join(tools)} '
        f'VERSION={version} '
        f'EXCLUDE="{exclude}"\n'
    )
    print(ifs_colors)

    md5 = hashlib.md5()
    md5.update(("; " + ifs_colors).encode('utf-8'))
    with open(file_path, 'rb') as f:
        for line_num, line in enumerate(f):
            if line_num == 0 and re.search(rb';\s*MD5\s*[:=]', line, re.IGNORECASE):
                continue
            md5.update(line)
    md5.update(bambu_metadata.encode('utf-8'))
    md5.hexdigest()

    file_path = Path(file_path)
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, dir=file_path.parent) as tmp:
        tmp.write(("; MD5:" + md5.hexdigest() + "\n").encode('utf-8'))
        tmp.write(("; " + ifs_colors).encode('utf-8'))
        with open(file_path, 'rb') as f:
            shutil.copyfileobj(f, tmp)
        tmp.write(bambu_metadata.encode('utf-8'))
    Path(tmp.name).replace(file_path)

    # Append to printer if not called from slicer
    if not from_slicer:
        write_to_file(PRINTER_PATH, ifs_colors + "\n")

if __name__ == "__main__":
    main()