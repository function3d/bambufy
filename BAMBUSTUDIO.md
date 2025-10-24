# Machine G-code for Bambu Studio and Orca slicer
## Machine start G-code Bambu Studio

```
START_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer_single] TOOL={initial_no_support_extruder}
T{initial_no_support_extruder}
SET_PRINT_STATS_INFO TOTAL_LAYER=[total_layer_count]
```

## Machine start G-code Orca slicer

```
START_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer_single] TOOL={initial_no_support_extruder}
SET_PRINT_STATS_INFO TOTAL_LAYER=[total_layer_count]
```

## Machine end G-code

```
END_PRINT
```

## Layer change G-code

```
;AFTER_LAYER_CHANGE
;[layer_z]
SET_PRINT_STATS_INFO CURRENT_LAYER={layer_num + 1}
; layer num/total_layer_count: {layer_num+1}/[total_layer_count]
```

##  Change filament G-code

```
{if old_filament_temp < new_filament_temp}
M104 S[new_filament_temp]
{endif}
G1 Z{max_layer_z + 3.0} F1200
M204 S9000
T[next_extruder]
{if next_extruder < 255}
{if flush_length > 0}
_GOTO_TRASH
{endif}
{if flush_length_1 > 1}
; FLUSH_START
{if flush_length_1 > 23.7}
G1 E23.7 F{old_filament_e_feedrate} ; do not need pulsatile flushing for start part
G1 E{(flush_length_1 - 23.7) * 0.04} F{old_filament_e_feedrate/2}
G1 E{(flush_length_1 - 23.7) * 0.21} F{old_filament_e_feedrate}
G1 E{(flush_length_1 - 23.7) * 0.04} F{old_filament_e_feedrate/2}
G1 E{(flush_length_1 - 23.7) * 0.21} F{new_filament_e_feedrate}
G1 E{(flush_length_1 - 23.7) * 0.04} F{new_filament_e_feedrate/2}
G1 E{(flush_length_1 - 23.7) * 0.21} F{new_filament_e_feedrate}
M106 P1 S128
G1 E{(flush_length_1 - 23.7) * 0.04} F{new_filament_e_feedrate/2}
G1 E{(flush_length_1 - 23.7) * 0.21} F{new_filament_e_feedrate}
{else}
G1 E{flush_length_1} F{old_filament_e_feedrate}
{endif}
; FLUSH_END
{endif}
{if flush_length_1 > 45 && flush_length_2 > 1}
; WIPE
M106 P1 S0
G1 E-[new_retract_length_toolchange] F1800
_SBROS_TRASH
G1 E[new_retract_length_toolchange] F1800
{endif}

M104 S[new_filament_temp]

{if flush_length_2 > 1}
; FLUSH_START
G1 E{flush_length_2 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_2 * 0.21} F{new_filament_e_feedrate}
G1 E{flush_length_2 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_2 * 0.21} F{new_filament_e_feedrate}
G1 E{flush_length_2 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_2 * 0.21} F{new_filament_e_feedrate}
M106 P1 S128
G1 E{flush_length_2 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_2 * 0.21} F{new_filament_e_feedrate}
; FLUSH_END
{endif}

{if flush_length_2 > 45 && flush_length_3 > 1}
; WIPE
M106 P1 S0
G1 E-[new_retract_length_toolchange] F1800
_SBROS_TRASH
G1 E[new_retract_length_toolchange] F1800
{endif}

{if flush_length_3 > 1}
; FLUSH_START
G1 E{flush_length_3 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_3 * 0.21} F{new_filament_e_feedrate}
G1 E{flush_length_3 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_3 * 0.21} F{new_filament_e_feedrate}
G1 E{flush_length_3 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_3 * 0.21} F{new_filament_e_feedrate}
M106 P1 S128
G1 E{flush_length_3 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_3 * 0.21} F{new_filament_e_feedrate}
; FLUSH_END
{endif}

{if flush_length_3 > 45 && flush_length_4 > 1}
; WIPE
M106 P1 S0
G1 E-[new_retract_length_toolchange] F1800
_SBROS_TRASH
G1 E[new_retract_length_toolchange] F1800
{endif}

{if flush_length_4 > 1}
; FLUSH_START
G1 E{flush_length_4 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_4 * 0.21} F{new_filament_e_feedrate}
G1 E{flush_length_4 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_4 * 0.21} F{new_filament_e_feedrate}
G1 E{flush_length_4 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_4 * 0.21} F{new_filament_e_feedrate}
M106 P1 S128
G1 E{flush_length_4 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_4 * 0.21} F{new_filament_e_feedrate}
; FLUSH_END
{endif}


{if flush_length > 0}
 ;WIPE
 M106 P1 S0
 G1 E-[new_retract_length_toolchange] F1800
 _SBROS_TRASH
 G1 Y220 ;Exit trash
{endif}


{if layer_z <= (initial_layer_print_height + 0.001)}
M204 S[initial_layer_acceleration]
{else}
M204 S[default_acceleration]
{endif}
{endif}
```

## Pause G-code
```
PAUSE
```
