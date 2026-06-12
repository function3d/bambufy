# Bambufy Zmod plugin for AD5X
   - Compatible with Bambu Studio and Orca slicer.
   - Purge sequences fully controlled by the slicer.
   - Accurate time and material usage estimates.
   - 24 mm retraction before filament cut (saves ~7 meters of filament across 300 color changes).
   - Reduced purge multiplier (~0.7 Bambu Studio, 1.0 Orca slicer).
   - `Flush into object infill` `flush into object supports` and `flush into object`
   effectively reduce filament waste.
   - **Material-to-waste ratio rarely exceeds 50%, even on 4-color prints** (0.2mm layer height, weight print > 70g).
   - **Mainsail/fluidd displays true colors directly from the slicer**.
   - **45 seconds color change time**.
   - Automatic fallback when IFS runs out: the remaining filament in the
   printhead is used until the next color change
   - Filament state detection at print_start to identify the active
   filament in the extruder
   - Detection of jams, breaks and filament runout
   - Improved routine for automatic print recovery after power outages or
   errors

## Mainsail/Fluidd Dialog
<img width="398" height="375" alt="image" src="https://github.com/user-attachments/assets/11e08a4e-b11b-421b-a2ec-32e09e0db8c9" />
<img height="514" alt="image" src="https://github.com/user-attachments/assets/223d3e88-01b5-4ebe-8d47-b995c702f5ce" />

#### REMAP (MAP)
Automatically matches slicer colors to the closest physical AMS spool colors when this dialog open. Use this button to re-trigger this automatic color-matching process at any time.

#### LEVEL
When enabled, automatically performs a bed mesh leveling scan focused only on the actual print area right before printing begins.

#### IFS
When enabled, the AMS is used for printing. When disabled, keeping the filament loaded in the hotend between consecutive prints.

#### BACKUP
When enabled, matching filaments act as backups. If one runs out, the system automatically switches to the first available backup (1 to 4). You can refill used backups while printing or paused.

#### INFO
When enabled, displays on-screen event details, providing either problem descriptions when issues occur or status information during active processes.


_**Tip**: Hide the console panel in the dashboard to speed up dialog loading (Mainsail)_


## Color Mapping Dialog
<img width="428" height="312" alt="image" src="https://github.com/user-attachments/assets/976a3563-1a86-454e-88d7-7d9f99689064" />

## Physical Spool Type/Color Selection Dialog
<img width="436" height="312" alt="image" src="https://github.com/user-attachments/assets/689235ba-02ee-43b5-a8fa-c4ed840c1369" />

## How to install

- Install [zmod](https://github.com/ghzserg/zmod) following the [instructions](https://github.com/ghzserg/zmod/wiki/Setup_en#installing-the-mod)
- Change the native display to **Guppyscreen** running the `DISPLAY_OFF` command
- (Optional) Change web ui to **Mainsail** running the `WEB` command
- Run `ENABLE_EXTRA_PLUGINS` command to enable the external plugin repository.
- Run `ENABLE_PLUGIN name=bambufy` command.
- Use this [3MF](https://github.com/function3d/bambufy/releases/download/v1.1.0/ArticulatedCuteTurtle_Multicolor4Color_BambuStudio.3mf) for Bambu Studio
- Use this [3MF](https://github.com/function3d/bambufy/releases/download/v1.1.0/ArticulatedCuteTurtle_Multicolor4Color_Orca.3mf) for Orca slicer.

## How to uninstall
- Run the `DISABLE_PLUGIN name=bambufy` command.
- (Optional) Go back to stock screen, run the `DISPLAY_ON` command.
- (Optional) Go back to Fluidd, run the `WEB` command.

## Multicolor printing nopoop
[Orca Slicer](https://github.com/function3d/bambufy/blob/master/MACHINE_GCODE.md#orca-slicer)

## Pull requests and issues are welcome!

## Results
<img width="412" alt="image" src="https://github.com/user-attachments/assets/f6812bbf-ffd2-45d0-85fb-2e95d7d04b9b" />
<img width="342" alt="image" src="https://github.com/user-attachments/assets/8ad8ce59-6f45-44ef-88ec-be9ecdcfb7f0" />

## Credits
Sergei (ghzserg) [zmod](https://github.com/ghzserg/zmod)
