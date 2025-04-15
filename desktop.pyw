import os
from win32com.client import Dispatch


def create_shortcut():
    # Define paths
    target = os.path.abspath('./main.py')
    icon = os.path.abspath('./assets/icon.ico')
    shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop")

    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.IconLocation = icon
    shortcut.Save()


if __name__ == "__main__":
    create_shortcut()
