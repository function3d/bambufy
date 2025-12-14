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
/^ifs_/ {
  sub(/^ifs_/, "bambufy_")
  print
  next
}
{ print }
' "$FILE" > "$FILE.tmp" && mv "$FILE.tmp" "$FILE"
