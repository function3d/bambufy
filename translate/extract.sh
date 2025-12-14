#!/bin/bash
set -e

python extract.py ../en/bambufy.cfg

for lang in es fr de it pt cs ru tr; do
  echo "   → $lang"
  msgmerge -U $lang.po base.pot
done

echo "✅ Done. Now translate the empty entries in Poedit."
echo "💡 Then run: generate.sh"