#!/usr/bin/env pythonw

import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTranslator, QLocale
from PyQt6.QtWidgets import QApplication

from .widgets.mainwindow import MainWindow, APP_VERSION

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
os.environ["SPV_SD_"] = SCRIPT_DIR

def main():
    if os.name == "nt":
        import ctypes
        appid = f'simple.parquet.viewer.oss.v{APP_VERSION[0]}.{APP_VERSION[2]}.{APP_VERSION[2]}'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    app = QApplication(sys.argv)
    translator = QTranslator()

    if translator.load(QLocale(), os.path.join(SCRIPT_DIR, "res", "translations") + os.path.sep):
        app.installTranslator(translator)

    app.setWindowIcon(QIcon(os.path.join(SCRIPT_DIR, "res", "imgs", "app_icon.ico")))
    app.setApplicationName("Simple Parquet Viewer")
    with open(os.path.join(SCRIPT_DIR, "res", "stylesheet", "dark.css"), "r") as f: app.setStyleSheet(f.read())

    mw = MainWindow()
    mw.show()
    
    sys.exit(app.exec())

def gen_shortcut():
    if os.name != "nt":
        print("This feature is only available for Windows.")
        sys.exit(0)

    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.expandvars("%APPDATA%"), "Microsoft", "Windows", "Start Menu", "Programs")
    if not (os.path.exists(out) and os.path.isdir(out)):
        print(f"A valid directory must be provided: \"{out}\" is not a directory.")
        sys.exit(1)
    
    try:
        from shutil import which
        from win32com.client import Dispatch
    except:
        print("There was an error while importing the necessary dependencies. Please, certify that 'pywin32' package is installed.")
        sys.exit(1)

    sc = Dispatch("WScript.Shell").CreateShortCut(os.path.join(out, "Simple Parquet Viewer.lnk"))
    sc.Targetpath = which("spv")
    sc.IconLocation = os.path.join(SCRIPT_DIR, "res", "imgs", "app_icon.ico")
    sc.save()

if __name__ == "__main__": main()