#!/bin/sh
set -e

source /opt/config/mod/.shell/0.sh

if [[ -d "${MOD}/root/mainsail_" ]]; then
  echo "Starting Mainsail uninstallation..."
  rm -rf "${MOD}/root/mainsail"
  mv "${MOD}/root/mainsail_" "${MOD}/root/mainsail"
  echo "Mainsail restored from backup."
  if [[ -f "$MOD_CONF/.theme/custom.css" ]]; then
    rm -rf "$MOD_CONF/.theme"
    echo "Removed custom CSS."
  fi

  echo "Uninstallation completed."
fi
