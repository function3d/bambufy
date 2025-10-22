#!/bin/sh
set -e

source /opt/config/mod/.shell/0.sh

if [[ ! -d "${MOD}/root/mainsail_" ]]; then
  echo "Starting Mainsail installation..."
  mv "${MOD}/root/mainsail" "${MOD}/root/mainsail_"
  echo "Existing Mainsail backed up to ${MOD}/root/mainsail_"
  chroot ${MOD} curl -s -L -k -o "/root/mainsail.zip" "https://github.com/function3d/mainsail/releases/download/v2.13.2-sms/mainsail.zip"
  mkdir -p "${MOD}/root/mainsail"
  unzip -q "${MOD}/root/mainsail.zip" -d "${MOD}/root/mainsail"
  rm -f "${MOD}/root/mainsail.zip"
  sed -i 's/"port": null,/"port": "7125",/' "${MOD}/root/mainsail/config.json"
  mkdir -p ${MOD_CONF}/.theme
  cat > "${MOD_CONF}/.theme/custom.css" <<'EOF'
.v-dialog__content .v-btn{
  min-width: 32px !important;
  padding: 0 4px !important;
  margin:0 2px !important;
}
EOF
  echo "Installation completed. Press Ctrl + F5 to reload Mainsail"
fi

