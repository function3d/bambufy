#!/bin/sh

JSON_FILE="/opt/config/mod_data/klipper_data.json"
TMP_PRINTER="/tmp/printer"

if [ "$1" = "test" ] && [ -f "$JSON_FILE" ]; then
    echo "!! Found unfinished print !!"
    echo "_ZRESTORE" > "$TMP_PRINTER"
    exit
fi

if [ -f "$JSON_FILE" ]; then
  read X Y Z E <<EOF
$(grep '"position":[^]]*' "$JSON_FILE" | sed -E 's/.*\[(.*)\].*/\1/' | tr ',' ' ')
EOF
  EXCLUDED=$(grep -o '"excluded_objects":[^]]*' "$JSON_FILE" | sed -E 's/.*\[(.*)/\1/')
  BED_TARGET=$(grep '"bed_target"' "$JSON_FILE" | sed -E 's/.*"bed_target": *([0-9.]+).*/\1/')
  EXTRUDER_TARGET=$(grep '"extruder_target"' "$JSON_FILE" | sed -E 's/.*"extruder_target": *([0-9.]+).*/\1/')
  ABSOLUTE_COORDS=$(grep '"absolute_coords"' "$JSON_FILE" | grep -o 'true\|false')
  E_MODE=$(grep '"e_mode"' "$JSON_FILE" | sed -E 's/.*"e_mode": *"([^"]+)".*/\1/')
  FAN_SPEED=$(grep '"fan_speed"' "$JSON_FILE" | sed -E 's/.*"fan_speed": *([0-9.]+).*/\1/')
  FILE_PATH=$(grep '"file_path"' "$JSON_FILE" | sed -E 's/.*"file_path": *"([^"]+)".*/\1/')
  FILE_POS=$(grep '"file_position"' "$JSON_FILE" | sed -E 's/.*"file_position": *([0-9.]+).*/\1/')
  EXTRUDE_FACTOR=$(grep '"extrude_factor"' "$JSON_FILE" | sed -E 's/.*"extrude_factor": *([0-9.]+).*/\1/')
  Z_OFFSET=$(grep '"z_offset"' "$JSON_FILE" | sed -E 's/.*"z_offset": *([-0-9.]+).*/\1/')
  PA_VALUE=$(grep '"pressure_advance"' "$JSON_FILE" | grep '"value"' | sed -E 's/.*"value": *([0-9.]+).*/\1/')
  PA_SMOOTH=$(grep '"pressure_advance"' "$JSON_FILE" | grep '"smooth_time"' | sed -E 's/.*"smooth_time": *([0-9.]+).*/\1/')
  RETRACT_LEN=$(grep '"retract_length"' "$JSON_FILE" | sed -E 's/.*"retract_length": *([0-9.]+).*/\1/')
  RETRACT_SPEED=$(grep '"retract_speed"' "$JSON_FILE" | sed -E 's/.*"retract_speed": *([0-9.]+).*/\1/')
  UNRETRACT_LEN=$(grep '"unretract_length"' "$JSON_FILE" | sed -E 's/.*"unretract_length": *([0-9.]+).*/\1/')
  UNRETRACT_SPEED=$(grep '"unretract_speed"' "$JSON_FILE" | sed -E 's/.*"unretract_speed": *([0-9.]+).*/\1/')


  echo "ZEXCLUDE FILENAME=\"$(basename "$FILE_PATH")\"" >> "$TMP_PRINTER"

  PREFIX_TEXT=$(dd if="$FILE_PATH" bs=1 count="$FILE_POS" 2>/dev/null)
  LAST_START_LINE=$(printf "%s" "$PREFIX_TEXT" | grep "^EXCLUDE_OBJECT_START" | tail -n 1)
  if [ -n "$LAST_START_LINE" ]; then
    echo "$LAST_START_LINE" >> "$TMP_PRINTER"
  fi

  for OBJ in $(echo "$EXCLUDED" | tr ',' ' '); do
    echo "EXCLUDE_OBJECT NAME=$OBJ" >> "$TMP_PRINTER"
  done
  
  echo "SET_GCODE_OFFSET Z=$Z_OFFSET MOVE=0" >> "$TMP_PRINTER"
  echo "SET_PRESSURE_ADVANCE ADVANCE=$PA_VALUE SMOOTH_TIME=$PA_SMOOTH" >> "$TMP_PRINTER"
  echo "SET_RETRACTION RETRACT_LENGTH=$RETRACT_LEN RETRACT_SPEED=$RETRACT_SPEED UNRETRACT_EXTRA_LENGTH=$UNRETRACT_LEN UNRETRACT_SPEED=$UNRETRACT_SPEED" >> "$TMP_PRINTER"
  echo "M221 S$(echo "$EXTRUDE_FACTOR * 100" | bc)" >> "$TMP_PRINTER"
  
  echo "M140 S$BED_TARGET" >> "$TMP_PRINTER"
  echo "M109 S$EXTRUDER_TARGET" >> "$TMP_PRINTER"
  echo "_G28" >> "$TMP_PRINTER"

  if awk -v z="$Z" 'BEGIN { exit (z > 0) ? 0 : 1 }'; then
    NEW_Z=$(awk -v z="$Z" 'BEGIN { printf "%.3f", z + 5 }')
    echo "G1 Z$NEW_Z" >> "$TMP_PRINTER"
  fi
  echo "M190 S$BED_TARGET" >> "$TMP_PRINTER"
  echo "_T_CURRENT" >> "$TMP_PRINTER"
  echo "_GOTO_TRASH" >> "$TMP_PRINTER"
  echo "_CLEAR_REZINA" >> "$TMP_PRINTER"
  echo "POOP FLUSH_LENGTH=45" >> "$TMP_PRINTER"
  echo "_CLEAR_REZINA" >> "$TMP_PRINTER"
  echo "G1 Y220 F3000" >> "$TMP_PRINTER"
  echo "G1 E2 F300" >> "$TMP_PRINTER"

  echo "M106 S$(echo "$FAN_SPEED * 255" | bc)" >> "$TMP_PRINTER"
  echo "G0 X$X F6000" >> "$TMP_PRINTER"
  echo "G0 Y$Y" >> "$TMP_PRINTER"
  echo "G0 Z$Z" >> "$TMP_PRINTER"

  if [ "$ABSOLUTE_COORDS" = "true" ]; then
    echo "G90" >> "$TMP_PRINTER"
  else
    echo "G91" >> "$TMP_PRINTER"
  fi

  if [ "$E_MODE" = "relative" ]; then
    echo "M83" >> "$TMP_PRINTER"
  else
    echo "M82" >> "$TMP_PRINTER"
  fi

  echo "G92 E$E" >> "$TMP_PRINTER"

  echo "M23 $(basename "$FILE_PATH")" >> "$TMP_PRINTER"
  echo "M26 S$FILE_POS" >> "$TMP_PRINTER"
  echo "M24" >> "$TMP_PRINTER"

fi
