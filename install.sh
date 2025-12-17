#!/bin/sh

FILE="/opt/config/mod_data/variables.cfg"

if [ ! -f "$FILE" ]; then
  echo "Error: $FILE not found"
  exit 1
fi

awk '
/^\[Variables\]/ {
  print
  next
}
/^ifs_motion_sensor/ {
  print
  next
}
/^ifs_/ {
  sub(/^ifs_/, "bambufy_")
  print
  next
}
{ print }
' "$FILE" > "$FILE.tmp" && mv "$FILE.tmp" "$FILE"

WEB="fluidd"; grep -q "^CLIENT=mainsail" /opt/config/mod_data/web.conf && WEB="mainsail"

if grep -q "^[[:space:]]*web[[:space:]]*=" "$FILE"; then
    sed -i "s|^[[:space:]]*web[[:space:]]*=.*|web = '$WEB'|" "$FILE"
else
    echo "web = '$WEB'" >> "$FILE"
fi
