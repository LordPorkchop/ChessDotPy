# File to store data used to debug the program
import os
from time import perf_counter


class frmt:
    WRN = '\033[93m[WRN]'           # Yellow (Warning)
    ERR = '\033[91m[ERR]'           # Red (Error)
    EXC = '\033[91m\033[1m[EXC]'    # Red, bold (Exception)
    DBG = '\033[94m[DBG]'           # Blue (Debug)
    RST = '\033[0m'                 # Reset to default color (Reset)
    STD = '\033[0m'                 # Standard color (Standard)
    SUC = '\033[92m'                # Green (Success)
    FAL = '\033[91m'                # Red (Failure)
    LOG = '\033[0m[LOG]'            # Standard color (Log)


timer = None


def get_timestamp() -> str:
    global timer
    if timer is None:
        timer = perf_counter()
        return "00:00:00"

    elapsed = perf_counter() - timer
    mins = elapsed // 60
    secs = int(elapsed) - mins * 60
    millis = int(((elapsed - mins * 60) - secs) * 100)
    stamp = f"{mins}:{secs}:{millis}"
    return stamp


def warn(msg: str) -> None:
    print(f"[{get_timestamp()}][{frmt.WRN}[WRN]: {msg}{frmt.RST}")


def error(msg: str) -> None:
    print(f"[{get_timestamp()}][{frmt.ERR}[ERR]: {msg}{frmt.RST}")


def exception(msg: str) -> None:
    print(f"[{get_timestamp()}][{frmt.EXC}[EXC]: {msg}{frmt.RST}")


def debug(msg: str) -> None:
    print(f"[{get_timestamp()}]{frmt.DBG}[DBG]: {msg}{frmt.RST}")


def log(msg: str) -> None:
    print(f"[{get_timestamp()}]{frmt.LOG}[LOG]: {msg}{frmt.RST}")
