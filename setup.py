import importlib
import json
import debug
import os
import platform
import requests
import stockfish
import sys
from CTkMessagebox import CTkMessagebox
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


def get_latest_version() -> str | None:
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/LordPorkchop/ChessDotPy/refs/heads/main/version.py",
            timeout=20)
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
            req = line.split("#")[0].strip()  # Remove comments
            if req:  # Skip empty lines
                reqs.append(req)
        return reqs


req_aliases = {
    "pillow": "PIL",
    "pywin32": "win32com",
}


def __is_greater(v1, v2):
    v1_parts = list(map(int, v1.split(".")))
    v2_parts = list(map(int, v2.split(".")))
    return v1_parts > v2_parts


def __is_lower(v1, v2):
    v1_parts = list(map(int, v1.split(".")))
    v2_parts = list(map(int, v2.split(".")))
    return v1_parts < v2_parts


latest = get_latest_version()
version = get_version()
if latest:
    if latest == version:
        debug.log(f"ChessDotPy version {version} (latest)")
    else:
        debug.log(f"ChessDotPy version {version}")
        if __is_greater(latest, version):
            debug.warn(
                f"New version available: {latest}. Please update to the latest version.")
        elif __is_lower(latest, version):
            debug.warn(
                f"Your version {version} is newer than the officially latest version {latest}, indicating a potentially unstable development version.")
        else:
            debug.error(
                "Your version does not match the Chess.py version naming scheme")
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
            importlib.import_module(req_aliases[req])
        else:
            importlib.import_module(req)
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

            run([sys.executable, "-m", "pip", "install", req, "--quiet"],
                stdout=DEVNULL, stderr=DEVNULL, check=True)
            debug.log(
                f"{debug.frmt.SUC}{req} installed successfully", debug.frmt.RST)
            installed.append(req)
        except Exception as e:
            debug.error(
                f"Failed to install {req}: {e}. Please install {req} manually: {debug.frmt.MAG}pip install {req}{debug.frmt.RST}")
            continue
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
    CTkMessagebox(
        title="Chess.py Setup Error",
        message="Failed to setup chess.py: Stockfish is not installed correctly. Please install it from https://stockfishchess.org/download or consider reinstalling Chess.py from the official GitHub repository: https://github.com/LordPorkchop/chessdotpy",
        icon="cancel",
        option_1="OK"
    )
    exit(1)

if not os.path.exists(os.path.join(root, "assets")):
    debug.exception(
        f"Asset directory (root/assets) does not exist. This indicates a corrupt installation. Please reinstall ChessDotPy from the official GitHub repository: {debug.frmt.MAG}https://github.com/LordPorkchop/chessdotpy {debug.frmt.RST}")
    CTkMessagebox(
        title="Chess.py Setup Error",
        message="Failed to setup chess.py: Asset directory is missing. Please reinstall Chess.py from the official GitHub repository: https://github.com/LordPorkchop/chessdotpy",
        icon="cancel",
        option_1="OK"
    )
    exit(1)

if not os.path.exists(os.path.join(root, "LICENSE.md")):
    debug.exception(
        f"The license file does not exist, likely indicating a non-official installation. Please install ChessDotPy for free from the official GitHub repository: {debug.frmt.MAG}https://github.com/LordPorkchop/chessdotpy {debug.frmt.RST}")
    exit(1)

if not os.path.exists(os.path.join(root, "CITATIONS.md")):
    debug.exception(
        f"The citations file does not exist, likely indicating a non-official installation. Please install ChessDotPy for free from the official GitHub repository: {debug.frmt.MAG}https://github.com/LordPorkchop/chessdotpy {debug.frmt.RST}")
    exit(1)

try:
    stockfish.Stockfish(os.path.join(
        root, "engine", "stockfish-windows-x86-64-avx2.exe"), depth=20)
    debug.log("Stockfish initialized successfully")
except Exception as e:
    debug.exception(f"Failed to initialize Stockfish: {e}")
    CTkMessagebox(
        title="Chess.py Setup Error",
        message=f"Failed to setup chess.py: Failed to initialize Chess Engine at {os.path.join(root, 'engine')} ({e})",
        icon="cancel",
        option_1="OK"
    )
    exit(1)

createShortcut = CTkMessagebox(
    title="Create desktop shortcut?",
    message="Do you want to create a shortcut on your desktop?",
    icon="question",
    option_1="Yes",
    option_2="No",
    option_focus=1
).get() == "Yes"
if createShortcut:
    debug.log("Creating shortcut on desktop...")
    try:
        run([sys.executable, "-m", "python",
            os.path.join(os.getcwd(), "desktop.pyw")], check=True)
    except Exception as e:
        debug.error(f"Failed to create shortcut: {e}")
        CTkMessagebox(
            title="ChessDotPy Setup Error",
            message=f"Failed to create shortcut: {e}",
            icon="cancel",
            option_1="OK"
        )
else:
    debug.log("Skipping shortcut creation after user prompt")


CTkMessagebox(
    title="ChessDotPy Setup Complete",
    message="ChessDotPy setup is complete. Run the program to start playing chess.",
    icon="check",
    option_1="OK"
)
debug.log("Cleaning up:")
debug.log("Removing files...")
root_path = os.getcwd()
to_remove = [
    "requirements.txt",
    ".gitignore",
    ".gitattributes",
    "desktop.pyw"
]
for file in to_remove:
    path = os.path.join(root_path, file)
    try:
        os.remove(os.path.join(root_path, file))
    except Exception as e:
        debug.error(f"Error while removing {file}: {e}")
    else:
        debug.log(f"Successfully removed {file}")
debug.finish()
