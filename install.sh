#!/bin/sh

ROOT_DIR="/usr/data/.mod/.zmod/root"
MAINSAIL_DIR="$ROOT_DIR/mainsail"
BACKUP_DIR="$ROOT_DIR/mainsail_"
THEME_DIR="/usr/data/config/.theme"

download_file() {
  local url="$1"
  local dest="$2"
  echo "Downloading $url to $dest"
  curl -s -L -k -o "$dest" "$url"
  echo "Download completed: $dest"
}

unzip_file() {
  local zip_path="$1"
  local dest_dir="$2"
  echo "Extracting $zip_path to $dest_dir"
  unzip -q "$zip_path" -d "$dest_dir"
  rm -f "$zip_path"
  echo "Extraction completed: $dest_dir"
}

edit_config_json() {
  local config_path="$1"
  if [[ ! -f "$config_path" ]]; then
    echo "Config file not found: $config_path"
    return
  fi
  sed -i 's/"port": null,/"port": "7125",/' "$config_path"
  echo "Updated config: $config_path"
}

create_custom_css() {
  mkdir -p "$THEME_DIR"
  cat > "$THEME_DIR/custom.css" <<'EOF'
.v-dialog__content .v-btn{
  min-width: 32px !important;
  padding: 0 4px !important;
  margin:0 2px !important;
}
EOF
  echo "Created custom CSS: $THEME_DIR/custom.css"
}


if [[ ! -d "$BACKUP_DIR" ]]; then
  echo "Starting Mainsail installation..."
  mv "$MAINSAIL_DIR" "$BACKUP_DIR"
  echo "Existing Mainsail backed up to $BACKUP_DIR"

  ZIP_PATH="$ROOT_DIR/mainsail.zip"
  URL="https://github.com/function3d/mainsail/releases/download/v2.13.2-sms/mainsail.zip"
  download_file "$URL" "$ZIP_PATH"
  unzip_file "$ZIP_PATH" "$MAINSAIL_DIR"
  edit_config_json "$MAINSAIL_DIR/config.json"
  create_custom_css
  echo "Installation completed"
  echo "Press Ctrl+F5 to reload Mainsail"
fi

