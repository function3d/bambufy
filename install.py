#!/usr/bin/env python3
import os
import shutil
import subprocess
import zipfile
import requests
from pathlib import Path
import sys

CHROOT_PATH = "/usr/data/.mod/.zmod/"
ROOT_DIR = Path("/root")
MAINSAIL_DIR = ROOT_DIR / "mainsail"
BACKUP_DIR = ROOT_DIR / "mainsail_"
THEME_DIR = Path("cd /usr/data/config/.theme")
MOD_DATA_DIR = Path("/usr/data/config/mod_data")

def download_file(url, dest):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            

def unzip_file(zip_path, dest_dir):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)
    os.remove(zip_path)


def edit_config_json(config_path):
    if not config_path.exists():
        return
    content = config_path.read_text(encoding="utf-8")
    new_content = content.replace('"port": null,', '"port": "7125",')
    config_path.write_text(new_content, encoding="utf-8")


def create_custom_css():
    print("Creando custom.css...")
    THEME_DIR.mkdir(parents=True, exist_ok=True)
    css_content = """.v-dialog__content .v-btn{
  min-width: 32px !important;
  padding: 0 4px !important;
  margin:0 2px !important;
}
"""
    (THEME_DIR / "custom.css").write_text(css_content, encoding="utf-8")

def update():
    repo_path = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(["git", "-C", repo_path, "fetch", "--all"], check=True)
    subprocess.run(["git", "-C", repo_path, "reset", "--hard", f"origin/{branch}"], check=True)
    #subprocess.run(["git", "-C", repo_path, "clean", "-fd"], check=True)  # elimina archivos sin seguimiento
    
def install_mainsail():
    if not BACKUP_DIR.exists():
        print("Backup de mainsail existente...")
        shutil.rmtree(BACKUP_DIR)
        MAINSAIL_DIR.rename(BACKUP_DIR)
        zip_path = ROOT_DIR / "mainsail.zip"
        url = "https://github.com/function3d/mainsail/releases/download/v2.13.2-sms/mainsail.zip"
        download_file(url, zip_path)
        unzip_file(zip_path, MAINSAIL_DIR)
        config_json = MAINSAIL_DIR / "config.json"
        edit_config_json(config_json)
        create_custom_css()
        #(MOD_DATA_DIR / "web.conf").write_text("CLIENT=mainsail\n", encoding="utf-8")
    MOD_DATA_DIR / "user.cfg".write_text("[include bambufy/user.cfg]", encoding="utf-8")

def uninstall_mainsail():
    if BACKUP_DIR.exists():
        shutil.rmtree(MAINSAIL_DIR)
        BACKUP_DIR.rename(MAINSAIL_DIR)
        css_path = THEME_DIR / "custom.css"
        if css_path.exists():
            css_path.unlink()
        (MOD_DATA_DIR / "web.conf").write_text("CLIENT=fluidd\n", encoding="utf-8")
    MOD_DATA_DIR / "user.cfg".write_text("", encoding="utf-8")

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "install"
    if action == "install":
        install_mainsail()
    elif action == "uninstall":
        uninstall_mainsail()
    elif action == "update":
        update()

if __name__ == "__main__":
    main()
