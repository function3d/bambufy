# Bambufy AD5X
 - Compatible with Bambu Studio, better management of the prime tower
   ([3MF](https://github.com/function3d/zmod_ff5x/raw/refs/heads/1.6/PinkyWings_FireDragon.3mf))
  - Purge sequences fully controlled by Bambu Studio (same behavior as
   Bambu Lab printers)
   - Accurate time and material usage estimates
   - 24 mm retraction before filament cut on every color change (saves ~7
   meters of filament across 300 color changes)
   - Reduced purge multiplier (≈ 0.7) possible without color mixing in
   most prints
   - `Flush into object infill` `flush into object supports` and `flush into object`
   effectively reduce filament waste
   - **Material-to-waste ratio rarely exceeds 50%, even on 4-color prints** (weight print > 70g)
   - **Mainsail displays true colors directly from the slicer**
   - **45 seconds color change time**
   - Bed leveling before print (Level On/Off)
   - External spool printing (IFS On/Off)
   - Backup printing mode – up to 4 kg of uninterrupted printing (Backup
   On/Off)
  - Automatic fallback when IFS runs out: the remaining filament in the
   printhead is used until the next color change
   - Filament state detection at print_start to identify the active
   filament in the extruder
   - Detection of jams, breaks and filament runout
   - Improved routine for automatic print recovery after power outages or
   errors

## Bambu Studio
<img width="1436" height="799" alt="image" src="https://github.com/user-attachments/assets/1d6a9e77-8b35-4d04-96d4-d92022a3500b" />

## Flush volumes
<img width="1307" height="810" alt="image" src="https://github.com/user-attachments/assets/fea280f2-809d-4bae-a744-4a4c36465881" />

## Mainsail
<img width="1059" height="810" alt="image" src="https://github.com/user-attachments/assets/bf80b66f-46e2-4b48-af52-d6f44f5accc8" />

## How to install

- Install [zmod](https://github.com/ghzserg/zmod) following the [instructions](https://github.com/ghzserg/zmod/wiki/Setup_en#installing-the-mod)

- Change the native display to Guppyscreen → Run the `DISPLAY_OFF` command

- Change web ui to **Mainsail** → Run the `WEB` command

- Open **Mainsail** and navigate to **Machine → mod_data → user.moonraker.conf**.
- At the **end of the file**, add the following section and save:
```
[update_manager bambufy]
type: git_repo
channel: stable
path: /root/printer_data/config/mod_data/bambufy/
origin: https://github.com/function3d/bambufy.git
is_system_service: False
primary_branch: master
```
- Open **Machine → mod_data → user.cfg**
- At the **beginning of the file**, add the following section and **SAVE & RESTART**:
```
[include bambufy/user.cfg]
```
- Use this [3MF](https://github.com/function3d/zmod_ff5x/raw/refs/heads/1.6/bambufy/PinkyWings_FireDragon.3mf) with Bambu Studio (from there you can save settings such as user profiles)

## How to uninstall
- Run the `BAMBUFY INSTALL=0` command

## Pull request yours issues
Let's do what Flashforge didn't want to do

## Results
<img width="1005" height="1113" alt="image" src="https://github.com/user-attachments/assets/f6812bbf-ffd2-45d0-85fb-2e95d7d04b9b" />
<img width="1200" height="1600" alt="image" src="https://github.com/user-attachments/assets/8ad8ce59-6f45-44ef-88ec-be9ecdcfb7f0" />

## Credits
Sergei (ghzserg) [zmod](https://github.com/ghzserg/zmod)



