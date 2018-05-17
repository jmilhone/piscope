from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui
from distutils.util import strtobool
from copy import deepcopy
from .scientificspin import ScientificDoubleSpinBox

default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']

class EditConfigDialog(QtWidgets.QDialog):

    def __init__(self, config, xloc=None, yloc=None):
        super(EditConfigDialog, self).__init__()
        self.config = deepcopy(config)
        self.setWindowIcon(QtGui.QIcon("Icons/application-wave.png"))

        grid = config.keys()
        grid = [x for x in grid if x != 'setup']
        self.grid = grid
        self.grid_labels = ["Column {1}, Row {0}".format(x[0], x[1]) for x in self.grid]
        self.grid_labels, self.grid = zip(*sorted(zip(self.grid_labels, self.grid)))
        self.combo = QtWidgets.QComboBox(self)
        for pos in self.grid_labels:
            self.combo.addItem(pos)
        self.combo_label = QtWidgets.QLabel(self)

        self.item_list = QtWidgets.QListWidget(self)

        self.x_qlabel = QtWidgets.QLabel(self)
        self.y_qlabel = QtWidgets.QLabel(self)
        self.x_input = QtWidgets.QLineEdit(self)
        self.y_input = QtWidgets.QLineEdit(self)

        self.xlim_check = QtWidgets.QCheckBox(self)
        self.xlim_low = ScientificDoubleSpinBox(self)
        self.xlim_high = ScientificDoubleSpinBox(self)

        self.ylim_check = QtWidgets.QCheckBox(self)
        self.ylim_low = ScientificDoubleSpinBox(self)
        self.ylim_high = ScientificDoubleSpinBox(self)

        self.signal_label = QtWidgets.QLabel(self)
        # self.signal_hbox
        self.xlabel = QtWidgets.QLineEdit(self)
        self.ylabel = QtWidgets.QLineEdit(self)
        self.label = QtWidgets.QLineEdit(self)
        self.legend = QtWidgets.QCheckBox(self)
        self.no_resample = QtWidgets.QCheckBox(self)
        self.xshareable = QtWidgets.QCheckBox(self)
        self.xlab = QtWidgets.QLabel(self)
        self.ylab = QtWidgets.QLabel(self)
        self.lab = QtWidgets.QLabel(self)
        self.toggle_hbox = QtWidgets.QHBoxLayout()
        self.color_label = QtWidgets.QLabel(self)
        self.color_chosen = QtWidgets.QLabel(self)
        self.color_input = QtWidgets.QLabel(self)

        self.color_button = QtWidgets.QPushButton(self)

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Apply |
                                                  QtWidgets.QDialogButtonBox.Ok |
                                                  QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.handle_apply_event)

        self.xlim_check.stateChanged.connect(self.enable_xlimits)
        self.ylim_check.stateChanged.connect(self.enable_ylimits)

        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.xhbox = QtWidgets.QHBoxLayout()
        self.yhbox = QtWidgets.QHBoxLayout()
        self.color_hbox = QtWidgets.QHBoxLayout()
        self.options_box = QtWidgets.QHBoxLayout()
        self.lab_box = QtWidgets.QHBoxLayout()
        self.xlim_box = QtWidgets.QHBoxLayout()
        self.ylim_box = QtWidgets.QHBoxLayout()
        self.init_UI(xloc=xloc, yloc=yloc)

        self.combo.activated.connect(self.change_list_view)
        self.item_list.currentRowChanged.connect(self.populate_signal_fields)
        self.color_button.clicked.connect(self.open_color_dialog)
        self.hello = 100


    def init_UI(self, xloc=None, yloc=None):
        self.x_qlabel.setText("X: ")
        self.y_qlabel.setText("Y: ")

        self.legend.setText("Legend")
        self.no_resample.setText("No Resample")
        self.xshareable.setText("X shareable")
        self.xlab.setText("X Label: ")
        self.ylab.setText("Y Label: ")
        self.lab.setText("Signal Name")
        self.combo_label.setText("Subplot Settings: ")
        self.signal_label.setText("Signal Settings: ")
        if xloc is None:
            xloc = 200
        if yloc is None:
            yloc = 200
        self.setGeometry(xloc, yloc, 600, 200)
        self.setWindowTitle('Edit Configuration')

        self.xlim_check.setText("X Limits")
        self.ylim_check.setText("Y Limits")

        self.color_label.setText("Color: ")
        self.color_chosen.setText("                     ")
        self.color_button.setText("Select a Color")
        self.color_button.setIcon(QtGui.QIcon("Icons/color-swatch.png"))

        self.xlim_low.setDecimals(4)
        self.xlim_high.setDecimals(4)
        self.ylim_low.setDecimals(4)
        self.ylim_high.setDecimals(4)

        self.color_hbox.addWidget(self.color_label)
        self.color_hbox.addWidget(self.color_input)
        self.color_hbox.addWidget(self.color_chosen)
        self.color_hbox.addWidget(self.color_button)
        self.color_hbox.addStretch()

        self.hbox.addWidget(self.combo_label)
        self.hbox.addWidget(self.combo)


        self.xhbox.addWidget(self.x_qlabel)
        self.xhbox.addWidget(self.x_input)

        self.options_box.addWidget(self.xlab)
        self.options_box.addWidget(self.xlabel)
        self.options_box.addWidget(self.ylab)
        self.options_box.addWidget(self.ylabel)
        self.toggle_hbox.addWidget(self.legend)
        self.toggle_hbox.addWidget(self.no_resample)
        self.toggle_hbox.addWidget(self.xshareable)
        self.toggle_hbox.addStretch()

        self.lab_box.addWidget(self.lab)
        self.lab_box.addWidget(self.label)

        self.yhbox.addWidget(self.y_qlabel)
        self.yhbox.addWidget(self.y_input)

        self.xlim_box.addWidget(self.xlim_check, 1)
        self.xlim_box.addWidget(self.xlim_low, 1)
        self.xlim_box.addWidget(self.xlim_high, 1)
        self.xlim_box.addStretch()

        self.ylim_box.addWidget(self.ylim_check, 1)
        self.ylim_box.addWidget(self.ylim_low, 1)
        self.ylim_box.addWidget(self.ylim_high, 1)
        self.ylim_box.addStretch()

        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.options_box)
        self.vbox.addLayout(self.toggle_hbox)
        self.vbox.addLayout(self.xlim_box)
        self.vbox.addLayout(self.ylim_box)
        self.vbox.addWidget(self.signal_label)
        self.vbox.addWidget(self.item_list)
        self.vbox.addLayout(self.lab_box)
        self.vbox.addLayout(self.xhbox)
        self.vbox.addLayout(self.yhbox)
        self.vbox.addLayout(self.color_hbox)
        self.vbox.addWidget(self.buttons)
        self.setLayout(self.vbox)

        self.populate_list_box(self.grid[0])
        self.populate_options(0)
        self.populate_signal_fields(0)

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

        if "noresample" in keys and strtobool(local_config['noresample']):
            self.no_resample.setChecked(True)
        else:
            self.no_resample.setChecked(False)

        # try:
        #     print(local_config['xshare'])
        # except KeyError:
        #     print('xshare not in {}'.format(pos))

        if "xshare" in keys and not strtobool(local_config['xshare']):
            self.xshareable.setChecked(False)
        else:
            self.xshareable.setChecked(True)

        if "xlim" in keys:
            self.xlim_check.setChecked(True)
            self.xlim_low.setEnabled(True)
            self.xlim_high.setEnabled(True)
            xlim = local_config['xlim']
            if isinstance(xlim, list) and len(xlim) == 2:
                self.xlim_low.setValue(float(xlim[0]))
                self.xlim_high.setValue(float(xlim[1]))
        else:
            self.xlim_check.setChecked(False)
            self.xlim_low.setEnabled(False)
            self.xlim_high.setEnabled(False)

        if "ylim" in keys:
            self.ylim_check.setChecked(True)
            self.ylim_low.setEnabled(True)
            self.ylim_high.setEnabled(True)
            ylim = local_config['ylim']
            if isinstance(ylim, list) and len(ylim) == 2:
                self.ylim_low.setValue(float(ylim[0]))
                self.ylim_high.setValue(float(ylim[1]))
        else:
            self.ylim_check.setChecked(False)
            self.ylim_low.setEnabled(False)
            self.ylim_high.setEnabled(False)

    def populate_list_box(self, key):
        ignore_items = ['xlabel', 'ylabel', 'legend', 'xlim', 'ylim', 'color', 'noresample', 'xshare']
        pos_items = [x for x in self.config[key] if x not in ignore_items]
        pos_items.sort()

        self.item_list.addItem("New Signal")
        for item in pos_items:
            self.item_list.addItem(item)
        self.item_list.setCurrentRow(0)

    def populate_signal_fields(self, idx):
        if idx != 0:
            pos = self.combo.currentText()
            pos = self.grid[self.combo.currentIndex()]
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

            if 'color' in keys:
                self.color_chosen.setStyleSheet("QWidget { background-color: %s;\n border:1px solid rgb(0, 0, 0)}" % local_config['color'])
                self.color_input.setText(local_config['color'])
            else:
                color_idx = (idx-1) % 10
                self.color_chosen.setStyleSheet("QWidget { background-color: %s;\n border:1px solid rgb(0, 0, 0)}" % default_colors[color_idx])
                self.color_input.setText(default_colors[color_idx])

            self.label.setText(label)
        else:
            self.x_input.clear()
            self.y_input.clear()
            self.label.clear()

            self.color_chosen.setStyleSheet("QWidget { background-color: #D3D3D3 ;\n border:1px solid rgb(0, 0, 0)}")
            self.color_input.setText("#D3D3D3")

    def handle_apply_event(self):
        idx = self.item_list.currentRow()
        xtext = self.x_input.text()
        ytext = self.y_input.text()
        label = self.label.text()

        pos = self.combo.currentText()
        pos = self.grid[self.combo.currentIndex()]
        item = self.item_list.currentItem()
        color = self.color_input.text()

        if ytext and xtext and label:
            if idx != 0:
                current_label = item.text()
                self.config[pos].pop(current_label, None)
                # del self.config[pos][current_label]
            self.config[pos][label] = dict()
            self.config[pos][label]['x'] = xtext
            self.config[pos][label]['y'] = ytext
            self.config[pos][label]['color'] = color
        else:
            if idx != 0:
                current_label = item.text()
                self.config[pos].pop(current_label, None)
                # del self.config[pos][current_label]

        xlabel = self.xlabel.text()
        ylabel = self.ylabel.text()
        legend = str(self.legend.isChecked())

        self.config[pos]['legend'] = legend
        self.config[pos]['xlabel'] = xlabel
        self.config[pos]['ylabel'] = ylabel
        if self.xlim_check.isChecked():
            xlow = self.xlim_low.value()
            xhigh = self.xlim_high.value()
            self.config[pos]['xlim'] = [str(xlow), str(xhigh)]
        else:
            self.config[pos].pop('xlim', None)

        if self.ylim_check.isChecked():
            ylow = self.ylim_low.value()
            yhigh = self.ylim_high.value()
            self.config[pos]['ylim'] = [str(ylow), str(yhigh)]
        else:
            self.config[pos].pop('ylim', None)

        if self.no_resample.isChecked():
            self.config[pos]['noresample'] = str(True)

        if not self.xshareable.isChecked():
            self.config[pos]['xshare'] = str(False)

        self.item_list.clear()
        self.populate_list_box(pos)

    def enable_xlimits(self, state):
        if state == QtCore.Qt.Checked:
            self.xlim_low.setEnabled(True)
            self.xlim_high.setEnabled(True)
        else:
            self.xlim_low.setDisabled(True)
            self.xlim_high.setDisabled(True)

    def enable_ylimits(self, state):
        if state == QtCore.Qt.Checked:
            self.ylim_low.setEnabled(True)
            self.ylim_high.setEnabled(True)
        else:
            self.ylim_low.setDisabled(True)
            self.ylim_high.setDisabled(True)

    def open_color_dialog(self):
        dlg = QtWidgets.QColorDialog()
        for idx, color in enumerate(default_colors):
            dlg.setCustomColor(idx, QtGui.QColor(color))

        if dlg.exec_():
            color = dlg.selectedColor().name()
            self.color_chosen.setStyleSheet("QWidget { background-color: %s;\n border:1px solid rgb(0, 0, 0)}" % color)
            self.color_input.setText(color)

