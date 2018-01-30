from __future__ import print_function, division
import app.gui.app as MyApp
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    myapp = QApplication([])
    window = MyApp.MyWindow()
    myapp.exec_()
