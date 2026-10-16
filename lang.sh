#!/bin/sh
# Bambufy override for Z-Mod's "zlang" command.
#
# Z-Mod only rewrites a plugin's [include] line in plugins.cfg when the plugin
# is (re)enabled, so Bambufy used to force a full ENABLE_PLUGIN (git pull +
# install.sh + a second restart) on every language change. Here we re-point
# just Bambufy's include before the reboot Z-Mod already performs, so a
# language change costs a single restart.
#
# Delivered by the plugin repo (git pull) and executed as root by Z-Mod.

MOD_CONF=/opt/config
DIR=$MOD_CONF/mod_data/plugins/bambufy
PLUGINS=$MOD_CONF/mod_data/plugins.cfg
ZMOD_ZLANG=/usr/data/zmod/zmod/.shell/zlang.sh

[ -x "$ZMOD_ZLANG" ] || exit 0

lang="$1"
[ -f "$DIR/$lang/bambufy.cfg" ] || lang=en

# Re-point an existing include only: never enable a disabled Bambufy.
if [ -f "$PLUGINS" ] && grep -q "^\[include plugins/bambufy/" "$PLUGINS" \
   && ! grep -q "^\[include plugins/bambufy/$lang/bambufy.cfg\]$" "$PLUGINS"; then
    sed -i "/^\[include plugins\/bambufy\//d" "$PLUGINS"
    echo "[include plugins/bambufy/$lang/bambufy.cfg]" >>"$PLUGINS"
    sync
fi

# Z-Mod writes lang.cfg and triggers the reboot.
exec "$ZMOD_ZLANG" "$1"
