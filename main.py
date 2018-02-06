from __future__ import print_function, division
from PyQt5.QtWidgets import QApplication
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a PiScope for the Big Red Ball.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--discharge", action="store_true")
    group.add_argument("-m", "--mach", action="store_true")
    args = parser.parse_args()

    if args.mach:
        print("Running mach")
        import app.gui.mach_app as MyApp
    else:
        print("Running discharge")
        import app.gui.discharge_app as MyApp

    myapp = QApplication([])
    window = MyApp.MyWindow()
    myapp.exec_()
