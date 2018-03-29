from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui
from configparser import ConfigParser
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from workers import Worker
from ..data import mdsplus_helpers as mdsh
from ..plotting import data_plotter
import events


class MyWindow(QtWidgets.QMainWindow):

    def __init__(self, config_file):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Big Red Ball PyScope")
        self.event_name = None
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.button_action = QtWidgets.QAction("&Open Configuration", self)
        self.file_menu.addAction(self.button_action)
        self.button_action.triggered.connect(self.onOpenClick)
        self.centralWidget = QtWidgets.QWidget()
        self.shot_number = 30270 #mdsh.get_current_shot()
        self.threadpool = QtCore.QThreadPool()  # This is where the grabbing of data will take place to not lock the gui

        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(0, 999999)
        self.spinBox.setKeyboardTracking(False)

        if self.shot_number is not None:
            self.spinBox.setValue(self.shot_number)

        # Share x axis check box
        self.shareX = QtWidgets.QCheckBox("Share X-Axis", self)

        # Binned data check box
        # self.binned = QtWidgets.QCheckBox("Binned?", self)

        # Auto Update Shot Number check box
        self.autoUpdate = QtWidgets.QCheckBox("Auto Update", self)

        # Update Plot Button
        self.updateBtn = QtWidgets.QPushButton("Update", self)

        # Status Label
        self.status = QtWidgets.QLabel("Idle", self)

        # Handle Layout Here
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.spinBox)
        #self.hbox.addWidget(self.binned)
        self.hbox.addWidget(self.shareX)
        self.hbox.addWidget(self.autoUpdate)
        self.hbox.addWidget(self.updateBtn)
        self.hbox.addWidget(self.status)
        self.hbox.addStretch(1)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox)
        self.centralWidget.setLayout(self.vbox)
        self.setCentralWidget(self.centralWidget)

        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.axs = None

        self.setGeometry(100, 100, 1200, 1200)

        if config_file is not None:
            self.load_configuration(config_file)

        self.updateBtn.clicked.connect(self.update_pressed)
        self.autoUpdate.stateChanged.connect(self.change_auto_update)
        self.shareX.stateChanged.connect(self.change_sharex)

        self.show()

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
            self.update_subplot_config(nrow, ncol)
            self.node_locs = locs
            self.fetch_data(self.shot_number)

    def config_parser(self, filename):
        parser = ConfigParser()
        parser.read(filename)
        nrow = 0
        ncol = 0
        if parser.has_section("setup"):
            if parser.has_option("setup", "nrow"):
                nrow = parser.getint("setup", "nrow")
            if parser.has_option("setup", "ncol"):
                ncol = parser.getint("setup", "ncol")
            if parser.has_option("setup", "event"):
                self.event_name = parser.get("setup", "event")
            #print(type(nrow), ncol)

        sections = []

        for i in xrange(nrow):
            for j in xrange(ncol):
                sections.append("{0:d}{1:d}".format(i, j))
        data_locs = {}
        for sec in sections:
            temp = {}
            if parser.has_section(sec):
                items = parser.items(sec)
                for item in items:
                    temp[item[0]] = item[1]
                data_locs[sec] = temp
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
        worker = Worker(mdsh.retrieve_all_data, shot_number, node_locs)
        worker.signals.result.connect(self.handle_mdsplus_data)
        self.threadpool.start(worker)

    def handle_mdsplus_data(self, data):
        self.data = data
        axs = self.axs
        for axes in axs:
            for ax in axes:
                ax.cla()
        if data is None:
            self.status.setText("Error opening Shot {0:d}".format(self.shot_number))
        else:

            data_plotter.plot_all_data(axs, self.node_locs, self.data)
        self.figure.suptitle("Shot {0:d}".format(self.shot_number))
        self.figure.tight_layout()

        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()
        self.status.setText("Idle")

    def change_auto_update(self, state):
        if self.axs is None:
            # Exit early because it's hard to load data with no config file
            return

        if self.event_name:
            if state == QtCore.Qt.Checked:
                if self.mds_update_event is None:
                    self.mds_update_event = events.MyEvent(self.event_name)
                    self.mds_update_event.sender.emitter.connect(self.fetch_data)
            else:
                if self.mds_update_event is not None and self.mds_update_event.isAlive():
                    self.mds_update_event.cancel()
                    self.mds_update_event = None


    def change_sharex(self, state):
        if self.axs is None:
            # Exit early before bad things happen
            return
        axs = self.axs
        ax0 = axs[0][0]
        if state == QtCore.Qt.Checked:
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
        if self.axs is None:
            # Hard to grab data if you don't have a config file
            return
        shot_number = self.spinBox.value()
        self.shot_number = shot_number
        self.fetch_data(shot_number)