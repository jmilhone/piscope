from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui


class NewConfigDialog(QtWidgets.QDialog):

    def __init__(self, xloc=None, yloc=None):
        super(NewConfigDialog, self).__init__()
        # Defaults
        self.nrows = 2
        self.ncols = 2
        self.server = '192.168.113.62'
        self.event = 'raw_data_ready'

        self.row_label = QtWidgets.QLabel(self)
        self.row_input = QtWidgets.QSpinBox(self)
        self.col_label = QtWidgets.QLabel(self)
        self.col_input = QtWidgets.QSpinBox(self)
        self.server_label = QtWidgets.QLabel(self)
        self.server_input = QtWidgets.QLineEdit(self)
        self.event_label = QtWidgets.QLabel(self)
        self.event_input = QtWidgets.QLineEdit(self)

        self.row_input.setRange(0, 9)
        self.col_input.setRange(0, 9)

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                                  QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.hbox_row_col = QtWidgets.QHBoxLayout()
        self.hbox_server = QtWidgets.QHBoxLayout()
        self.hbox_event = QtWidgets.QHBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()
        self.init_UI(xloc=xloc, yloc=yloc)

        self.row_input.valueChanged.connect(self.update_row)
        self.col_input.valueChanged.connect(self.update_col)
        self.server_input.editingFinished.connect(self.update_server)
        self.event_input.editingFinished.connect(self.update_event)

    def init_UI(self, xloc=None, yloc=None):
        if xloc is None:
            xloc = 200
        if yloc is None:
            yloc = 200
        self.setGeometry(xloc, yloc, 500, 100)
        self.setWindowTitle('New Configuration')

        self.row_label.setText("Number of Rows: ")
        self.col_label.setText("Number of Columns: ")
        self.server_label.setText("Server Address: ")
        self.event_label.setText("MDSplus Event Name: ")

        self.row_input.setValue(self.nrows)
        self.col_input.setValue(self.ncols)
        self.server_input.setText(self.server)
        self.event_input.setText(self.event)

        self.hbox_row_col.addWidget(self.row_label)
        self.hbox_row_col.addWidget(self.row_input)
        self.hbox_row_col.addWidget(self.col_label)
        self.hbox_row_col.addWidget(self.col_input)
        self.hbox_row_col.addStretch()

        self.hbox_server.addWidget(self.server_label)
        self.hbox_server.addWidget(self.server_input)

        self.hbox_event.addWidget(self.event_label)
        self.hbox_event.addWidget(self.event_input)

        self.vbox.addLayout(self.hbox_row_col)
        self.vbox.addLayout(self.hbox_server)
        self.vbox.addLayout(self.hbox_event)
        self.vbox.addWidget(self.buttons)
        self.setLayout(self.vbox)

    def update_row(self, row):
        self.nrows = row

    def update_col(self, col):
        self.ncols = col

    def update_server(self):
        self.server = self.server_input.text()

    def update_event(self):
        self.event = self.event_input.text()



