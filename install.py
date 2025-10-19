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
    print("Starting Mainsail installation...")
    if not BACKUP_DIR.exists():
        MAINSAIL_DIR.rename(BACKUP_DIR)
        print(f"Existing Mainsail backed up to {BACKUP_DIR}")

    zip_path = ROOT_DIR / "mainsail.zip"
    url = "https://github.com/function3d/mainsail/releases/download/v2.13.2-sms/mainsail.zip"
    download_file(url, zip_path)
    unzip_file(zip_path, MAINSAIL_DIR)
    edit_config_json(MAINSAIL_DIR / "config.json")
    create_custom_css()

    (MOD_DATA_DIR / "user.cfg").write_text("[include bambufy/user.cfg]", encoding="utf-8")
    print(f"Updated user configuration: {MOD_DATA_DIR / 'user.cfg'}")

    ensure_upstream()
    sync_with_upstream(get_default_branch("origin"))
    
    print("Installation completed. Printer will reboot.")
    with open("/tmp/printer", "a", encoding='utf-8') as f:
        f.write('REBOOT\n')

def run_git(args):
    """Execute git commands inside chroot and return CompletedProcess."""
    return subprocess.run(
        ["chroot", "/usr/data/.mod/.zmod/", "git", "-C", str(repo_path)] + args,
        check=True,
        capture_output=True,
        text=True
    )

def ensure_upstream():
    """Add the upstream remote if it does not exist."""
    try:
        run_git(["remote", "get-url", "upstream"])
        print("Remote 'upstream' already exists.")
    except subprocess.CalledProcessError:
        print("Adding remote 'upstream'...")
        run_git(["remote", "add", "upstream", upstream_url])
        print("Remote 'upstream' added.")

def sync_with_upstream(branch="1.6"):
    """Update and synchronize local branch with upstream/branch."""
    print(f"Synchronizing with upstream/{branch}...")
    run_git(["fetch", "upstream"])

    try:
        run_git(["branch", "-D", branch])
        print(f"Deleted existing local branch: {branch}")
    except subprocess.CalledProcessError:
        print(f"Local branch {branch} does not exist, skipping delete")

    run_git(["checkout", "-B", branch, f"upstream/{branch}"])
    print(f"Local branch {branch} now matches upstream/{branch}")

def revert_to_origin():
    """Revert changes to origin's main branch."""
    run_git(["fetch", "origin"])
    default_branch = get_default_branch("origin")
    if not default_branch:
        raise RuntimeError("Failed to determine the default branch of origin.")

    print(f"Reverting to origin/{default_branch}...")
    run_git(["checkout", "-B", default_branch, f"origin/{default_branch}"])
    run_git(["reset", "--hard", f"origin/{default_branch}"])
    print(f"Repository restored to origin/{default_branch}")

def get_default_branch(remote="origin"):
    """Return the default branch configured on the remote."""
    result = run_git(["remote", "show", remote])
    match = re.search(r"HEAD branch:\s+(\S+)", result.stdout)
    return match.group(1) if match else None

def uninstall_mainsail():
    print("Starting Mainsail uninstallation...")
    if BACKUP_DIR.exists():
        shutil.rmtree(MAINSAIL_DIR)
        BACKUP_DIR.rename(MAINSAIL_DIR)
        print(f"Mainsail restored from backup: {BACKUP_DIR} -> {MAINSAIL_DIR}")

        css_path = THEME_DIR / "custom.css"
        if css_path.exists():
            css_path.unlink()
            print(f"Removed custom CSS: {css_path}")

        (MOD_DATA_DIR / "user.cfg").write_text("", encoding="utf-8")
        print(f"Cleared user configuration: {MOD_DATA_DIR / 'user.cfg'}")

        revert_to_origin()
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

