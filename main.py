from __future__ import print_function, division
from PyQt5.QtWidgets import QApplication
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a PiScope for the Big Red Ball.")
    parser.add_argument("--config", "-c", type=str, default=None, help="Config File to Load.")
    parser.add_argument("--shot_number", "-s", type=int, default=None, help="Shot Number to Open at Start Up")
    #group = parser.add_mutually_exclusive_group()
    #group.add_argument("-d", "--discharge", action="store_true")
    #group.add_argument("-g", "--gun", action="store_true")
    #group.add_argument("-m", "--mach", action="store_true")
    #group.add_argument("-b", "--magnetics", action="store_true")
    #parser.add_argument("--hall", nargs='?', default=3, type=int, help="Hall probe array number, default is 3")
    args = parser.parse_args()

    #if args.mach:
    #    print("Running mach")
    #    import app.gui.mach_app as MyApp
    #elif args.gun:
    #    print("Running guns")
    #    import app.gui.gun_app as MyApp
    #elif args.magnetics:
    #    print("Running magnetics")
    #    import app.gui.magnetics_app as MyApp
    #else:
    #    print("Running discharge")
    import app.gui.discharge_app as MyApp

    import app.gui.app as MyApp

    myapp = QApplication([])
    window = MyApp.MyWindow(args.config, args.shot_number)
    #if args.magnetics:
    #    window = MyApp.MyWindow(args.hall)
    #else:
    #    window=MyApp.MyWindow()
    myapp.exec_()
