from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui
from configobj import ConfigObj
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from workers import Worker
from ..data import mdsplus_helpers as mdsh
from ..plotting import data_plotter
import events


class MyWindow(QtWidgets.QMainWindow):

    def __init__(self, config_file, shot_number=None):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Big Red Ball PiScope")

        # Useful configuration things
        self.event_name = None
        self.server = None
        self.config = None
        self.threadpool = QtCore.QThreadPool()  # This is where the grabbing of data will take place to not lock the gui

        if shot_number is None:
            self.shot_number = mdsh.get_current_shot()
        else:
            self.shot_number = shot_number

        # Menu Bar stuff
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.open_config_action = QtWidgets.QAction("&Open Configuration", self)
        self.file_menu.addAction(self.open_config_action)
        self.open_config_action.triggered.connect(self.onOpenClick)
        self.option_menu = self.menu.addMenu("&Options")
        self.shareX_action = QtWidgets.QAction("&Share X-axis", self)
        self.autoUpdate_action = QtWidgets.QAction("&Auto Update", self)
        self.option_menu.addAction(self.autoUpdate_action)
        self.option_menu.addAction(self.shareX_action)
        self.autoUpdate_action.setCheckable(True)
        self.shareX_action.setCheckable(True)

        self.centralWidget = QtWidgets.QWidget()

        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(0, 999999)
        self.spinBox.setKeyboardTracking(False)

        if self.shot_number is not None:
            self.spinBox.setValue(self.shot_number)

        # self.shareX = QtWidgets.QCheckBox("Share X-Axis", self)
        # self.binned = QtWidgets.QCheckBox("Binned?", self)
        # self.autoUpdate = QtWidgets.QCheckBox("Auto Update", self)
        self.updateBtn = QtWidgets.QPushButton("Update", self)
        self.status = QtWidgets.QLabel("Idle", self)

        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()
        self.initalize_layout()

        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.axs = None

        self.setGeometry(100, 100, 1200, 1200)

        if config_file is not None:
            self.load_configuration(config_file)
        else:
            self.updateBtn.setDisabled(True)
            self.status.setText("Please Load a Configuration File")
            self.autoUpdate_action.setDisabled(True)
            self.shareX_action.setDisabled(True)

        self.updateBtn.clicked.connect(self.update_pressed)
        # self.autoUpdate.stateChanged.connect(self.change_auto_update)
        #self.shareX.stateChanged.connect(self.change_sharex)
        self.shareX_action.triggered.connect(self.change_sharex)
        self.show()


    def initalize_layout(self):
        self.hbox.addWidget(self.spinBox)
        #self.hbox.addWidget(self.binned)
        # self.hbox.addWidget(self.shareX)
        # self.hbox.addWidget(self.autoUpdate)
        self.hbox.addWidget(self.updateBtn)
        self.hbox.addWidget(self.status)
        self.hbox.addStretch(1)

        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox)
        self.centralWidget.setLayout(self.vbox)
        self.setCentralWidget(self.centralWidget)

    def onOpenClick(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(["Config Files (*.ini)", "Text files (*.txt)"])
        dlg.selectNameFilter("Config Files (*.ini)")
        files = []

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.load_configuration(filenames[0])

    def load_configuration(self, filename):
            nrow, ncol, locs = self.config_parser(filename)
            self.updateBtn.setEnabled(True)
            self.shareX_action.setEnabled(True)
            self.autoUpdate_action.setEnabled(True)
            self.update_subplot_config(nrow, ncol)
            self.node_locs = locs

            self.fetch_data(self.shot_number)

    def config_parser(self, filename):
        config = ConfigObj(filename)
        config = config.dict()
        self.config = config

        nrow = int(config['setup']['nrow'])
        ncol = int(config['setup']['ncol'])
        self.event = config['setup']['event']
        self.server = config['setup']['server']

        data_locs = {}
        for key in config.keys():
            if key.lower() != 'setup':
                data_locs[key] = config[key]
        return nrow, ncol, data_locs


    def update_subplot_config(self, nrow, ncol):
        if self.figure is not None:
            self.vbox.removeWidget(self.toolbar)
            self.vbox.removeWidget(self.canvas)

        self.vbox.removeItem(self.hbox)

        self.figure, self.axs = plt.subplots(nrow, ncol)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.vbox.addWidget(self.toolbar, 2)
        self.vbox.addWidget(self.canvas, 12)
        self.vbox.addLayout(self.hbox)

    @QtCore.pyqtSlot(int)
    def fetch_data(self, shot_number):
        self.shot_number = shot_number
        self.spinBox.setValue(shot_number)
        node_locs = self.node_locs
        self.status.setText("Retrieving Data from Shot {0:d}".format(shot_number))
        worker = Worker(mdsh.retrieve_all_data, shot_number, node_locs, self.server)
        worker.signals.result.connect(self.handle_mdsplus_data)
        self.threadpool.start(worker)

    def handle_mdsplus_data(self, data):
        axs = self.axs
        for axes in axs:
            for ax in axes:
                ax.cla()
        if data is None:
            self.status.setText("Error opening Shot {0:d}".format(self.shot_number))
        else:
            data_plotter.plot_all_data(axs, self.node_locs, data)
        self.figure.suptitle("Shot {0:d}".format(self.shot_number))
        self.figure.tight_layout()

        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()
        self.status.setText("Idle")

    def change_auto_update(self, state):
        if self.event_name:
            # if state == QtCore.Qt.Checked:
            if self.autoUpdate_action.isChecked():
                if self.mds_update_event is None:
                    self.mds_update_event = events.MyEvent(self.event_name)
                    self.mds_update_event.sender.emitter.connect(self.fetch_data)
            else:
                if self.mds_update_event is not None and self.mds_update_event.isAlive():
                    self.mds_update_event.cancel()
                    self.mds_update_event = None


    def change_sharex(self):
        axs = self.axs
        ax0 = axs[0][0]
        if self.shareX_action.isChecked():
            for ax in axs:
                for a in ax:
                    if a != axs[0][0]:
                        a.get_shared_x_axes().join(a, ax0)
        else:
            for ax in axs:
                for a in ax:
                    if a != axs[0][0]:
                        ax0.get_shared_x_axes().remove(a)

    def update_pressed(self):
        shot_number = self.spinBox.value()
        self.shot_number = shot_number
        self.fetch_data(shot_number)
