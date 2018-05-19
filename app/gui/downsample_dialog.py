from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui


class EditDownsampleDialog(QtWidgets.QDialog):
    """

    """

    def __init__(self, points, xloc=None, yloc=None):
        """

        Args:
            points:
            xloc:
            yloc:
        """
        super(EditDownsampleDialog, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Icons/application-wave.png"))
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                                  QtWidgets.QDialogButtonBox.Cancel)
        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()

        self.points_input = QtWidgets.QSpinBox(self)
        self.points_label = QtWidgets.QLabel(self)
        self.points = points

        self.init_UI(xloc=xloc, yloc=yloc)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.points_input.valueChanged.connect(self.points_change)

    def init_UI(self, xloc=None, yloc=None):
        """

        Args:
            xloc:
            yloc:

        Returns:

        """
        if xloc is None:
            xloc = 200

        if yloc is None:
            yloc = 200

        self.setWindowTitle("Change Downsampling")

        self.points_label.setText("Number of Points: ")
        self.points_input.setRange(1, 1000000)
        self.points_input.setValue(self.points)

        self.hbox.addWidget(self.points_label)
        self.hbox.addWidget(self.points_input)

        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.buttons)
        self.setLayout(self.vbox)

        self.setGeometry(xloc, yloc, 300, 100)

    def points_change(self, value):
        """

        Args:
            value:

        Returns:

        """
        self.points = value

