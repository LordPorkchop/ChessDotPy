import os
from debug import *
from subprocess import run, DEVNULL

log("Running setup.py")
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'


def get_version():
    with open(os.path.join(root, "version.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    raise RuntimeError("Unable to find version string.")


# Read dependencies from requirements.txt
def parse_requirements():
    with open("requirements.txt") as f:
        reqs = []
        content = f.read()
        content = content.splitlines()
        for line in content:
            reqs.append(line.split("#")[0].strip())  # Remove comments
        return reqs


root = os.path.abspath(os.path.dirname(__file__)).capitalize()

version = get_version()
log(f"ChessDotPy version {version}")

log(f"Root directory: {root}")

log("Reading requirements")
requirements = parse_requirements()
reqs = len(requirements)
log(f"{reqs} requirements found")

to_install = []
for req in requirements:
    try:
        exec(f"import {req}")
        log(f"({requirements.index(req) + 1}/{reqs}) {req}: {frmt.SUC}installed{frmt.RST}")
    except ModuleNotFoundError:
        log(f"({requirements.index(req) + 1}/{reqs}) {req}: {frmt.FAIL}not installed{frmt.RST}")
        to_install.append(req)
if len(to_install) == 0:
    log(frmt.SUC + "All requirements installed" + frmt.RST)
else:
    installed = []
    warn(f"{len(to_install)}/10 requirements not installed")
    for req in to_install:
        log(f"Installing {req}...")
        try:
            run(f"pip install {req}", shell=True,
                stdout=DEVNULL, stderr=DEVNULL)
            log(f"{frmt.SUC}{req} installed successfully", frmt.RST)
            installed.append(req)
        except Exception as e:
            error(
                f"Failed to install {req}: {e}. Please install {req} manually: {frmt.MAG}pip install {req}{frmt.RST}")
            break
if installed == to_install:
    log(frmt.SUC + "All requirements installed" + frmt.RST)
