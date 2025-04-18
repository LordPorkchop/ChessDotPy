import debug
import os
import platform
import requests as r
import stockfish
from tkinter import messagebox
from subprocess import run, DEVNULL


debug.log("Running setup.py")
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

root = os.path.abspath(os.path.dirname(__file__))
debug.log(f"Root directory: {root}")


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
            debug.error(
                f"Failed to fetch latest version. Status code: {response.status_code}")
    except Exception as e:
        debug.error(f"Error fetching latest version: {e}")


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
        debug.log(f"ChessDotPy version {version} (latest)")
    else:
        debug.log(f"ChessDotPy version {version}")
        debug.warn(
            f"New version available: {latest}. Please update to the latest version.")
else:
    debug.log(f"ChessDotPy version {version}")


osversion = platform.version()
if os.name != 'nt' or int(osversion.split('.')[0]) < 10:
    debug.exception("ChessDotPy requires Windows 10 or newer.")
    exit(1)

debug.log("Reading requirements")
requirements = parse_requirements()
reqs = len(requirements)
debug.log(f"{reqs} requirements found")

to_install = []
for req in requirements:
    try:
        if req in req_aliases.keys():
            exec(f"import {req_aliases[req]}")
        else:
            exec(f"import {req}")
        debug.log(
            f"({requirements.index(req) + 1}/{reqs}) {req}: {debug.frmt.SUC}installed{debug.frmt.RST}")
    except ModuleNotFoundError:
        debug.log(
            f"({requirements.index(req) + 1}/{reqs}) {req}: {debug.frmt.FAIL}not installed{debug.frmt.RST}")
        to_install.append(req)

if len(to_install) == 0:
    debug.log("All requirements installed")
else:
    installed = []
    debug.warn(f"{len(to_install)} requirement(s) not installed")
    for req in to_install:
        debug.log(f"Installing {req}...")
        try:
            run(f"pip install {req}", shell=True,
                stdout=DEVNULL, stderr=DEVNULL, check=True)
            debug.log(
                f"{debug.frmt.SUC}{req} installed successfully", debug.frmt.RST)
            installed.append(req)
        except Exception as e:
            debug.error(
                f"Failed to install {req}: {e}. Please install {req} manually: {debug.frmt.MAG}pip install {req}{debug.frmt.RST}")
            break
    if installed == to_install:
        debug.log(debug.frmt.SUC + "All requirements installed" + debug.frmt.RST)
    else:
        for i in installed:
            to_install.remove(i)
        debug.error(
            f"Failed to install {len(to_install) - len(installed)} requirement(s)")
        debug.error("Please install the missing requirements manually")
        debug.error(f"Missing requirements: {', '.join(to_install)}")
        exit(1)

if os.path.exists(os.path.join(root, "saves")):
    debug.log("Scanning root/saves for played games...")
    games = []
    others = []
    for file in os.listdir(os.path.join(root, "saves")):
        if file.endswith(".pgn"):
            games.append(os.path.join(root, "saves", file))
        else:
            others.append(os.path.join(root, "saves", file))
    debug.log(f"{len(games)} game(s) found")
    if len(others) > 0:
        debug.warn(
            f"[{len(others)}] non-PGN files found in {os.path.join(root, "saves")}.")
        debug.log("Removing non-PGN files in root/saves...")
        for file in others:
            os.remove(file)
            debug.log(f"Removed {file}")
else:
    debug.warn("root/saves does not exist. This indicates a corrupt installation. Please consider reinstalling ChessDotPy from GitHub")
    debug.log("Creating root/saves")
    os.mkdir(os.path.join(root, "saves"))

if not os.path.exists(os.path.join(root, "engine", "stockfish-windows-x86-64-avx2.exe")):
    debug.exception(
        f"Stockfish is not installed correctly. Please install it from {debug.frmt.MAG}https://stockfishchess.org/download{debug.frmt.RST} or consider reinstalling ChessDotPy from the official GitHub repository: {debug.frmt.MAG}https://github.com/LordPorkchop/chessdotpy {debug.frmt.RST}")
    messagebox.showerror(title="ChessDotPy Setup Error",
                         message="Failed to setup chess.py: Stockfish is not installed correctly",
                         icon=messagebox.ERROR,
                         type=messagebox.OK)
    exit(1)

if not os.path.exists(os.path.join(root, "assets")):
    debug.exception(
        f"Asset directory (root/assets) does not exist. This indicates a corrupt installation. Please reinstall ChessDotPy from the official GitHub repository: {debug.frmt.MAG}https://github.com/LordPorkchop/chessdotpy {debug.frmt.RST}")
    messagebox.showerror(title="ChessDotPy Setup Error",
                         message="Failed to setup chess.py: Asset directory is missing",
                         icon=messagebox.ERROR,
                         type=messagebox.OK)
    exit(1)

if not os.path.exists(os.path.join(root, "LICENSE.md")):
    debug.exception(
        f"The license file does not exist, likely indicating a non-official installation. Please install ChessDotPy for free from the official GitHub repository: {debug.frmt.MAG}https://github.com/LordPorkchop/chessdotpy {debug.frmt.RST}")
    exit(1)

if not os.path.exists(os.path.join(root, "CITATION.cff")):
    debug.exception(
        f"The citation file does not exist, likely indicating a non-official installation. Please install ChessDotPy for free from the official GitHub repository: {debug.frmt.MAG}https://github.com/LordPorkchop/chessdotpy {debug.frmt.RST}")
    exit(1)

try:
    stockfish.Stockfish(os.path.join(
        root, "engine", "stockfish-windows-x86-64-avx2.exe"), depth=20)
    debug.log("Stockfish initialized successfully")
except Exception as e:
    debug.exception(f"Failed to initialize Stockfish: {e}")
    messagebox.showerror(title="ChessDotPy Setup Error",
                         message=f"Failed to setup chess.py: Failed to initialize Chess Engine at {os.path.join(root, "engine")} ({e})",
                         icon=messagebox.ERROR,
                         type=messagebox.OK)
    exit(1)

createShortcut = messagebox.askyesno(title="Chess.py Setup Complete",
                                     message="Chess.py setup is complete. Do you want to create a shortcut on your desktop?",
                                     icon=messagebox.INFO,
                                     type=messagebox.YESNO)
if createShortcut:
    debug.log("Creating shortcut on desktop...")
    try:
        run("python desktop.pyw", check=True)
    except Exception as e:
        debug.error(f"Failed to create shortcut: {e}")
        messagebox.showerror(title="ChessDotPy Setup Error",
                             message=f"Failed to create shortcut: {e}",
                             icon=messagebox.ERROR,
                             type=messagebox.OK)

debug.log(debug.frmt.SUC + "ChessDotPy Setup complete" + debug.frmt.RST)
messagebox.showinfo(title="ChessDotPy Setup Complete",
                    message="ChessDotPy setup is complete. Please run the program to start playing chess.",
                    icon=messagebox.INFO,
                    type=messagebox.OK)
