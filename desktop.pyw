import os
import sys

if sys.platform == "win32":
    from win32com.client import Dispatch
elif sys.platform == "linux":
    import stat
elif sys.platform == "darwin":
    import stat
    import plistlib
    import subprocess

# Define paths
target_path = os.path.join(os.getcwd(), "main.pyw")
icon_path = os.path.join(os.getcwd(), "assets", "icon.ico")
python_path = os.path.realpath(sys.executable)


def create_shortcut_windows():
    shortcut_path = os.path.join(
        os.path.expanduser("~"), "Desktop", "Chess.py.lnk")

    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.WorkingDirectory = os.path.dirname(target_path)
    shortcut.IconLocation = icon_path
    shortcut.WindowStyle = 7  # 7 = Minimized window
    shortcut.Save()


def create_shortcut_linux():
    desktop_entry = [
        "[Desktop Entry]",
        "Version=1.0",
        "Type=Application",
        "Name=chess.py",
        "Comment=Chess in python!",
        f"Exec={python_path} {target_path}",
        "Terminal=false",
        f"Icon={icon_path}"
    ]
    desktop_content = "\n".join(desktop_entry) + "\n"
    applications_dir = os.path.expanduser("~/.local/share/applications")
    desktop_dir = os.path.expanduser("~/Desktop")
    os.makedirs(applications_dir, exist_ok=True)
    os.makedirs(desktop_dir, exist_ok=True)

    app_shortcut_path = os.path.join(applications_dir, "chess.desktop")
    desktop_shortcut_path = os.path.join(desktop_dir, "chess.desktop")

    def write_shortcut(path):
        with open(path, "w") as f:
            f.write(desktop_content)
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)  # type: ignore

    write_shortcut(app_shortcut_path)
    write_shortcut(desktop_shortcut_path)


def create_shortcut_mac():
    icon_path = os.path.join(os.getcwd(), "assets", "icon.icns")

    app_dir = "chess.py.app"
    contents_dir = os.path.join(app_dir, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    resources_dir = os.path.join(contents_dir, "Resources")
    os.makedirs(macos_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)

    plist = {
        "CFBundleName": "chess.py",
        "CFBundleDisplayName": "chess.py",
        "CFBundleExecutable": "runscript",
        "CFBundlePackageType": "APPL",
        "CFBundleVersion": "1.0",
        "CFBundleIconFile": os.path.basename(icon_path)
    }
    with open(os.path.join(contents_dir, "Info.plist"), "wb") as f:
        plistlib.dump(plist, f)  # type: ignore

    subprocess.run(["cp", icon_path, os.path.join(  # type: ignore
        resources_dir, os.path.basename(icon_path))])

    run_script_path = os.path.join(macos_dir, "runscript")
    script_content = f"#!/bin/bash\n'{python_path}' '{target_path}'\n"

    with open(run_script_path, "w") as f:
        f.write(script_content)

    st = os.stat(run_script_path)
    os.chmod(run_script_path, st.st_mode | stat.S_IEXEC)  # type: ignore


if __name__ == "__main__":
    match sys.platform:
        case "win32":
            create_shortcut_windows()
        case "linux":
            create_shortcut_linux()
        case "darwin":
            create_shortcut_mac()
