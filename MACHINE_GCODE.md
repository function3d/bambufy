# Machine G-code for Bambu Studio and Orca slicer

## Bambu Studio: Machine start G-code

```
START_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer_single] TOOL={initial_no_support_extruder}
T{initial_no_support_extruder}
SET_PRINT_STATS_INFO TOTAL_LAYER=[total_layer_count]
```

## Orca slicer: Machine start G-code

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

##  Bambu Studio: Change filament G-code

```
; Machine: AD5X
; Bambufy: v1.2.3
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
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
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
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
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
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
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
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
G1 E{flush_length_4 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_4 * 0.21} F{new_filament_e_feedrate}
; FLUSH_END
{endif}
{if flush_length > 0}
; WIPE
M106 P1 S0
G1 E-[new_retract_length_toolchange] F1800
_SBROS_TRASH
{endif}
G1 Y220 ;Exit trash
{endif}
M104 S[new_filament_temp]
{if layer_z <= (initial_layer_print_height + 0.001)}
M204 S[initial_layer_acceleration]
{else}
M204 S[default_acceleration]
{endif}
```
## Orca slicer
If you have created your profile without using the 3MF I provided, then take these settings into account in addition to these Machines gcode:
- Printer settings
  - Multimaterial
    - Filament load time: 23
    - Filament unload time: 23
  - Extruder
    - Retraction when switching material length: 2
    - Extra length on restart: 0
- Material setting
  - Multimaterial
    - Minimal purge on prime tower: 15
   
##  Orca slicer: Change filament G-code, unified: poop and nopoop
With this unified gcode for filament change, you only need to enable or disable this option to purge in the tower(nopoop) or in the form of poops

<img width="618" height="419" alt="image" src="https://github.com/user-attachments/assets/9554da95-0ee1-4b77-a690-e9f084397978" />

```
; Machine: AD5X
; Bambufy: v1.2.3
{if old_filament_temp < new_filament_temp}
M104 S[new_filament_temp]
{endif}

M204 S9000

{if purge_in_prime_tower || flush_length == 0}
{if toolchange_count > 1}
_NOPOOP
{endif}
G1 Z{max_layer_z + 3.0} F1200
T[next_extruder]
{else}
G1 Z{max_layer_z + 3.0} F1200
T[next_extruder]
{if next_extruder < 255}
{if flush_length > 1}
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
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
G1 E{(flush_length_1 - 23.7) * 0.04} F{new_filament_e_feedrate/2}
G1 E{(flush_length_1 - 23.7) * 0.21} F{new_filament_e_feedrate}
{else}
G1 E{flush_length_1} F{old_filament_e_feedrate}
{endif}
; FLUSH_END
{if flush_length_1 > 45 && flush_length_2 > 1}
; WIPE
M106 P1 S0
G1 E-[new_retract_length_toolchange] F1800
_SBROS_TRASH
G1 E[new_retract_length_toolchange] F1800
{endif}
{endif}
{if flush_length > 1 && flush_length_1 == 0}
; FLUSH_START
{if flush_length > 23.7}
G1 E23.7 F{old_filament_e_feedrate} ; do not need pulsatile flushing for start part
G1 E{(flush_length - 23.7) * 0.04} F{old_filament_e_feedrate/2}
G1 E{(flush_length - 23.7) * 0.21} F{old_filament_e_feedrate}
G1 E{(flush_length - 23.7) * 0.04} F{old_filament_e_feedrate/2}
G1 E{(flush_length - 23.7) * 0.21} F{new_filament_e_feedrate}
G1 E{(flush_length - 23.7) * 0.04} F{new_filament_e_feedrate/2}
G1 E{(flush_length - 23.7) * 0.21} F{new_filament_e_feedrate}
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
G1 E{(flush_length - 23.7) * 0.04} F{new_filament_e_feedrate/2}
G1 E{(flush_length - 23.7) * 0.21} F{new_filament_e_feedrate}
{else}
G1 E{flush_length} F{old_filament_e_feedrate}
{endif}
; FLUSH_END
{if flush_length > 45 && flush_length_2 > 1}
; WIPE
M106 P1 S0
G1 E-[new_retract_length_toolchange] F1800
_SBROS_TRASH
G1 E[new_retract_length_toolchange] F1800
{endif}
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
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
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
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
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
M106 P1 S{255/100.0*fan_max_speed[next_extruder]*0.4}
G1 E{flush_length_4 * 0.04} F{new_filament_e_feedrate/2}
G1 E{flush_length_4 * 0.21} F{new_filament_e_feedrate}
; FLUSH_END
{endif}
{if flush_length > 0}
; WIPE
M106 P1 S0
G1 E-[new_retract_length_toolchange] F1800
_SBROS_TRASH
{endif}
{if toolchange_count > 1}
G1 Y220 ;Exit trash
{endif}
{endif}
{endif}

M104 S[new_filament_temp]

{if layer_z <= (initial_layer_print_height + 0.001)}
M204 S[initial_layer_acceleration]
{else}
M204 S[default_acceleration]
{endif}
```

## Pause G-code

```
PAUSE
```

##  Prusaslicer: Change filament G-code
```
; *********************************
; AD5X Change Filament G-code START

{if previous_extruder != -1}
  {if temperature[previous_extruder] < temperature[next_extruder]}
    M104 S[temperature[next_extruder]]
  {endif}
{endif}

{if wipe_tower || filament_minimal_purge_on_wipe_tower[next_extruder] <= 0}
  {if previous_extruder != -1 }
    _NOPOOP
  {endif}
  G1 Z{layer_z + 3.0} F1200
  T[next_extruder]
  G1 Z{layer_z} F1200
{else}
  {if previous_extruder != -1}
    G1 Z{layer_z + 3.0} F1200
    T[next_extruder]
    {if next_extruder < 255}
      ;jdeme do kose    
      _GOTO_TRASH
      ; FLUSH_START
      M106 P1 S{255/100.0*max_fan_speed[next_extruder]*0.4}
      ; --- flush 1 ---
      {if wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder] > 0}
          G1 E{0.237 * (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) / (3.14159265359 * (filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2))} F{0.8 * (filament_max_volumetric_speed[next_extruder]*60 / (3.14159265359*(filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2)))}
          G1 E{0.04 * (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) / (3.14159265359 * (filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2))} F{0.4 * (filament_max_volumetric_speed[next_extruder]*60 / (3.14159265359*(filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2)))}
          G1 E{0.21 * (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) / (3.14159265359 * (filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2))} F{0.8 * (filament_max_volumetric_speed[next_extruder]*60 / (3.14159265359*(filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2)))}
          G1 E{0.04 * (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) / (3.14159265359 * (filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2))} F{0.4 * (filament_max_volumetric_speed[next_extruder]*60 / (3.14159265359*(filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2)))}
          G1 E{0.21 * (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) / (3.14159265359 * (filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2))} F{1.0 * (filament_max_volumetric_speed[next_extruder]*60 / (3.14159265359*(filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2)))}
          G1 E{0.04 * (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) / (3.14159265359 * (filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2))} F{0.5 * (filament_max_volumetric_speed[next_extruder]*60 / (3.14159265359*(filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2)))}
          G1 E{0.21 * (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) / (3.14159265359 * (filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2))} F{1.2 * (filament_max_volumetric_speed[next_extruder]*60 / (3.14159265359*(filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2)))}
          G1 E-0.2 F3000
          G1 E0.2 F3000
          G1 E{0.21 * (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) / (3.14159265359 * (filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2))} F{1.4 * (filament_max_volumetric_speed[next_extruder]*60 / (3.14159265359*(filament_diameter[next_extruder]/2)*(filament_diameter[next_extruder]/2)))}
          G1 E-0.2 F3000
          G1 E0.2 F3000
      {endif}
      ; FLUSH_END
      ; --- WIPE po flush 1 ---
      {if (wiping_volumes_matrix[next_extruder] + wiping_volumes_matrix[previous_extruder]) > 0}
          M106 P1 S255 
          G4 P800      
          M106 P1 S0
          {if is_nil(filament_retract_length_toolchange[next_extruder])} 
            G1 E-[filament_retract_length[next_extruder]] F[filament_retract_speed[next_extruder]]
            _SBROS_TRASH
            G1 E[filament_retract_length[next_extruder]] F[filament_retract_speed[next_extruder]]          
          {else}
            G1 E-[filament_retract_length_toolchange[next_extruder]] F[filament_retract_speed[next_extruder]]
            _SBROS_TRASH
            G1 E[filament_retract_length_toolchange[next_extruder]] F[filament_retract_speed[next_extruder]]
          {endif}
          _CLEAR_REZINA
      {endif}            
      {if previous_extruder != -1 }
        G1 Y220
      {endif}
    {endif}
    G1 Z{layer_z} F1200
  {else}
    ;prvni extruder
    T[next_extruder]
  {endif}  
{endif}

;teplotu na aktualni extruder
M104 S[temperature[next_extruder]]

; AD5X Change Filament G-code END
; *********************************
```