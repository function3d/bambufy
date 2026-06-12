#!/bin/sh

VARS="/opt/config/mod_data/variables.cfg"

if [ ! -f "$VARS" ]; then
  echo "Error: $VARS not found"
  exit 1
fi

bambufy_version=$(sed -n "s/^bambufy_version = //p" "$VARS")

#rename ifs_xxxxx to bambufy_xxxxx (variables.cfg)
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
' "$VARS" > "$VARS.tmp" && mv "$VARS.tmp" "$VARS"

#web = mainsail|fluidd (variables.cfg)
WEB="fluidd"; grep -q "^CLIENT=mainsail" /opt/config/mod_data/web.conf && WEB="mainsail"
if grep -q "^[[:space:]]*web[[:space:]]*=" "$VARS"; then
    sed -i "s|^[[:space:]]*web[[:space:]]*=.*|web = '$WEB'|" "$VARS"
else
    echo "web = '$WEB'" >> "$VARS"
fi

if grep -q "^[[:space:]]*bambufy_mesh[[:space:]]*=" "$VARS"; then
    sed -i "s|^[[:space:]]*bambufy_mesh[[:space:]]*=.*|bambufy_mesh = 0|" "$VARS"
else
    echo "bambufy_mesh = 0" >> "$VARS"
fi

#display_off_timeout = 10 (variables.cfg)
if grep -qE '^[[:space:]]*display_off_timeout[[:space:]]*=' "$VARS" 2>/dev/null; then
    sed -i 's/^[[:space:]]*display_off_timeout[[:space:]]*=.*/display_off_timeout = 10/' "$VARS"
else
    echo "display_off_timeout = 10" >> "$VARS"
fi

#use kamp_offset as gcode_offset if exist
kamp_offset=$(sed -n "s/^kamp_offsets = //p" "$VARS")
if [ -n "$kamp_offset" ]; then
    sed -i "/^\(kamp\|gcode\)_offsets = /d" "$VARS"
    echo "gcode_offsets = $kamp_offset" >> "$VARS"
elif [ -z "$bambufy_version" ]; then #version empty
  sed -i "/^gcode_offsets = /d" "$VARS"
  echo "gcode_offsets = {'z': '0'}" >> "$VARS"
fi

#g28_tenz
CONF=/opt/config/printer.base.cfg
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
.v-dialog .bambufy-button{
  width: 80px !important;
  padding: 0 8px !important;
  margin: 3px !important;
}
.v-dialog .bambufy-color{
  width: 40px !important;
  min-width: 40px !important;
  padding: 0 8px !important;
  margin: 3px !important;
}
.v-dialog .bambufy-type{
  width: 54px !important;
  min-width: 54px !important;
  padding: 0 8px !important;
  margin: 3px !important;
}
EOF

VERSION=1
#Version control for reinstallation if necessary.
if grep -q "^[[:space:]]*bambufy_version[[:space:]]*=" "$VARS"; then
    sed -i "s|^[[:space:]]*bambufy_version[[:space:]]*=.*|bambufy_version = $VERSION|" "$VARS"
else
    echo "bambufy_version = $VERSION" >> "$VARS"
fi

#uninstall g28_tenz: bambufy already include g28_tenz
sed -i "/plugins\/g28_tenz\//d" /opt/config/mod_data/plugins.cfg
