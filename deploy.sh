#!/bin/bash
# Deploy bambufy configs to AD5X printer (bambufy only works on AD5X).
# Usage: ./deploy.sh [lang]   (default: all languages)
set -e
PRINTER_IP="192.168.100.35"
PRINTER_USER="root"
PRINTER_PASS="root"  # Z-Mod AD5X factory default
cd "$(dirname "$0")"
venv/bin/python -c "import polib" 2>/dev/null || { echo "venv sin polib: recrea venv e instala polib"; exit 1; }
source venv/bin/activate
cd translate
./generate.sh
cd ..
for lang in ${1:-en es fr de it pt cs ru tr ja ko zh}; do
  f="$lang/bambufy.cfg"
  if cat "$f" | sshpass -p "$PRINTER_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$PRINTER_USER@$PRINTER_IP" "cat > /usr/data/config/mod_data/plugins/bambufy/$f"; then
    echo "  ✅ $f"
  else
    echo "  ✗ $f"
    exit 1
  fi
done
