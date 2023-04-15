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

if __name__ == "__main__": main()