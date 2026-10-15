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

#update custom.css
cat > "/opt/config/.theme/custom.css" << 'EOF'
.v-dialog .v-btn{
    min-width: 40px !important;
    padding: 0 8px !important;
    margin: 3px !important;
}
EOF

if grep -q "^[[:space:]]*bambufy_mesh[[:space:]]*=" "$VARS"; then
    sed -i "s|^[[:space:]]*bambufy_mesh[[:space:]]*=.*|bambufy_mesh = 0|" "$VARS"
else
    echo "bambufy_mesh = 0" >> "$VARS"
fi

echo "FIRMWARE_RESTART" >/tmp/printer