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
from .helpers import global_lcm
from distutils.util import strtobool
import logging
import MDSplus as mds

default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']

logger = logging.getLogger('pi-scope-logger')


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
        self.shared_axs = None
        # self.setGeometry(100, 100, 1200, 1200)

        self.acquiring_data = False

        if config_file is not None:
            self.load_configuration(config_file)

            if shot_number is None:
                self.shot_number = mdsh.get_current_shot(self.server, self.tree)
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

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_alive)
        self.timer.setInterval(10.0 * 1000)
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
        self.open_config_action.triggered.connect(self.onOpenClick)
        self.show()

    def check_alive(self):
        logger.debug("event watcher alive? % s" % str(self.mds_update_event.isAlive()))
        # print("MDSplus event watcher, alive or dead?: ", self.mds_update_event.isAlive())

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
            new_config['setup'] = {'col': dlg.column_setup,
                                   'server': dlg.server,
                                   'event': dlg.event,
                                   'tree': dlg.tree,
                                   }

            self.add_grid_keys(new_config, dlg.column_setup)
            self.config = new_config
            self.server = dlg.server
            self.tree = dlg.tree
            self.event_name = dlg.event

            self.enable_actions_after_config()
            self.node_locs = self.get_data_locs()
            self.update_subplot_config(dlg.column_setup)
            self.fetch_data(self.shot_number)

    def edit_configuration(self):
        xloc, yloc = self.new_dialog_positions()
        dlg = EditConfigDialog(self.config, xloc=xloc, yloc=yloc)
        if dlg.exec_():
            self.config = dlg.config
            self.node_locs = self.get_data_locs()
            sharex = self.shareX_action.isChecked()
            if sharex:
                self.shareX_action.setChecked(False)
                self.change_sharex()
                self.modify_shared_axes_list()
                self.shareX_action.setChecked(True)
                self.change_sharex()
            else:
                self.modify_shared_axes_list()
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
            # Disable the old MDSplus event if it is running
            update_state = self.autoUpdate_action.isChecked()
            self.autoUpdate_action.setChecked(False)
            self.change_auto_update(None)

            self.config_filename = filenames[0]
            self.load_configuration(filenames[0])
            self.data = None
            self.change_sharex()

            # Start up the new MDSplus event if it needs to be
            self.autoUpdate_action.setChecked(update_state)
            self.change_auto_update(update_state)

    def enable_actions_after_config(self):
        self.updateBtn.setEnabled(True)
        self.shareX_action.setEnabled(True)
        self.autoUpdate_action.setEnabled(True)
        self.openPanelConfigAction.setEnabled(True)
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)

    def load_configuration(self, filename):
        col_setup, locs = self.config_parser(filename)
        self.enable_actions_after_config()
        self.update_subplot_config(col_setup)
        self.node_locs = locs
        self.modify_shared_axes_list()

    def config_parser(self, filename):
        config = ConfigObj(filename)
        config = config.dict()
        self.config = config

        col_setup = self.config['setup']['col']
        col_setup = [int(x) for x in col_setup]

        # determine grid keys
        self.add_grid_keys(self.config, col_setup)

        try:
            self.tree = self.config['setup']['tree']
        except KeyError:
            self.config['setup']['tree'] = 'wipal'
            self.tree = 'wipal'

        self.event_name = self.config['setup']['event']
        self.server = self.config['setup']['server']
        data_locs = self.get_data_locs()
        return col_setup, data_locs

    def add_grid_keys(self, config, column_setup):
        for col, nrow in enumerate(column_setup):
            for row in range(nrow):
                new_key = "{0:d}{1:d}".format(row, col)
                if new_key not in self.config:
                    config[new_key] = dict()

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
        top_ignore = ['xlabel', 'ylabel', 'xlim', 'ylim', 'legend', 'noresample', 'xshare']
        j = 0
        for k in keys:
            if k not in top_ignore:
                # this is a signal
                # time to check if it has a color picked already
                if 'color' not in local_config[k].keys():
                    self.config[key][k]['color'] = default_colors[j % 10]
                    j += 1

    # def update_subplot_config(self, nrow, ncol):
    def update_subplot_config(self, col_setup):
        if self.figure is not None:
            self.vbox.removeWidget(self.toolbar)
            self.vbox.removeWidget(self.canvas)

        self.vbox.removeItem(self.hbox)
        self.vbox.removeItem(self.shot_hbox)

        #self.figure, self.axs = plt.subplots(nrow, ncol)
        self.figure = plt.figure(0)
        self.axs = []
        cols = [x for x in col_setup if x > 0]
        lcm = global_lcm(cols)
        ncols = len(cols)
        for idx, item in enumerate(cols):
            factor = lcm // item
            axs = []
            for j in range(item):
                ax = plt.subplot2grid((lcm, ncols), (factor*j, idx), rowspan=factor)
                axs.append(ax)
            self.axs.append(axs)

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.vbox.addWidget(self.toolbar, 2)
        self.vbox.addLayout(self.shot_hbox)
        self.vbox.addWidget(self.canvas, 12)
        self.vbox.addLayout(self.hbox)

    @QtCore.pyqtSlot(int)
    def fetch_data(self, shot_number):
        if self.acquiring_data:
            # already grabbing data, do nothing
            logger.debug("User tried to grab more data when already acquiring.  Ignoring User request.")
            return

        self.acquiring_data = True
        self.status.setText("Retrieving Data from Shot {0:d}".format(shot_number))
        self.shot_number = shot_number

        node_locs = self.node_locs
        keys = node_locs.keys()
        ignore_items = ['legend', 'xlabel', 'ylabel', 'xlim', 'ylim', 'color', 'noresample', 'xshare']
        self.data = dict()
        self.completion = 0
        self.n_positions = 0
        # First loop through and count the number of signals
        for k in keys:
            self.data[k] = list()
            for name in node_locs[k]:
                if name not in ignore_items:
                    self.n_positions += 1
        logger.debug("Asking if tree is available to be opened")
        tree_available = mdsh.check_open_tree(shot_number, self.server, self.tree)
        print("is the tree available?", tree_available)
        if not tree_available:
            print('passing None to hanld mdsplus data')
            self.handle_mdsplus_data(None)
            self.acquiring_data = False
            logger.warn("tree was unable to be opened. shot = %d" % shot_number)
            return
        # Now reloop over and start the workers
        logger.debug("Asking for data")
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
        logger.debug("Retrieving data for %s" % name)
        if self.completion == self.n_positions:
            self.acquiring_data = False
            self.handle_mdsplus_data(self.data)

    def handle_mdsplus_data(self, data):
        self.data = data

        axs = self.axs
        for axes in axs:
            for ax in axes:
                ax.cla()
        if data is None:
            self.status.setText("Error opening Shot {0:d}".format(self.shot_number))
            logger.warn("No data for %d" % self.shot_number)
        elif mdsh.check_data_dictionary(self.data):
            self.down_samplers = data_plotter.plot_all_data(axs, self.node_locs, data,
                                                            downsampling=self.downsampling_points)
            self.status.setText("Idle")
            logger.debug("There is data for %d, now plotting" % self.shot_number)
        else:
            self.status.setText("Didn't Find any data in Shot {0:d}".format(self.shot_number))
            self.data = None
            logger.debug("No data was found for %d" % self.shot_number)

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
                    logger.debug("Auto update is now on")
                    self.mds_update_event = MyEvent(self.event_name)
                    self.mds_update_event.sender.emitter.connect(self.handle_incoming_mds_event)
                    self.timer.start()
            else:
                if self.mds_update_event is not None and self.mds_update_event.isAlive():
                    self.timer.stop()
                    try:
                        self.mds_update_event.cancel()
                    except mds.mdsExceptions.SsSUCCESS as e:
                        print(e)
                        logger.error("STUPID MDSPLUS CANCEL ERROR, %s" % e.message)
                    self.mds_update_event = None
                    logger.debug("Auto update is now off.")

    def change_sharex(self):
        axs = self.shared_axs

        if axs is None or len(axs) == 1:
            # Nothing to do here
            return

        ax0 = axs[0]
        if self.shareX_action.isChecked():
            for ax in axs[1:]:
                ax0.get_shared_x_axes().join(ax, ax0)
        else:
            for ax in axs[1:]:
                ax0.get_shared_x_axes().remove(ax)

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

    def modify_shared_axes_list(self):
        self.shared_axs = []
        for pos in self.node_locs:
            if 'xshare' in self.node_locs[pos] and not strtobool(self.node_locs[pos]['xshare']):
                pass
            else:
                i, j = (int(x) for x in pos)
                self.shared_axs.append(self.axs[j][i])

    @QtCore.pyqtSlot(int)
    def handle_incoming_mds_event(self, shot_number):
        try:
            self.mds_update_event.cancel()
            self.mds_update_event = None
        except mds.mdsExceptions.SsSUCCESS as e:
            print(e)
            logger.error("STUPID MDSPLUS CANCEL ERROR in handle_incoming_mds_event, %s" % e.message)
        self.mds_update_event = MyEvent(self.event_name)
        self.mds_update_event.sender.emitter.connect(self.handle_incoming_mds_event)
        self.fetch_data(shot_number)
