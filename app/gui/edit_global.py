from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui
from copy import deepcopy


class EditGlobalDialog(QtWidgets.QDialog):

    def __init__(self, config, xloc=None, yloc=None):
        super(EditGlobalDialog, self).__init__()
        self.config = deepcopy(config)
        self.setWindowIcon(QtGui.QIcon("Icons/application-wave.png"))

        self.server = self.config['setup']['server']
        self.tree = self.config['setup']['tree']

        self.server_label = QtWidgets.QLabel(self)
        self.server_input = QtWidgets.QLineEdit(self)

        self.tree_label = QtWidgets.QLabel(self)
        self.tree_input = QtWidgets.QLineEdit(self)

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.vbox = QtWidgets.QVBoxLayout()
        self.tree_hbox = QtWidgets.QHBoxLayout()
        self.server_hbox = QtWidgets.QHBoxLayout()

        self.init_UI(xloc=xloc, yloc=yloc)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.server_input.editingFinished.connect(self.update_server)
        self.tree_input.editingFinished.connect(self.update_tree)

    def init_UI(self, xloc, yloc):
        if xloc is None:
            xloc = 200
        if yloc is None:
            yloc = 200

        self.server_label.setText("Server Address: ")
        self.server_input.setText(self.server)

        self.tree_label.setText("Tree Name: ")
        self.tree_input.setText(self.tree)

        self.setGeometry(xloc, yloc, 500, 100)
        self.setWindowTitle('Edit Global Configuration')
        self.server_hbox.addWidget(self.server_label)
        self.server_hbox.addWidget(self.server_input)

        self.tree_hbox.addWidget(self.tree_label)
        self.tree_hbox.addWidget(self.tree_input)

        self.vbox.addLayout(self.server_hbox)
        self.vbox.addLayout(self.tree_hbox)
        self.vbox.addWidget(self.buttons)
        self.setLayout(self.vbox)

    def update_server(self):
        self.server = self.server_input.text()

    def update_tree(self):
        self.tree = self.tree_input.text()
