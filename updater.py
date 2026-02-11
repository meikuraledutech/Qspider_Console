import os
import io
import shutil
import zipfile
import subprocess
import requests
import urllib3

from version import VERSION

urllib3.disable_warnings()

APP_DIR = os.path.dirname(os.path.abspath(__file__))

REMOTE_VERSION_URL = "https://raw.githubusercontent.com/meikuraledutech/Qspider_Console/main/version.json"
REMOTE_ZIP_URL = "https://github.com/meikuraledutech/Qspider_Console/archive/refs/heads/main.zip"

# files to never overwrite during update
PROTECTED = {"app.db", ".env"}


def _fetch_remote_version():
    """Fetch remote version.json and return (version, changelog)."""
    res = requests.get(REMOTE_VERSION_URL, verify=False, timeout=15)
    res.raise_for_status()
    data = res.json()
    return data["version"], data.get("changelog", "")


def _compare_versions(local, remote):
    """Return True if remote is newer than local."""
    def to_tuple(v):
        return tuple(int(x) for x in v.split("."))
    return to_tuple(remote) > to_tuple(local)


def _download_and_extract():
    """Download repo zip and overwrite app files."""
    res = requests.get(REMOTE_ZIP_URL, verify=False, timeout=60)
    res.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
        # zip contains a root folder like "Qspider_Console-main/"
        root = zf.namelist()[0].split("/")[0]

        for member in zf.namelist():
            # skip directories
            if member.endswith("/"):
                continue

            # get relative path after root folder
            rel_path = member[len(root) + 1:]
            if not rel_path:
                continue

            # skip protected files
            if os.path.basename(rel_path) in PROTECTED:
                continue

            # skip .venv, __pycache__, .git
            if any(part in rel_path for part in [".venv", "__pycache__", ".git"]):
                continue

            dest = os.path.join(APP_DIR, rel_path)

            # create subdirectories if needed
            dest_dir = os.path.dirname(dest)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # extract file
            with zf.open(member) as src, open(dest, "wb") as dst:
                dst.write(src.read())


def _install_deps():
    """Install dependencies from requirements.txt."""
    venv_pip = os.path.join(APP_DIR, ".venv", "bin", "pip")
    if not os.path.exists(venv_pip):
        venv_pip = os.path.join(APP_DIR, ".venv", "Scripts", "pip.exe")

    req_file = os.path.join(APP_DIR, "requirements.txt")

    if os.path.exists(venv_pip) and os.path.exists(req_file):
        subprocess.run(
            [venv_pip, "install", "-r", req_file, "-q"],
            capture_output=True, timeout=120
        )


def update_app(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 4, f"Current version: {VERSION}")
    stdscr.addstr(3, 4, "Checking for updates...")
    stdscr.refresh()

    try:
        remote_ver, changelog = _fetch_remote_version()
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(2, 4, "Failed to check for updates")
        stdscr.addstr(4, 6, str(e)[:200])
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
        return

    if not _compare_versions(VERSION, remote_ver):
        stdscr.clear()
        stdscr.addstr(2, 4, f"You're up to date! (v{VERSION})")
        stdscr.addstr(4, 4, "Press any key to return...")
        stdscr.getch()
        return

    # new version available
    stdscr.clear()
    stdscr.addstr(2, 4, f"New version available: v{remote_ver}  (current: v{VERSION})")
    if changelog:
        lines = changelog.split("\n")
        for i, line in enumerate(lines[:5]):
            stdscr.addstr(4 + i, 6, line[:70])
    stdscr.addstr(10, 4, "Downloading update...")
    stdscr.refresh()

    try:
        _download_and_extract()
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(2, 4, "Download failed")
        stdscr.addstr(4, 6, str(e)[:200])
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
        return

    stdscr.addstr(11, 4, "Installing dependencies...")
    stdscr.refresh()

    try:
        _install_deps()
    except Exception:
        pass  # non-critical, app may still work

    stdscr.clear()
    stdscr.addstr(2, 4, f"Updated to v{remote_ver}!")
    if changelog:
        stdscr.addstr(4, 4, "What's new:")
        lines = changelog.split("\n")
        for i, line in enumerate(lines[:5]):
            stdscr.addstr(5 + i, 6, line[:70])
    stdscr.addstr(11, 4, "Restart the app for changes to take effect.")
    stdscr.addstr(13, 4, "Press any key to return...")
    stdscr.getch()
