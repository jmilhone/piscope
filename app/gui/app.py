from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui
from configobj import ConfigObj
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from .workers import Worker
from ..data import mdsplus_helpers as mdsh
from ..plotting import data_plotter
from .events import MyEvent
from .edit_configuration import EditConfigDialog
from .new_configuration import NewConfigDialog
from .downsample_dialog import EditDownsampleDialog
from .edit_global import EditGlobalDialog

default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']


class MyWindow(QtWidgets.QMainWindow):

    def __init__(self, config_file, shot_number=None):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Big Red Ball PiScope")
        self.setWindowIcon(QtGui.QIcon("Icons/application-wave.png"))
        # Useful configuration things
        self.event_name = None
        self.server = None
        self.config = None
        self.tree = None
        self.mds_update_event = None
        self.config_filename = config_file
        self.threadpool = QtCore.QThreadPool()  # This is where the grabbing of data will take place to not lock the gui
        self.down_samplers = None
        self.downsampling_points = 10000
        self.node_locs = None
        self.data = None

        # for the progress bar
        self.n_positions = 0.0
        self.completion = 0.0


        # Menu Bar stuff
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.edit_menu = self.menu.addMenu("&Edit")
        self.option_menu = self.menu.addMenu("&Options")
        self.open_config_action = QtWidgets.QAction(QtGui.QIcon("Icons/blue-folder-horizontal-open.png"),
                                                    "&Open Configuration...", self)
        self.open_config_action.triggered.connect(self.onOpenClick)
        self.shareX_action = QtWidgets.QAction("&Share X-axis", self)
        self.autoUpdate_action = QtWidgets.QAction("&Auto Update", self)
        self.openPanelConfigAction = QtWidgets.QAction(QtGui.QIcon("Icons/application--pencil"),
                                                       "&Edit Configuration...", self)
        self.save_action = QtWidgets.QAction(QtGui.QIcon("Icons/disk-black.png"), "&Save...", self)
        self.save_as_action = QtWidgets.QAction(QtGui.QIcon("Icons/disks-black.png"), "Save As", self)
        self.exit_action = QtWidgets.QAction(QtGui.QIcon("Icons/cross-button.png"), "&Exit PiScope", self)
        self.new_config_action = QtWidgets.QAction(QtGui.QIcon("Icons/application--plus.png"),
                                                   "&New Configuration...", self)
        self.change_downsample = QtWidgets.QAction("Edit Downsampling", self)
        self.edit_global_action = QtWidgets.QAction(QtGui.QIcon("Icons/gear--pencil.png"),
                                                    "Edit Global Settings...", self)

        self.centralWidget = QtWidgets.QWidget()
        self.spinBox = QtWidgets.QSpinBox(self)
        self.font = self.spinBox.font()

        self.updateBtn = QtWidgets.QPushButton("Update", self)
        self.updateBtn.setIcon(QtGui.QIcon("Icons/arrow-circle-225.png"))
        self.status = QtWidgets.QLabel("Idle", self)

        self.hbox = QtWidgets.QHBoxLayout()
        self.shot_hbox = QtWidgets.QHBoxLayout()
        self.shot_number_label = QtWidgets.QLabel(self)
        self.progess_bar = QtWidgets.QProgressBar(self)

        self.vbox = QtWidgets.QVBoxLayout()
        self.init_UI()

        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.axs = None

        self.setGeometry(100, 100, 1200, 1200)

        if config_file is not None:
            self.load_configuration(config_file)

            if shot_number is None:
                self.shot_number = mdsh.get_current_shot(self.tree)
            else:
                self.shot_number = shot_number

            if self.shot_number is not None:
                self.spinBox.setValue(self.shot_number)
                self.shot_number_label.setText("Shot Number: {0:d}".format(self.shot_number))
                self.fetch_data(self.shot_number)

        else:
            self.updateBtn.setDisabled(True)
            self.status.setText("Please Load a Configuration File")
            self.autoUpdate_action.setDisabled(True)
            self.shareX_action.setDisabled(True)
            self.openPanelConfigAction.setDisabled(True)
            self.save_action.setDisabled(True)
            self.save_as_action.setDisabled(True)

        self.exit_action.setEnabled(True)
        self.updateBtn.clicked.connect(self.update_pressed)
        self.shareX_action.triggered.connect(self.change_sharex)
        self.openPanelConfigAction.triggered.connect(self.edit_configuration)
        self.save_action.triggered.connect(self.save_configuration)
        self.save_as_action.triggered.connect(self.save_as_configuration)
        self.new_config_action.triggered.connect(self.new_configuration)
        self.change_downsample.triggered.connect(self.open_change_downsample)
        self.autoUpdate_action.triggered.connect(self.change_auto_update)
        self.exit_action.triggered.connect(self.close)
        self.edit_global_action.triggered.connect(self.edit_global_settings)
        self.show()

    def init_UI(self):
        # Add all of the file actions to the file menu
        self.file_menu.addAction(self.new_config_action)
        self.file_menu.addAction(self.open_config_action)
        # self.file_menu.addAction(self.openPanelConfigAction)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addAction(self.exit_action)

        self.edit_menu.addAction(self.edit_global_action)
        self.edit_menu.addAction(self.openPanelConfigAction)

        # Add all of the option actions to the action menu
        self.option_menu.addAction(self.autoUpdate_action)
        self.option_menu.addAction(self.shareX_action)
        self.option_menu.addAction(self.change_downsample)


        self.autoUpdate_action.setCheckable(True)
        self.shareX_action.setCheckable(True)
        self.spinBox.setRange(0, 999999)
        self.spinBox.setKeyboardTracking(False)

        self.progess_bar.setValue(0.0)


        # Take care of fonts here
        self.font.setPointSize(18)
        self.spinBox.setFont(self.font)
        self.status.setFont(self.font)
        self.updateBtn.setFont(self.font)
        self.shot_number_label.setFont(self.font)
        self.progess_bar.setFont(self.font)
        self.progess_bar.setTextVisible(False)

        # Shot number and Status Stuff
        self.hbox.addWidget(self.spinBox)
        self.hbox.addWidget(self.updateBtn)
        self.hbox.addWidget(self.progess_bar)
        self.hbox.addWidget(self.status)
        self.hbox.addStretch(1)

        # Displayed shot
        self.shot_hbox.addStretch()
        self.shot_hbox.addWidget(self.shot_number_label)
        self.shot_hbox.addStretch()

        # Add everything to the vertical box layout
        self.vbox.addLayout(self.shot_hbox)
        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox)
        self.centralWidget.setLayout(self.vbox)
        self.setCentralWidget(self.centralWidget)

    def new_configuration(self):
        xloc, yloc = self.new_dialog_positions()
        dlg = NewConfigDialog(xloc=xloc, yloc=yloc)

        if dlg.exec_():
            self.config_filename = None
            new_config = dict()
            new_config['setup'] = {'nrow': dlg.nrow,
                                   'ncol': dlg.ncol,
                                   'server': dlg.server,
                                   'event': dlg.event,
                                   'tree': dlg.tree,
                                   }
            for i in range(dlg.nrow):
                for j in range(dlg.ncol):
                    new_config['{0:d}{1:d}'.format(i, j)] = {}

            self.config = new_config
            self.server = dlg.server
            self.tree = dlg.tree
            self.event_name = dlg.event

            self.enable_actions_after_config()
            self.node_locs = self.get_data_locs()
            self.update_subplot_config(dlg.nrow, dlg.ncol)
            self.fetch_data(self.shot_number)

    def edit_configuration(self):
        xloc, yloc = self.new_dialog_positions()
        dlg = EditConfigDialog(self.config, xloc=xloc, yloc=yloc)
        if dlg.exec_():
            self.config = dlg.config
            self.node_locs = self.get_data_locs()
            self.fetch_data(self.shot_number)

    def edit_global_settings(self):
        xloc, yloc = self.new_dialog_positions()
        dlg = EditGlobalDialog(self.config, xloc=xloc, yloc=yloc)
        if dlg.exec_():
            self.server = dlg.server
            self.tree = dlg.tree
            self.config['setup']['server'] = self.server
            self.config['setup']['tree'] = self.tree

    def new_dialog_positions(self):
        rect = self.geometry()
        xloc = rect.x() + 0.1 * rect.width()
        yloc = rect.y() + 0.1 * rect.height()
        return xloc, yloc

    def onOpenClick(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(["Config Files (*.ini)", "Text files (*.txt)"])
        dlg.selectNameFilter("Config Files (*.ini)")
        files = list()

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.config_filename = filenames[0]
            self.load_configuration(filenames[0])

    def enable_actions_after_config(self):
        self.updateBtn.setEnabled(True)
        self.shareX_action.setEnabled(True)
        self.autoUpdate_action.setEnabled(True)
        self.openPanelConfigAction.setEnabled(True)
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)

    def load_configuration(self, filename):
        nrow, ncol, locs = self.config_parser(filename)
        self.enable_actions_after_config()
        self.update_subplot_config(nrow, ncol)

        self.node_locs = locs

        #self.fetch_data(self.shot_number)

    def config_parser(self, filename):
        config = ConfigObj(filename)
        config = config.dict()
        self.config = config
        nrow = int(self.config['setup']['nrow'])
        ncol = int(self.config['setup']['ncol'])

        try:
            self.tree = self.config['setup']['tree']
        except KeyError:
            self.tree = 'wipal'

        self.event_name = self.config['setup']['event']
        self.server = self.config['setup']['server']
        data_locs = self.get_data_locs()

        return nrow, ncol, data_locs

    def get_data_locs(self):
        data_locs = {}
        for key in self.config.keys():
            if key.lower() != 'setup':
                data_locs[key] = self.config[key]
                self.parse_data_colors(key)
        return data_locs

    def parse_data_colors(self, key):
        local_config = self.config[key]
        keys = [x for x in local_config.keys()]
        keys.sort()
        top_ignore = ['xlabel', 'ylabel', 'xlim', 'ylim', 'legend']
        j = 0
        for k in keys:
            if k not in top_ignore:
                # this is a signal
                # time to check if it has a color picked already
                if 'color' not in local_config[k].keys():
                    self.config[key][k]['color'] = default_colors[j % 10]
                    j += 1

    def update_subplot_config(self, nrow, ncol):
        if self.figure is not None:
            self.vbox.removeWidget(self.toolbar)
            self.vbox.removeWidget(self.canvas)

        self.vbox.removeItem(self.hbox)
        self.vbox.removeItem(self.shot_hbox)

        self.figure, self.axs = plt.subplots(nrow, ncol)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.vbox.addWidget(self.toolbar, 2)
        self.vbox.addLayout(self.shot_hbox)
        self.vbox.addWidget(self.canvas, 12)
        self.vbox.addLayout(self.hbox)

    @QtCore.pyqtSlot(int)
    def fetch_data(self, shot_number):
        self.status.setText("Retrieving Data from Shot {0:d}".format(shot_number))
        self.shot_number = shot_number

        node_locs = self.node_locs
        keys = node_locs.keys()
        ignore_items = ['legend', 'xlabel', 'ylabel', 'xlim', 'ylim', 'color']
        self.data = dict()
        self.completion = 0
        self.n_positions = 0
        # First loop through and count the number of signals
        for k in keys:
            self.data[k] = list()
            for name in node_locs[k]:
                if name not in ignore_items:
                    self.n_positions += 1
        # Now reloop over and start the workers
        for k in keys:
            for name in node_locs[k]:
                if name not in ignore_items:
                    worker = Worker(mdsh.retrieve_signal, shot_number, node_locs[k][name], k, name,
                                    self.server, self.tree)
                    worker.signals.result.connect(self.handle_returning_data)
                    self.threadpool.start(worker)

    def handle_returning_data(self, data_tuple):
        self.completion += 1

        self.progess_bar.setValue(self.completion / self.n_positions * 100.0)
        # unpack data_tuple
        loc, name, data = data_tuple
        self.data[loc].append(data)

        if self.completion == self.n_positions:
            self.handle_mdsplus_data(self.data)

    def handle_mdsplus_data(self, data):
        self.data = data

        axs = self.axs
        for axes in axs:
            for ax in axes:
                ax.cla()
        if data is None:
            self.status.setText("Error opening Shot {0:d}".format(self.shot_number))
        elif mdsh.check_data_dictionary(self.data):
            self.down_samplers = data_plotter.plot_all_data(axs, self.node_locs, data,
                                                            downsampling=self.downsampling_points)
            self.status.setText("Idle")
        else:
            self.status.setText("Didn't Find any data in Shot {0:d}".format(self.shot_number))

        self.shot_number_label.setText("Shot {0:d}".format(self.shot_number))
        self.spinBox.setValue(self.shot_number)
        self.figure.tight_layout()

        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()
        self.progess_bar.setValue(0.0)

    def change_auto_update(self, state):
        if self.event_name:
            # if state == QtCore.Qt.Checked:
            if self.autoUpdate_action.isChecked():
                if self.mds_update_event is None:
                    self.mds_update_event = MyEvent(self.event_name)
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
        if shot_number == self.shot_number and self.data is not None:
            # No change, just replot
            self.handle_mdsplus_data(self.data)
        else:
            self.shot_number = shot_number
            self.fetch_data(shot_number)

    def save_as_configuration(self):
        self.save_as_dialog = QtWidgets.QFileDialog()
        self.save_as_dialog.fileSelected.connect(self._save_configuration)
        self.save_as_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.save_as_dialog.setNameFilter("Config Files (*.ini *.txt)")
        self.save_as_dialog.exec_()

    def save_configuration(self):
        if self.config_filename:
            self._save_configuration(self.config_filename)
        else:
            self.save_as_configuration()

    def _save_configuration(self, filename):
        self.config_filename = filename
        config_obj = ConfigObj(indent_type="    ")
        config_obj.filename = self.config_filename
        config_obj.update(self.config)
        config_obj.write()

    def open_change_downsample(self):
        xloc, yloc = self.new_dialog_positions()
        dlg = EditDownsampleDialog(self.downsampling_points, xloc=xloc, yloc=yloc)
        if dlg.exec_():
            self.downsampling_points = dlg.points

            if self.data is not None:
                self.handle_mdsplus_data(self.data)
            else:
                self.fetch_data(self.shot_number)

