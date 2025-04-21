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
    YEL = '\033[93m'                # Yellow (Yellow)


timer = perf_counter()
ERRORS = 0
WARNINGS = 0
EXCEPTIONS = 0
DEBUGS = 0
LOGS = 0


def get_timestamp() -> str:
    global timer
    if timer is None:
        timer = perf_counter()
        return get_timestamp()

    elapsed = perf_counter() - timer
    mins = int(elapsed // 60)
    secs = int(elapsed - mins * 60)
    millis = int(((elapsed - mins * 60) - secs) * 1000)
    stamp = f"{str(mins).zfill(2)}:{str(secs).zfill(2)}.{str(millis).zfill(4)}"
    return stamp


def warn(msg: str, *args) -> None:
    global WARNINGS
    print(f"[{get_timestamp()}]{frmt.WRN}: {msg + " " + " ".join(args)}{frmt.RST}")
    WARNINGS += 1


def error(msg: str, *args) -> None:
    global ERRORS
    print(f"[{get_timestamp()}]{frmt.ERR}: {msg + " " + " ".join(args)}{frmt.RST}")
    ERRORS += 1


def exception(msg: str, *args) -> None:
    global EXCEPTIONS
    print(f"[{get_timestamp()}]{frmt.EXC}: {msg + " " + " ".join(args)}{frmt.RST}")
    EXCEPTIONS += 1


def debug(msg: str, *args) -> None:
    global DEBUGS
    print(f"[{get_timestamp()}]{frmt.DBG}: {msg + " " + " ".join(args)}{frmt.RST}")
    DEBUGS += 1


def log(msg: str, *args) -> None:
    global LOGS
    print(f"[{get_timestamp()}]{frmt.LOG}: {msg + " " + " ".join(args)}{frmt.RST}")
    LOGS += 1


def finish() -> None:
    global ERRORS, WARNINGS, EXCEPTIONS, DEBUGS, LOGS
    print(f"{frmt.SUC}FINISHED{frmt.STD} in {get_timestamp()} with\n\t{frmt.SUC if EXCEPTIONS == 0 else frmt.FAIL}{EXCEPTIONS}{frmt.STD} exceptions,\n\t{frmt.SUC if ERRORS == 0 else frmt.FAIL}{ERRORS}{frmt.STD} errors,\n\t{frmt.SUC if WARNINGS == 0 else frmt.YEL}{WARNINGS}{frmt.STD} warnings,\n\t{DEBUGS} debug messages and\n\t{LOGS} log messages.")


if __name__ == "__main__":
    # Example usage of the functions
    print("Usage example:")
    log("This is a log message.")
    debug("This is a debug message.")
    warn("This is a warning message.")
    error("This is an error message.")
    exception("This is an exception message.")

    # Finish the script and print summary
    finish()
