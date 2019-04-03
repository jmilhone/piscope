from __future__ import print_function, division
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import argparse
import source.gui.piscope as MyApp
#import logging
from source.logging.piscope_logging import create_logger, log
import os.path as path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a PiScope for the Big Red Ball.")
    parser.add_argument("--config", "-c", type=str, default=None, help="Config File to Load.")
    parser.add_argument("--shot_number", "-s", type=int, default=None, help="Shot Number to Open at Start Up")
    parser.add_argument("--logging", "-L", type=str, default=None,
                        help="Log file name for debug logging")
    args = parser.parse_args()


    if args.logging:
        logger = create_logger(name='pi-scope-logger', filename=args.logging, useNull=False)
    else:
        logger = create_logger(name='pi-scope-logger', useNull=True)

        # handler = logging.FileHandler(filename=args.logging, mode='w')
        # logger.setLevel(logging.DEBUG)

        # # create formatter
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

        # # add formatter to ch
        # handler.setFormatter(formatter)

    # else:
    #     handler = logging.NullHandler()

    # logger.addHandler(handler)
    logger.debug("*****************************************")
    logger.debug("Starting up")

    myapp = QApplication([])
    myapp.setWindowIcon(QIcon("Icons/application-wave.png"))
    print(args.config, type(args.config))
    import os
    print(os.path.dirname(os.path.realpath(__file__)))
    window = MyApp.PiScope(args.config, args.shot_number)
    myapp.exec_()
