import os
import sys

from PyQt6.QtWidgets import QApplication
from widgets.mainwindow import MainWindow

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
os.environ["SPV_SD_"] = SCRIPT_DIR

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Parquet Viewer")
    with open(os.path.join(SCRIPT_DIR, "res", "stylesheet", "dark.css"), "r") as f: app.setStyleSheet(f.read())

    mw = MainWindow()
    mw.show()
    
    sys.exit(app.exec())

if __name__ == "__main__": main()