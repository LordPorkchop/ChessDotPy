import os
import platform
import requests as r
from debug import *
from subprocess import run, DEVNULL


log("Running setup.py")
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

root = os.path.abspath(os.path.dirname(__file__))
log(f"Root directory: {root}")


def get_version():
    with open(os.path.join(root, "version.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    raise RuntimeError("Unable to find version string in root/version.py")


def get_latest_version() -> str:
    try:
        response = r.get(
            "https://raw.githubusercontent.com/LordPorkchop/ChessDotPy/refs/heads/main/version.py")
        if response.status_code == 200:
            for line in response.text.splitlines():
                if line.startswith("__version__"):
                    return line.split("=")[1].split("#")[0].strip().strip('"')
        else:
            error(
                f"Failed to fetch latest version. Status code: {response.status_code}")
    except Exception as e:
        error(f"Error fetching latest version: {e}")


# Read dependencies from requirements.txt
def parse_requirements():
    with open("requirements.txt") as f:
        reqs = []
        content = f.read()
        content = content.splitlines()
        for line in content:
            reqs.append(line.split("#")[0].strip())  # Remove comments
        return reqs


req_aliases = {
    "pillow": "PIL",
    "pywin32": "win32com",
}


latest = get_latest_version()
version = get_version()
if latest:
    if latest == version:
        log(f"ChessDotPy version {version} (latest)")
    else:
        log(f"ChessDotPy version {version}")
        warn(
            f"New version available: {latest}. Please update to the latest version.")
else:
    log(f"ChessDotPy version {version}")


osversion = platform.version()
if os.name != 'nt' or int(osversion.split('.')[0]) < 10:
    exception("ChessDotPy requires Windows 10 or newer.")
    exit(1)

log("Reading requirements")
requirements = parse_requirements()
reqs = len(requirements)
log(f"{reqs} requirements found")

to_install = []
for req in requirements:
    try:
        if req in req_aliases.keys():
            exec(f"import {req_aliases[req]}")
        else:
            exec(f"import {req}")
        log(f"({requirements.index(req) + 1}/{reqs}) {req}: {frmt.SUC}installed{frmt.RST}")
    except ModuleNotFoundError:
        log(f"({requirements.index(req) + 1}/{reqs}) {req}: {frmt.FAIL}not installed{frmt.RST}")
        to_install.append(req)

if len(to_install) == 0:
    log("All requirements installed")
else:
    installed = []
    warn(f"{len(to_install)} requirement(s) not installed")
    for req in to_install:
        log(f"Installing {req}...")
        try:
            run(f"pip install {req}", shell=True,
                stdout=DEVNULL, stderr=DEVNULL, check=True)
            log(f"{frmt.SUC}{req} installed successfully", frmt.RST)
            installed.append(req)
        except Exception as e:
            error(
                f"Failed to install {req}: {e}. Please install {req} manually: {frmt.MAG}pip install {req}{frmt.RST}")
            break
    if installed == to_install:
        log(frmt.SUC + "All requirements installed" + frmt.RST)
    else:
        for i in installed:
            to_install.remove(i)
        error(
            f"Failed to install {len(to_install) - len(installed)} requirement(s)")
        error("Please install the missing requirements manually")
        error(f"Missing requirements: {', '.join(to_install)}")
        exit(1)

if os.path.exists(os.path.join(root, "saves")):
    log("Scanning root/saves for played games...")
    games = []
    others = []
    for file in os.listdir(os.path.join(root, "saves")):
        if file.endswith(".pgn"):
            games.append(os.path.join(root, "saves", file))
        else:
            others.append(os.path.join(root, "saves", file))
    log(f"{len(games)} game(s) found")
    if len(others) > 0:
        warn(f"[{len(others)}] non-PGN files found in {os.path.join(root, "saves")}.")
        log("Removing non-PGN files in root/saves...")
        for file in others:
            os.remove(file)
            log(f"Removed {file}")
else:
    warn("root/saves does not exist. This indicates a corrupt installation. Please consider reinstalling ChessDotPy from GitHub")
    log("Creating root/saves")
    os.mkdir(os.path.join(root, "saves"))

if not os.path.exists(os.path.join(root, "engine", "stockfish-windows-x86-64-avx2.exe")):
    exception(
        f"Stockfish is not installed correctly. Please install it from {frmt.MAG}https://stockfishchess.org/download{frmt.RST} or consider reinstalling ChessDotPy from the official GitHub repository: {frmt.MAG}https://github.com/LordPorkchop/chessdotpy {frmt.RST}")
    exit(1)

if not os.path.exists(os.path.join(root, "assets")):
    exception(
        f"Asset directory (root/assets) does not exist. This indicates a corrupt installation. Please reinstall ChessDotPy from the official GitHub repository: {frmt.MAG}https://github.com/LordPorkchop/chessdotpy {frmt.RST}")
    exit(1)

if not os.path.exists(os.path.join(root, "LICENSE.md")):
    exception(
        f"The license file does not exist, likely indicating a non-official installation. Please install ChessDotPy for free from the official GitHub repository: {frmt.MAG}https://github.com/LordPorkchop/chessdotpy {frmt.RST}")
    exit(1)

if not os.path.exists(os.path.join(root, "CITATION.cff")):
    exception(
        f"The citation file does not exist, likely indicating a non-official installation. Please install ChessDotPy for free from the official GitHub repository: {frmt.MAG}https://github.com/LordPorkchop/chessdotpy {frmt.RST}")
    exit(1)

log(frmt.SUC + "ChessDotPy Setup complete" + frmt.RST)
print()
log("You can now run ChessDotPy by double-clicking main.py")
log(
    f"If you want to create a desktop icon, please run {frmt.MAG}desktop.pyw{frmt.RST}")
input("\nPress Enter to close...")
