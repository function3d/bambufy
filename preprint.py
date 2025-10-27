#!/usr/bin/env python3
import sys
import os
import re
import math

def compute_bbox_from_block(block):
    """Calcula el bounding box (xmin, ymin, xmax, ymax) de un bloque G-code."""
    re_cmd = re.compile(r'^(?P<cmd>G[0-9]+)\b', re.IGNORECASE)
    re_xy = re.compile(r'([XY])\s*([-+]?\d*\.?\d+)')
    re_ij = re.compile(r'([IJ])\s*([-+]?\d*\.?\d+)')

    cur_x = cur_y = None
    xmin = ymin = float('inf')
    xmax = ymax = -float('inf')

    def update_bbox(x, y):
        nonlocal xmin, xmax, ymin, ymax
        xmin = min(xmin, x)
        xmax = max(xmax, x)
        ymin = min(ymin, y)
        ymax = max(ymax, y)

    def angle_in_sweep(theta, start, end, ccw=True):
        def norm(a): return a % (2*math.pi)
        s, e, t = norm(start), norm(end), norm(theta)
        if ccw:
            return s <= t <= e if e >= s else t >= s or t <= e
        else:
            return e <= t <= s if e <= s else not (s < t < e)

    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith(';'):
            continue

        m_cmd = re_cmd.match(line)
        cmd = m_cmd.group('cmd').upper() if m_cmd else None
        coords = {k: float(v) for k, v in re_xy.findall(line)}
        ij = {k: float(v) for k, v in re_ij.findall(line)}

        if cmd in ('G0', 'G1') or cmd is None:
            nx, ny = coords.get('X', cur_x), coords.get('Y', cur_y)
            if nx is None or ny is None:
                continue
            if cur_x is None or cur_y is None:
                cur_x, cur_y = nx, ny
                update_bbox(nx, ny)
                continue
            update_bbox(cur_x, cur_y)
            update_bbox(nx, ny)
            cur_x, cur_y = nx, ny

        elif cmd in ('G2', 'G3'):
            if cur_x is None or cur_y is None or 'X' not in coords or 'Y' not in coords:
                continue
            nx, ny = coords['X'], coords['Y']
            cx, cy = cur_x + ij.get('I', 0.0), cur_y + ij.get('J', 0.0)
            r = math.hypot(cur_x - cx, cur_y - cy)
            start_ang = math.atan2(cur_y - cy, cur_x - cx)
            end_ang = math.atan2(ny - cy, nx - cx)
            ccw = (cmd == 'G3')
            update_bbox(cur_x, cur_y)
            update_bbox(nx, ny)
            for test_ang in (0, math.pi/2, math.pi, 3*math.pi/2):
                if angle_in_sweep(test_ang, start_ang, end_ang, ccw=ccw):
                    tx, ty = cx + r * math.cos(test_ang), cy + r * math.sin(test_ang)
                    update_bbox(tx, ty)
            cur_x, cur_y = nx, ny

    if xmin == float('inf'):
        return None
    return xmin, ymin, xmax, ymax


def extract_wipe_block_from_file(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    start = text.find('; WIPE_TOWER_START')
    end = text.find('; WIPE_TOWER_END', start if start != -1 else 0)
    if start == -1 or end == -1:
        return None
    return text[start:end + len('; WIPE_TOWER_END')]


def extract_filament_info(filename):
    re_tool = re.compile(r"^\s*T(\d+)")

    tools = set()
    colors, types = [], []
    feedrates = ""

    with open(filename, 'r', encoding='utf-8', errors='ignore') as gcode:
        for line in gcode:
            if m := re_tool.match(line):
                tools.add(m.group(1))
                continue
            if not colors and line.startswith("; filament_colour ="):
                colors = line.split("=")[1].strip().split(";")
                continue
            if not types and line.startswith("; filament_type ="):
                types = line.split("=")[1].strip().split(";")
                continue
            if not feedrates and line.startswith("; filament_max_volumetric_speed ="):
                values = (float(x) for x in line.split("=")[1].split(","))
                feedrates = ','.join(str(round(v / 2 * 60)) for v in values)
                continue

    return tools, colors, types, feedrates


if len(sys.argv) < 2:
    print("Uso: script.py <file.gcode>")
    sys.exit(1)

file_path = sys.argv[1]
basename = os.path.basename(file_path)

tools, colors, types, feedrates = extract_filament_info(file_path)
wipe_block = extract_wipe_block_from_file(file_path)

# Escribir información de colores, tipos, herramientas, etc.
try:
    with open("/tmp/printer", "a", encoding='utf-8') as f:
        exclude = ''
        if wipe_block:
            bbox = compute_bbox_from_block(wipe_block)
            if bbox:
                xmin, ymin, xmax, ymax = bbox
                cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
                polygon = (
                    f"[[{xmin:.6f},{ymin:.6f}],"
                    f"[{xmax:.6f},{ymin:.6f}],"
                    f"[{xmax:.6f},{ymax:.6f}],"
                    f"[{xmin:.6f},{ymax:.6f}]]"
                )
                exclude = (
                    f'EXCLUDE_OBJECT_DEFINE NAME=Wipe_Tower '
                    f'CENTER={cx:.6f},{cy:.6f} POLYGON={polygon}'
                )
            else:
                print("No se encontraron coordenadas en el bloque WIPE_TOWER.")
        f.write(
            f'_IFS_COLORS START=1 '
            f'FILENAME="{basename}" '
            f'TYPES={",".join(types)} '
            f'E_FEEDRATES={feedrates} '
            f'COLORS={",".join(c[1:] for c in colors)} '
            f'TOOLS={",".join(sorted(tools))} '
            f'EXCLUDE="{exclude}"\n'
        )
except OSError as e:
    print(f"Error al escribir en /tmp/printer: {e}")
