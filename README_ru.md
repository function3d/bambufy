# Bambufy AD5X
 - Совместим с Bambu Studio, улучшенное управление башней подачи  
   ([3MF](https://github.com/function3d/bambufy/releases/download/v1.0.0/PinkyWing_FireDragon.3mf))
 - Последовательности продувки полностью управляются Bambu Studio (такое же поведение, как у принтеров Bambu Lab)
 - Точные оценки времени печати и расхода материала
 - Ретракт 24 мм перед обрезкой нити при каждой смене цвета (экономия ~7 метров нити на 300 сменах цвета)
 - Возможность снижения множителя продувки (≈ 0.7) без смешивания цветов в большинстве печатей
 - `Flush into object infill`, `flush into object supports` и `flush into object` эффективно снижают расход нити
 - **Соотношение материала к отходам редко превышает 50 % даже при 4-цветной печати** (высота слоя 0.2 мм, масса модели > 70 г)
 - **Mainsail отображает истинные цвета непосредственно из слайсера**
 - **Время смены цвета — 45 секунд**
 - Автоматическая калибровка стола перед печатью (Level On/Off)
 - Печать с внешней катушки (IFS On/Off)
 - Режим резервной печати — до 4 кг непрерывной печати (Backup On/Off)
 - Автоматический переход при опустошении внешней катушки: оставшаяся нить в экструдере используется до следующей смены цвета
 - Определение состояния нити при запуске печати для идентификации активной нити в экструдере
 - Обнаружение засоров, обрывов и окончания нити
 - Улучшенная процедура автоматического восстановления печати после отключений питания или ошибок

## Bambu Studio
<img width="812" width="1436" height="799" alt="image" src="https://github.com/user-attachments/assets/1d6a9e77-8b35-4d04-96d4-d92022a3500b" />

## Объёмы продувки (Flush volumes)
<img width="812" width="1307" height="810" alt="image" src="https://github.com/user-attachments/assets/fea280f2-809d-4bae-a744-4a4c36465881" />

## Mainsail
<img width="812" width="1059" height="810" alt="image" src="https://github.com/user-attachments/assets/bf80b66f-46e2-4b48-af52-d6f44f5accc8" />

## Установка

- Установите [zmod](https://github.com/ghzserg/zmod) согласно [инструкции](https://github.com/ghzserg/zmod/wiki/Setup_en#installing-the-mod)
- Переключите родной дисплей на **Guppyscreen**, выполнив команду `DISPLAY_OFF`
- Переключите веб-интерфейс на **Mainsail**, выполнив команду `WEB`
- Выполните в консоли команду `ENABLE_PLUGIN name=bambufy`
- Используйте этот [3MF](https://github.com/function3d/bambufy/releases/download/v1.0.0/PinkyWing_FireDragon.3mf) в Bambu Studio (оттуда можно сохранять настройки, такие как пользовательские профили)

## Удаление
- Выполните в консоли команду `DISABLE_PLUGIN name=bambufy`
- (Опционально) Верните родной экран командой `DISPLAY_ON`
- (Опционально) Верните Fluidd командой `WEB`

## Сообщайте об ошибках и предлагайте улучшения
Сделаем то, что Flashforge не захотел делать

## Результаты
<img width="812" alt="image" src="https://github.com/user-attachments/assets/f6812bbf-ffd2-45d0-85fb-2e95d7d04b9b" />
<img width="812" alt="image" src="https://github.com/user-attachments/assets/8ad8ce59-6f45-44ef-88ec-be9ecdcfb7f0" />

## Благодарности
Сергей (ghzserg) — [zmod](https://github.com/ghzserg/zmod)
