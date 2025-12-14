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
    return list(dict.fromkeys(matches))  # elimina duplicados, mantiene orden

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