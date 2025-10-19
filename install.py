#!/usr/bin/env python3
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys
import re

ROOT_DIR = Path("/root")
MAINSAIL_DIR = ROOT_DIR / "mainsail"
BACKUP_DIR = ROOT_DIR / "mainsail_"
THEME_DIR = Path("cd /usr/data/config/.theme")
MOD_DATA_DIR = Path("/usr/data/config/mod_data")
repo_path = "/usr/data/config/mod"                                                                                                                                                        
upstream_url = "https://github.com/function3d/zmod_ff5x.git"

def download_file(url, dest):
    subprocess.run(["curl", "-s", "-L", "-o", dest, url], check=True)

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
    THEME_DIR.mkdir(parents=True, exist_ok=True)
    css_content = """.v-dialog__content .v-btn{
  min-width: 32px !important;
  padding: 0 4px !important;
  margin:0 2px !important;
}
"""
    (THEME_DIR / "custom.css").write_text(css_content, encoding="utf-8")

def install_mainsail():
    if not BACKUP_DIR.exists():
        MAINSAIL_DIR.rename(BACKUP_DIR)
        zip_path = ROOT_DIR / "mainsail.zip"
        url = "https://github.com/function3d/mainsail/releases/download/v2.13.2-sms/mainsail.zip"
        download_file(url, zip_path)
        unzip_file(zip_path, MAINSAIL_DIR)
        config_json = MAINSAIL_DIR / "config.json"
        edit_config_json(config_json)
        create_custom_css()
        #(MOD_DATA_DIR / "web.conf").write_text("CLIENT=mainsail\n", encoding="utf-8")
    (MOD_DATA_DIR / "user.cfg").write_text("[include bambufy/user.cfg]", encoding="utf-8")
    ensure_upstream()                                                                                                                                                                         
    sync_with_upstream(get_default_branch("origin"))

def run_git(args):
    """Ejecuta comandos git en el repositorio."""
    subprocess.run(["git", "-C", str(repo_path)] + args, check=True)

def ensure_upstream():
    """Añade el remoto upstream si no existe."""
    try:
        subprocess.run(
            ["git", "-C", str(repo_path), "remote", "get-url", "upstream"],
            check=True,
            capture_output=True,
        )
        print("✅ Remoto 'upstream' ya existe.")
    except subprocess.CalledProcessError:
        print("➕ Añadiendo remoto 'upstream'...")
        run_git(["remote", "add", "upstream", upstream_url])

def sync_with_upstream(branch="1.6"):
    """Actualiza y sincroniza la rama local con upstream/branch."""
    print(f"📥 Sincronizando con upstream/{branch}...")
    run_git(["fetch", "upstream"])

    # Elimina la rama local si existe para clonar el remoto con precisión
    subprocess.run(
        ["git", "-C", str(repo_path), "branch", "-D", branch],
        stderr=subprocess.DEVNULL,
    )

    # Crea una nueva rama local idéntica a upstream/1.6
    run_git(["checkout", "-B", branch, f"upstream/{branch}"])
    print(f"✅ Rama local '{branch}' ahora refleja upstream/{branch}")

def revert_to_origin(branch="master"):
    """Vuelve al repositorio original (origin/branch)."""
    print(f"↩️ Revirtiendo a origin/{branch}...")
    run_git(["fetch", "origin"])
    run_git(["checkout", branch])
    run_git(["reset", "--hard", f"origin/{branch}"])
    print(f"✅ Repositorio restaurado a origin/{branch}")

def get_default_branch(remote="origin"):
    """Devuelve la rama principal configurada en el remoto (HEAD branch)."""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "remote", "show", remote],
        capture_output=True,
        text=True,
        check=True,
    )
    match = re.search(r"HEAD branch:\s+(\S+)", result.stdout)
    return match.group(1) if match else None

def revert_to_origin():
    """Revierten los cambios al estado de la rama principal de origin."""
    run_git(["fetch", "origin"])

    default_branch = get_default_branch("origin")
    if not default_branch:
        raise RuntimeError("❌ No se pudo determinar la rama principal del remoto.")

    print(f"↩️ Revirtiendo a origin/{default_branch}...")
    run_git(["checkout", "-B", default_branch, f"origin/{default_branch}"])
    run_git(["reset", "--hard", f"origin/{default_branch}"])
    print(f"✅ Repositorio restaurado a origin/{default_branch}")

def uninstall_mainsail():
    if BACKUP_DIR.exists():
        shutil.rmtree(MAINSAIL_DIR)
        BACKUP_DIR.rename(MAINSAIL_DIR)
        css_path = THEME_DIR / "custom.css"
        if css_path.exists():
            css_path.unlink()
        (MOD_DATA_DIR / "web.conf").write_text("CLIENT=fluidd\n", encoding="utf-8")
    (MOD_DATA_DIR / "user.cfg").write_text("", encoding="utf-8")
    revert_to_origin()

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "install"
    if action == "install":
        install_mainsail()
    elif action == "uninstall":
        uninstall_mainsail()

if __name__ == "__main__":
    main()
