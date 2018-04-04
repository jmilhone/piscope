from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui
from distutils.util import strtobool
from copy import deepcopy

class PanelConfig(QtWidgets.QDialog):

    def __init__(self, config):
        super(PanelConfig, self).__init__()
        self.config = deepcopy(config)

        grid = config.keys()
        grid = [x for x in grid if x != 'setup']
        grid.sort()
        self.grid = grid

        self.combo = QtWidgets.QComboBox(self)
        for pos in grid:
            self.combo.addItem(pos)
        self.combo_label = QtWidgets.QLabel(self)

        self.item_list = QtWidgets.QListWidget(self)

        self.x_qlabel = QtWidgets.QLabel(self)
        self.y_qlabel = QtWidgets.QLabel(self)
        self.x_input = QtWidgets.QLineEdit(self)
        self.y_input = QtWidgets.QLineEdit(self)

        self.xlabel = QtWidgets.QLineEdit(self)
        self.ylabel = QtWidgets.QLineEdit(self)
        self.label = QtWidgets.QLineEdit(self)
        self.legend = QtWidgets.QCheckBox(self)
        self.xlab = QtWidgets.QLabel(self)
        self.ylab = QtWidgets.QLabel(self)
        self.lab = QtWidgets.QLabel(self)

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Apply |
                                                  QtWidgets.QDialogButtonBox.Ok |
                                                  QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.handle_apply_event)

        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.xhbox = QtWidgets.QHBoxLayout()
        self.yhbox = QtWidgets.QHBoxLayout()
        self.options_box = QtWidgets.QHBoxLayout()
        self.lab_box = QtWidgets.QHBoxLayout()
        self.init_UI()

        self.combo.activated.connect(self.change_list_view)
        self.item_list.currentRowChanged.connect(self.populate_signal_fields)
        self.hello = 100
    def print_hello(self):
        print("hello")

    def init_UI(self):
        self.populate_list_box(self.grid[0])
        self.populate_options(0)
        self.x_qlabel.setText("X: ")
        self.y_qlabel.setText("Y: ")

        self.legend.setText("Legend")
        self.xlab.setText("X Label: ")
        self.ylab.setText("Y Label: ")
        self.lab.setText("Signal Name")
        self.combo_label.setText("Plot: ")
        self.setGeometry(200, 200, 500, 200)
        self.setWindowTitle('Edit Configuration')

        self.hbox.addWidget(self.combo_label)
        self.hbox.addWidget(self.combo)

        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.item_list)

        self.xhbox.addWidget(self.x_qlabel)
        self.xhbox.addWidget(self.x_input)

        self.options_box.addWidget(self.xlab)
        self.options_box.addWidget(self.xlabel)
        self.options_box.addWidget(self.ylab)
        self.options_box.addWidget(self.ylabel)
        self.options_box.addWidget(self.legend)

        self.lab_box.addWidget(self.lab)
        self.lab_box.addWidget(self.label)

        self.yhbox.addWidget(self.y_qlabel)
        self.yhbox.addWidget(self.y_input)

        self.vbox.addLayout(self.options_box)
        self.vbox.addLayout(self.lab_box)
        self.vbox.addLayout(self.xhbox)
        self.vbox.addLayout(self.yhbox)
        self.vbox.addWidget(self.buttons)
        self.setLayout(self.vbox)

    def change_list_view(self, idx):
        text = self.grid[idx]
        self.item_list.clear()
        self.populate_list_box(text)
        self.populate_options(idx)

    def populate_options(self, idx):
        pos = self.grid[idx]
        local_config = self.config[pos]
        keys = local_config.keys()
        if "xlabel" in keys:
            self.xlabel.setText(local_config['xlabel'])
        else:
            self.xlabel.clear()

        if "ylabel" in keys:
            self.ylabel.setText(local_config['ylabel'])
        else:
            self.ylabel.clear()

        if "legend" in keys and strtobool(local_config['legend']):
            self.legend.setChecked(True)
        else:
            self.legend.setChecked(False)

    def populate_list_box(self, key):
        ignore_items = ['xlabel', 'ylabel', 'legend']
        pos_items = [x for x in self.config[key] if x not in ignore_items]
        pos_items.sort()

        self.item_list.addItem("New Signal")
        for item in pos_items:
            self.item_list.addItem(item)
        self.item_list.setCurrentRow(0)

    def populate_signal_fields(self, idx):
        if idx != 0:
            pos = self.combo.currentText()
            item = self.item_list.currentItem()
            if item is None:  # Seems to trigger this function when switching grid positions, need to figure that out
                return
            label = item.text()

            local_config = self.config[pos][label]
            keys = local_config.keys()
            if 'x' in keys:
                self.x_input.setText(local_config['x'])

            if 'y' in keys:
                self.y_input.setText(local_config['y'])

            self.label.setText(label)
        else:
            self.x_input.clear()
            self.y_input.clear()
            self.label.clear()

    def handle_apply_event(self):
        idx = self.item_list.currentRow()
        xtext = self.x_input.text()
        ytext = self.y_input.text()
        label = self.label.text()

        #if not (ytext and label):
        #    self.error_dialog = QtWidgets.QErrorMessage()
        #    self.error_dialog.setWindowModality(QtCore.Qt.WindowModal)
        #    self.error_dialog.showMessage('You did not fill in the necessary fields (y and label)!')
        #    return

        pos = self.combo.currentText()
        item = self.item_list.currentItem()

        if ytext and xtext and label:
            self.config[pos][label] = {}
            self.config[pos][label]['x'] = xtext
            self.config[pos][label]['y'] = ytext
        else:
            if idx != 0:
                print("I should delete")
                current_label = item.text()
                print(current_label)
                del self.config[pos][current_label]

        xlabel = self.xlabel.text()
        ylabel = self.ylabel.text()
        legend = str(self.legend.isChecked())

        self.config[pos]['legend'] = legend
        self.config[pos]['xlabel'] = xlabel
        self.config[pos]['ylabel'] = ylabel
        self.item_list.clear()
        self.populate_list_box(pos)



















