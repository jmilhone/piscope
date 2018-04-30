from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui


class NewConfigDialog(QtWidgets.QDialog):

    def __init__(self, xloc=None, yloc=None):
        super(NewConfigDialog, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Icons/application-wave.png"))
        # Defaults
        self.nrow = 2
        self.ncol = 2
        self.server = '192.168.113.62'
        self.event = 'raw_data_ready'
        self.tree = 'wipal'

        self.column_setup = [0 for _ in range(6)]
        self.column_setup[0] = 1

        # self.row_label = QtWidgets.QLabel(self)
        # self.row_input = QtWidgets.QSpinBox(self)
        # self.col_label = QtWidgets.QLabel(self)
        # self.col_input = QtWidgets.QSpinBox(self)
        self.server_label = QtWidgets.QLabel(self)
        self.server_input = QtWidgets.QLineEdit(self)
        self.event_label = QtWidgets.QLabel(self)
        self.event_input = QtWidgets.QLineEdit(self)
        self.tree_label = QtWidgets.QLabel(self)
        self.tree_input = QtWidgets.QLineEdit(self)
        self.column_label = QtWidgets.QLabel(self)

        self.sliders = []
        for i in range(6):
            self.sliders.append(CustomSlider(i, 1.0))


        # self.row_input.setRange(2, 9)
        # self.col_input.setRange(2, 9)

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                                  QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # self.hbox_row_col = QtWidgets.QHBoxLayout()
        self.hbox_server = QtWidgets.QHBoxLayout()
        self.hbox_event = QtWidgets.QHBoxLayout()
        self.hbox_tree = QtWidgets.QHBoxLayout()
        self.hbox_slider = QtWidgets.QHBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()
        self.init_UI(xloc=xloc, yloc=yloc)

        # self.row_input.valueChanged.connect(self.update_row)
        # self.col_input.valueChanged.connect(self.update_col)
        self.server_input.editingFinished.connect(self.update_server)
        self.event_input.editingFinished.connect(self.update_event)
        self.tree_input.editingFinished.connect(self.update_tree)
        for slider in self.sliders:
            slider.valueChanged.connect(self.update_column_config)

    def init_UI(self, xloc=None, yloc=None):
        if xloc is None:
            xloc = 200
        if yloc is None:
            yloc = 200
        self.setGeometry(xloc, yloc, 500, 350)
        self.setWindowTitle('New Configuration')

        # self.row_label.setText("Number of Rows: ")
        # self.col_label.setText("Number of Columns: ")
        self.server_label.setText("Server Address: ")
        self.event_label.setText("MDSplus Event Name: ")
        self.tree_label.setText("MDSplus Tree Name: ")

        # self.row_input.setValue(self.nrow)
        # self.col_input.setValue(self.ncol)
        self.server_input.setText(self.server)
        self.event_input.setText(self.event)
        self.tree_input.setText(self.tree)

        # self.hbox_row_col.addWidget(self.row_label)
        # self.hbox_row_col.addWidget(self.row_input)
        # self.hbox_row_col.addWidget(self.col_label)
        # self.hbox_row_col.addWidget(self.col_input)
        # self.hbox_row_col.addStretch()

        self.hbox_server.addWidget(self.server_label)
        self.hbox_server.addWidget(self.server_input)

        self.hbox_event.addWidget(self.event_label)
        self.hbox_event.addWidget(self.event_input)

        self.hbox_tree.addWidget(self.tree_label)
        self.hbox_tree.addWidget(self.tree_input)

        for sli in self.sliders:
            self.hbox_slider.addWidget(sli)
            sli.slider.setMinimum(0)
            sli.slider.setMaximum(6)
            sli.slider.setTickInterval(1)
            sli.slider.setTickPosition(QtWidgets.QSlider.TicksLeft)
        self.sliders[0].slider.setMinimum(1)
        self.column_label.setText("Select the number of rows for each column.")
        # self.vbox.addLayout(self.hbox_row_col)
        self.vbox.addLayout(self.hbox_server)
        self.vbox.addLayout(self.hbox_tree)
        self.vbox.addLayout(self.hbox_event)
        self.vbox.addWidget(self.column_label)
        self.vbox.addLayout(self.hbox_slider)
        self.vbox.addWidget(self.buttons)
        self.setLayout(self.vbox)

    # def update_row(self, row):
    #     self.nrow = row

    # def update_col(self, col):
    #     self.ncol = col

    def update_server(self):
        self.server = self.server_input.text()

    def update_event(self):
        self.event = self.event_input.text()

    def update_tree(self):
        self.tree = self.tree_input.text()

    def update_column_config(self, value):
        sender = self.sender()
        self.column_setup[sender.index] = value


class CustomSlider(QtWidgets.QWidget):

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, index, value, *args, **kwargs):
        super(CustomSlider, self).__init__(*args, **kwargs)
        self.index = index
        self.value = value
        self.slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.label = QtWidgets.QLabel()
        # self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.slider.setValue(1)
        self.label.setText(str(self.slider.value()))
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.slider, 5)
        self.vbox.addWidget(self.label, 1)
        self.setLayout(self.vbox)

        self.slider.valueChanged.connect(self.update_value)

    def update_value(self, value):
        self.value = value
        self.label.setText(str(value))
        self.valueChanged.emit(self.value)


