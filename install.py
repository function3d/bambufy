import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys
import re

ROOT_DIR = Path("/usr/data/.mod/.zmod/root")
MAINSAIL_DIR = ROOT_DIR / "mainsail"
BACKUP_DIR = ROOT_DIR / "mainsail_"
THEME_DIR = Path("/usr/data/config/.theme")
MOD_DATA_DIR = Path("/usr/data/config/mod_data")
repo_path = "/usr/data/config/mod"
upstream_url = "https://github.com/function3d/zmod_ff5x.git"

def download_file(url, dest):
    print(f"Downloading {url} to {dest}")
    subprocess.run(["curl", "-s", "-L", "-k", "-o", dest, url], check=True)
    print(f"Download completed: {dest}")

def unzip_file(zip_path, dest_dir):
    print(f"Extracting {zip_path} to {dest_dir}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)
    os.remove(zip_path)
    print(f"Extraction completed: {dest_dir}")

def edit_config_json(config_path):
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        return
    content = config_path.read_text(encoding="utf-8")
    new_content = content.replace('"port": null,', '"port": "7125",')
    config_path.write_text(new_content, encoding="utf-8")
    print(f"Updated config: {config_path}")

def create_custom_css():
    THEME_DIR.mkdir(parents=True, exist_ok=True)
    css_content = """.v-dialog__content .v-btn{
  min-width: 32px !important;
  padding: 0 4px !important;
  margin:0 2px !important;
}
"""
    (THEME_DIR / "custom.css").write_text(css_content, encoding="utf-8")
    print(f"Created custom CSS: {THEME_DIR / 'custom.css'}")

def install_mainsail():
    if not BACKUP_DIR.exists():
        print("Starting Mainsail installation...")
        MAINSAIL_DIR.rename(BACKUP_DIR)
        print(f"Existing Mainsail backed up to {BACKUP_DIR}")

        zip_path = ROOT_DIR / "mainsail.zip"
        url = "https://github.com/function3d/mainsail/releases/download/v2.13.2-sms/mainsail.zip"
        download_file(url, zip_path)
        unzip_file(zip_path, MAINSAIL_DIR)
        edit_config_json(MAINSAIL_DIR / "config.json")
        create_custom_css()
        print("Installation completed")
        print("Press Crtl+F5 to reload Mainsail")
    else:
        print("Install: Ok")

def uninstall_mainsail():
    if BACKUP_DIR.exists():
        print("Starting Mainsail uninstallation...")
        shutil.rmtree(MAINSAIL_DIR)
        BACKUP_DIR.rename(MAINSAIL_DIR)
        print(f"Mainsail restored from backup: {BACKUP_DIR} -> {MAINSAIL_DIR}")

        css_path = THEME_DIR / "custom.css"
        if css_path.exists():
            css_path.unlink()
            print(f"Removed custom CSS: {css_path}")

        print("Uninstallation completed.")

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "install"
    if action == "install":
        install_mainsail()
    elif action == "uninstall":
        uninstall_mainsail()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()

