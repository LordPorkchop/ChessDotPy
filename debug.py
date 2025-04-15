# File to store data used to debug the program
from time import perf_counter


class frmt:
    WRN = '\033[93m[WRN]'           # Yellow (Warning)
    ERR = '\033[91m[ERR]'           # Red (Error)
    EXC = '\033[91m\033[1m[EXC]'    # Red, bold (Exception)
    DBG = '\033[94m[DBG]'           # Blue (Debug)
    RST = '\033[0m'                 # Reset to default color (Reset)
    STD = '\033[0m'                 # Standard color (Standard)
    SUC = '\033[92m'                # Green (Success)
    FAIL = '\033[91m'               # Red (Failure)
    LOG = '\033[0m[LOG]'            # Standard color (Log)
    MAG = '\033[35m'                # Magenta (Magenta)


timer = None


def get_timestamp() -> str:
    global timer
    if timer is None:
        timer = perf_counter()
        return "00:00.0000"

    elapsed = perf_counter() - timer
    mins = int(elapsed // 60)
    secs = int(elapsed - mins * 60)
    millis = int(((elapsed - mins * 60) - secs) * 1000)
    stamp = f"{str(mins).zfill(2)}:{str(secs).zfill(2)}.{str(millis).zfill(4)}"
    return stamp


def warn(msg: str, *args) -> None:
    print(f"[{get_timestamp()}]{frmt.WRN}: {msg + " " + " ".join(args)}{frmt.RST}")


def error(msg: str, *args) -> None:
    print(f"[{get_timestamp()}]{frmt.ERR}: {msg + " " + " ".join(args)}{frmt.RST}")


def exception(msg: str, *args) -> None:
    print(f"[{get_timestamp()}]{frmt.EXC}: {msg + " " + " ".join(args)}{frmt.RST}")


def debug(msg: str, *args) -> None:
    print(f"[{get_timestamp()}]{frmt.DBG}: {msg + " " + " ".join(args)}{frmt.RST}")


def log(msg: str, *args) -> None:
    print(f"[{get_timestamp()}]{frmt.LOG}: {msg + " " + " ".join(args)}{frmt.RST}")
