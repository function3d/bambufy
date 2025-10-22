#!/bin/sh
set -e

ROOT_DIR="/usr/data/.mod/.zmod/root"
MAINSAIL_DIR="$ROOT_DIR/mainsail"
BACKUP_DIR="$ROOT_DIR/mainsail_"
THEME_DIR="/usr/data/config/.theme"

if [[ -d "$BACKUP_DIR" ]]; then
  echo "Starting Mainsail uninstallation..."
  rm -rf "$MAINSAIL_DIR"
  mv "$BACKUP_DIR" "$MAINSAIL_DIR"
  echo "Mainsail restored from backup: $BACKUP_DIR -> $MAINSAIL_DIR"

  CSS_PATH="$THEME_DIR/custom.css"
  if [[ -f "$CSS_PATH" ]]; then
    rm -f "$CSS_PATH"
    echo "Removed custom CSS: $CSS_PATH"
  fi

  echo "Uninstallation completed."
else
  echo "No backup found. Nothing to uninstall."
fi
}
