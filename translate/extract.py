#!/usr/bin/env python3
import re
import sys
import os
from pathlib import Path

def extract_msg_strings(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # Busca todas las ocurrencias de MSG="..." y TITLE="..."
    # Soporta comillas dobles y saltos de línea (poco probables, pero seguros)
    pattern = r'(?:MSG|TITLE)\s*=\s*"([^"]*)"'
    matches = re.findall(pattern, content)

    # Lista de patrones que NO se traducen
    NO_TRANSLATE_PREFIXES = (
        "action:prompt_end",
        "action:prompt_button_group_start",
        "action:prompt_button {type}|_IFS_COLORS_PORT_TYPE_DIALOG PORT={port} TYPE={type}|primary",
        "action:prompt_button {type}|_IFS_COLORS_PORT_TYPE_DIALOG PORT={port} TYPE={type}",
        "action:prompt_button_group_end",
        "action:prompt_footer_button Close|_IFS_COLORS:",
        "action:prompt_show",
        "action:prompt_button P{port}:{ifs_types[port-1]}|_IFS_COLORS_TYPE PORT={port}",
        "action:prompt_button P{port}:—",
        "action:prompt_button C{tool|int + 1}:{types[tool|int]}||ifs-color-slot warning|{colors[tool|int]}",
        "action:prompt_button >P{port}|||{colors[tool|int]}",
        "action:prompt_button P{port}|_IFS_COLORS_ASSIGN TOOL={tool} PORT={port}",
        "{variable|lower|replace('_', ' ')|title} : {printer['gcode_macro _IFS_VARS'][variable|lower]}",
        "{params.VARIABLE|lower|replace('_', ' ')|title} : {printer['gcode_macro _IFS_VARS'][params.VARIABLE|lower]}",
        "{var}: {printer.save_variables.variables['ifs_'+var]}",
        "Bambufy - {title}: {msg}",
        "{msg}",
        "action:prompt_begin Bambufy - {title}",
        "action:prompt_text {msg}",
        "action:prompt_text {tip}"
    )

    filtered = [
        s for s in matches
        if not any(s.startswith(prefix) for prefix in NO_TRANSLATE_PREFIXES)
    ]

    return list(dict.fromkeys(filtered))  # elimina duplicados, mantiene orden

if __name__ == "__main__":
    en_cfg = sys.argv[1] if len(sys.argv) > 1 else "en/bambufy.cfg"
    strings = extract_msg_strings(en_cfg)

    # Generar base.pot (formato gettext, pero solo con msgid = texto inglés)
    pot_path = "base.pot"
    with open(pot_path, "w", encoding="utf-8") as f:
        f.write('msgid ""\n')
        f.write('msgstr ""\n')
        f.write('"Content-Type: text/plain; charset=UTF-8\\n"\n')
        f.write('"Language: en\\n"\n\n')

        for s in strings:
            # Escapamos comillas y backslashes para .po
            escaped = s.replace('"', '\\"').replace('\\', '\\\\')
            f.write(f'msgid "{escaped}"\n')
            f.write(f'msgstr ""\n\n')

    print(f"✅ {len(strings)} unique messages extracted → {pot_path}")