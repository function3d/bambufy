#!/bin/sh

CONF=/opt/config/printer.base.cfg
VARS="/opt/config/mod_data/variables.cfg"

awk '
  /^\[stepper_z\]/ {
    in_z = 1
    print
    next
  }
  /^\[/ {
    in_z = 0
    print
    next
  }
  in_z && /^[[:space:]]*position_endstop[[:space:]]*:/ && !/^[[:space:]]*;/ {
    print ";" $0
    next
  }
  { print }
' ${CONF} > /tmp/tmp && mv /tmp/tmp $CONF

if grep -q "^[[:space:]]*bambufy_mesh[[:space:]]*=" "$VARS"; then
    sed -i "s|^[[:space:]]*bambufy_mesh[[:space:]]*=.*|bambufy_mesh = 0|" "$VARS"
else
    echo "bambufy_mesh = 0" >> "$VARS"
fi