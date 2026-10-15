#!/usr/bin/env python3
import polib  # pip install polib
import re
import sys
import os
from pathlib import Path

def load_translations(po_file):
    po = polib.pofile(po_file)
    trans = {}
    for entry in po:
        # Clave = msgid (texto inglés original), valor = msgstr (traducción)
        if entry.msgstr.strip():
            # Desescapar para usar en reemplazo
            key = entry.msgid.replace('\\"', '"').replace('\\\\', '\\')
            val = entry.msgstr.replace('\\"', '"').replace('\\\\', '\\')
            trans[key] = val
    return trans

def replace_messages(input_cfg, trans_dict, output_cfg):
    with open(input_cfg, encoding='utf-8') as f:
        content = f.read()

    # Solo se traduce lo marcado por el autor con ===...===.
    # Sin traducción, se deja el original (y se quitan las marcas).
    def replacer(match):
        orig_msg = match.group(2).strip()
        new_msg = trans_dict.get(orig_msg, orig_msg)
        return f'{new_msg}'

    content = re.sub(
        r'(===)(.*?)(===)',
        replacer,
        content
    )

    # Guardar
    Path(output_cfg).parent.mkdir(parents=True, exist_ok=True)
    with open(output_cfg, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python generate.py <root_cfg> <lang>")
        print("Ej:  python generate.py bambufy.cfg es")
        sys.exit(1)

    en_cfg = sys.argv[1] if len(sys.argv) > 1 else "../bambufy.cfg"
    lang = sys.argv[2]
    trans = load_translations(f"{lang}.po")
    replace_messages(en_cfg, trans, f"../{lang}/bambufy.cfg")
    print(f"✅ Generated {lang}/bambufy.cfg with {len(trans)} translations applied")
