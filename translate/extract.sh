#!/bin/bash
set -e

python extract.py ../bambufy.cfg

for lang in en es fr de it pt cs ru tr ja ko zh; do
  echo "   → $lang"
  msgmerge --backup=none -U $lang.po base.pot
  msgattrib --no-obsolete $lang.po -o $lang.po
done

echo "✅ Done. Now translate the empty entries in Poedit."
echo "💡 Then run: generate.sh"