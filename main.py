from __future__ import print_function, division
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import argparse
import app.gui.app as MyApp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a PiScope for the Big Red Ball.")
    parser.add_argument("--config", "-c", type=str, default=None, help="Config File to Load.")
    parser.add_argument("--shot_number", "-s", type=int, default=None, help="Shot Number to Open at Start Up")
    args = parser.parse_args()

    myapp = QApplication([])
    myapp.setWindowIcon(QIcon("Icons/application-wave.png"))
    window = MyApp.MyWindow(args.config, args.shot_number)
    myapp.exec_()
