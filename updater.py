import os
import subprocess
import sys

REPO_URL = "https://github.com/meikuraledutech/Qspider_Console.git"
APP_DIR = os.path.dirname(os.path.abspath(__file__))


def update_app(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 4, "Checking for updates...", 0)
    stdscr.refresh()

    is_git = os.path.isdir(os.path.join(APP_DIR, ".git"))

    try:
        if is_git:
            # Already a git repo — pull latest
            result = subprocess.run(
                ["git", "pull", "--rebase"],
                cwd=APP_DIR,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout.strip()
            err = result.stderr.strip()

            if result.returncode != 0:
                stdscr.clear()
                stdscr.addstr(2, 4, "Update failed")
                stdscr.addstr(4, 6, err[:200] if err else "Unknown git error")
                stdscr.addstr(6, 4, "Press any key to return...")
                stdscr.getch()
                return

            if "Already up to date" in output:
                stdscr.clear()
                stdscr.addstr(2, 4, "Already up to date!")
                stdscr.addstr(4, 4, "Press any key to return...")
                stdscr.getch()
                return

        else:
            # Not a git repo — clone into temp then copy over
            stdscr.addstr(4, 4, "Downloading latest version...")
            stdscr.refresh()

            # Init git and pull
            subprocess.run(["git", "init"], cwd=APP_DIR, capture_output=True, timeout=10)
            subprocess.run(
                ["git", "remote", "add", "origin", REPO_URL],
                cwd=APP_DIR, capture_output=True, timeout=10
            )
            result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=APP_DIR, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                stdscr.clear()
                stdscr.addstr(2, 4, "Download failed")
                stdscr.addstr(4, 6, result.stderr[:200])
                stdscr.addstr(6, 4, "Press any key to return...")
                stdscr.getch()
                return

            subprocess.run(
                ["git", "reset", "--hard", "origin/main"],
                cwd=APP_DIR, capture_output=True, timeout=10
            )
            output = "Downloaded latest version"

        # Install/update dependencies
        stdscr.clear()
        stdscr.addstr(2, 4, "Updating dependencies...")
        stdscr.refresh()

        venv_pip = os.path.join(APP_DIR, ".venv", "bin", "pip")
        if not os.path.exists(venv_pip):
            venv_pip = os.path.join(APP_DIR, ".venv", "Scripts", "pip.exe")

        req_file = os.path.join(APP_DIR, "requirements.txt")

        if os.path.exists(venv_pip) and os.path.exists(req_file):
            subprocess.run(
                [venv_pip, "install", "-r", req_file, "-q"],
                capture_output=True, timeout=60
            )

        # Done
        stdscr.clear()
        stdscr.addstr(2, 4, "Update complete!", 0)
        stdscr.addstr(4, 6, output[:80])
        stdscr.addstr(6, 4, "Restart the app for changes to take effect.")
        stdscr.addstr(8, 4, "Press any key to return...")
        stdscr.getch()

    except FileNotFoundError:
        stdscr.clear()
        stdscr.addstr(2, 4, "git is not installed")
        stdscr.addstr(4, 6, "Install git:")
        stdscr.addstr(5, 8, "Mac  : brew install git")
        stdscr.addstr(6, 8, "Linux: sudo apt install git")
        stdscr.addstr(7, 8, "Win  : https://git-scm.com/downloads")
        stdscr.addstr(9, 4, "Press any key to return...")
        stdscr.getch()

    except subprocess.TimeoutExpired:
        stdscr.clear()
        stdscr.addstr(2, 4, "Update timed out. Check your internet.")
        stdscr.addstr(4, 4, "Press any key to return...")
        stdscr.getch()

    except Exception as e:
        stdscr.clear()
        stdscr.addstr(2, 4, "Update error")
        stdscr.addstr(4, 6, str(e)[:200])
        stdscr.addstr(6, 4, "Press any key to return...")
        stdscr.getch()
