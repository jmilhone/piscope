from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets, QtGui
from configobj import ConfigObj
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from .workers import Worker
from ..data import mdsplus_helpers as mdsh
from ..plotting import data_plotter
from ..config import parser
from .events import MyEvent
from .edit_configuration import EditConfigDialog
from .new_configuration import NewConfigDialog
from .downsample_dialog import EditDownsampleDialog
from .edit_global import EditGlobalDialog
from distutils.util import strtobool
import logging
import MDSplus as mds

default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']

logger = logging.getLogger('pi-scope-logger')


class MyWindow(QtWidgets.QMainWindow):
    """The PiScope Main Window

    Note: Auto-updating will only work if you are on the same subnet as your MDSplus server
    """

    def __init__(self, config_file=None, shot_number=None):
        """

        Args:
            config_file (str, optional): filepath to a config file (*.ini)
            shot_number (int, optional): shot number to open

        Attributes:
             config (dict): Configuration containing information for data retrieval and plotting
             server (str): MDSplus server to retrieve data from
             tree (str): MDSplus tree name, default is wipal
             event_name (str): MDSplus event name to catch for auto-update.  Note this only works if you are on the same
                subnet as your MDSplus server
        """
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
        self.setGeometry(100, 100, 500, 500)

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
            self.shot_number = None
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
        self.openPanelConfigAction.triggered.connect(self.open_edit_configuration_dialog)
        self.save_action.triggered.connect(self.save_configuration)
        self.save_as_action.triggered.connect(self.save_as_configuration)
        self.new_config_action.triggered.connect(self.new_configuration)
        self.change_downsample.triggered.connect(self.open_change_downsample)
        self.autoUpdate_action.triggered.connect(self.change_auto_update)
        self.exit_action.triggered.connect(self.close)
        self.edit_global_action.triggered.connect(self.open_edit_global_settings)
        self.open_config_action.triggered.connect(self.open_config_dialog)
        self.show()

    def check_alive(self):
        """
        Checks the status of the self.mds_update_event thread and writes to log.
        """
        logger.debug("event watcher alive? % s" % str(self.mds_update_event.isAlive()))

    def init_UI(self):
        """
        Initializes the layout of the BRB PiScope User Interface

        The main layout is a vertical box layout (self.vbox).
        """
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
        """
        Opens a NewConfigDialog instance / dialog box to create a new configuration.

        User can create a new BRB PiScope configuration using this dialog.  User can configure the subplot orientation,
        the MDSplus server, the MDSplus tree, and the MDSplus event. There will not be any information from a previous
        configuration stored after creating a new configuration.
        """
        xloc, yloc = self._new_dialog_positions()
        dlg = NewConfigDialog(xloc=xloc, yloc=yloc)

        if dlg.exec_():
            self.config_filename = None
            new_config = dict()
            new_config['setup'] = {'col': dlg.column_setup,
                                   'server': dlg.server,
                                   'event': dlg.event,
                                   'tree': dlg.tree,
                                   }
            parser.add_grid_keys(new_config, dlg.column_setup)
            # self.add_grid_keys(new_config, dlg.column_setup)
            self.config = new_config
            self.server = dlg.server
            self.tree = dlg.tree
            self.event_name = dlg.event

            self.enable_actions_after_config()
            #self.node_locs = self.get_data_locs()
            self.node_locs = parser.get_data_locs(self.config)
            self.update_subplot_config(dlg.column_setup)

            if self.shot_number is None:
                self.shot_number = mdsh.get_current_shot(self.server, self.tree)
                self.spinBox.setValue(self.shot_number)
            self.fetch_data(self.shot_number)

    def open_edit_configuration_dialog(self):
        """
        Opens a EditConfigDialog dialog box where the user can add and edit signals for the current subplots.

        Note: Data will be fetched if the OK on the dialog box is hit.
        """
        xloc, yloc = self._new_dialog_positions()
        dlg = EditConfigDialog(self.config, xloc=xloc, yloc=yloc)
        if dlg.exec_():
            self.config = dlg.config
            # self.node_locs = self.get_data_locs()
            self.node_locs = self.get_data_locs(self.config)
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

    def open_edit_global_settings(self):
        """
        Opens a EditGlobalDialog dialog box where the user can edit the server and tree names.
        """
        xloc, yloc = self._new_dialog_positions()
        dlg = EditGlobalDialog(self.config, xloc=xloc, yloc=yloc)
        if dlg.exec_():
            self.server = dlg.server
            self.tree = dlg.tree
            self.config['setup']['server'] = self.server
            self.config['setup']['tree'] = self.tree

    def _new_dialog_positions(self):
        """
        Helper function for finding the x and y location to open a dialog box at.

        Returns:
            xloc (float): x location on the screen
            yloc (float): y location on the screen
        """
        rect = self.geometry()
        xloc = rect.x() + 0.1 * rect.width()
        yloc = rect.y() + 0.1 * rect.height()
        return xloc, yloc

    def open_config_dialog(self):
        """
        Opens a QFileDialog dialog box for picking a configuration file to open.

        If a file is picked, the configuration will replace the current configuration.
        """
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

            if self.shot_number is None:
                self.shot_number = mdsh.get_current_shot(self.server, self.tree)
            self.spinBox.setValue(self.shot_number)
            self.status.setText("Idle")
            # Start up the new MDSplus event if it needs to be
            self.autoUpdate_action.setChecked(update_state)
            self.change_auto_update(update_state)

    def enable_actions_after_config(self):
        """
        Enables a bunch of GUI actions and buttons that are not active when a config file is not loaded.
        """
        self.updateBtn.setEnabled(True)
        self.shareX_action.setEnabled(True)
        self.autoUpdate_action.setEnabled(True)
        self.openPanelConfigAction.setEnabled(True)
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)

    def load_configuration(self, filename):
        """
        Loads a configuration file named filename and replaces the old configuration stored in memory.

        Args:
            filename (str): config file to be opened and used
        """
        #col_setup, locs = self.config_parser(filename)
        config, server, tree, event_name, col_setup, locs = parser.config_parser(filename)
        self.config = config
        self.server = server
        self.tree = tree
        self.event_name = event_name
        self.node_locs = locs

        self.enable_actions_after_config()
        self.update_subplot_config(col_setup)
        self.modify_shared_axes_list()

    def update_subplot_config(self, col_setup):
        """
        Updates the subplot configuration based on the new column setup.

        The canvas, axes, figure, and toolbar are deleted and recreated based on the new column setup.

        Args:
            col_setup (list): list of ints for the number of plots in a column
        """
        if self.figure is not None:
            self.vbox.removeWidget(self.toolbar)
            self.vbox.removeWidget(self.canvas)
            self.figure.clear()
            self.figure = None
            self.toolbar = None
            self.canvas = None

        if self.axs is not None:
            for ax in self.axs:
                ax = None

        self.vbox.removeItem(self.hbox)
        self.vbox.removeItem(self.shot_hbox)

        cols = [x for x in col_setup if x > 0]

        self.figure, self.axs = data_plotter.create_figure(cols)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.vbox.addWidget(self.toolbar, 2)
        self.vbox.addLayout(self.shot_hbox)
        self.vbox.addWidget(self.canvas, 12)
        self.vbox.addLayout(self.hbox)

    @QtCore.pyqtSlot(int)
    def fetch_data(self, shot_number):
        """
        Starts a QThreadPool of Workers (workers.Worker) to fetch data if the tree can be opened.

        Function exits immediately if self.acquiring_data is True

        Next step is to count the number of signals to be fetched.

        Before starting workers, we check to see if the tree can be opened for this shot number.  If not, we call
            self.handle_mdsplus_data with data=None and exit.

        If the tree is available, we start a QThreadPool with instances of Worker for fetching data.  Each Worker
            fetches only one signal.

        Args:
            shot_number (int): Shot number to fetch data from
        """
        if self.acquiring_data:
            # already grabbing data, do nothing
            print('already acquiring')
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
        print(self.n_positions)

        # No data, turn acquring_data off, go back to event loop
        if self.n_positions == 0:
            self.status.setText('Idle')
            self.acquiring_data = False
            return

        logger.debug("Asking if tree is available to be opened")
        tree_available = mdsh.check_open_tree(shot_number, self.server, self.tree)
        print("is the tree available?", tree_available)

        # Can't open tree, set acquiring_data to false, call handle_mdplus_data(None)
        if not tree_available:
            # print('passing None to handle mdsplus data')
            self.acquiring_data = False
            self.handle_mdsplus_data(None)
            logger.warn("tree was unable to be opened. shot = %d" % shot_number)
            return

        # There is data to grab and the tree exists.
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
        """
        Adds returning MDSplus data to its location in the self.data dictionary

        This function is connected to the output of the Workers called in fetch_data.  self.completion is
        counting the number of times this function is called.  If it self.completion equals self.n_positions, all of the
        data has arrived and self.handle_mdsplus_data can be called.

        Args:
            data_tuple (str, str, data.Data): (location of data in dictionary, name of signal, instance of data.Data)
        """
        self.completion += 1

        self.progess_bar.setValue(self.completion / self.n_positions * 100.0)
        # unpack data_tuple
        loc, name, data = data_tuple
        self.data[loc].append(data)
        logger.debug("Retrieving data for %s" % name)
        if self.completion == self.n_positions:
            self.handle_mdsplus_data(self.data)

    def handle_mdsplus_data(self, data):
        """
        Plots data if there is data to be plotted.  Otherwise, plot is cleared and function is exited.

        If data is None, there was an error opening the shot

        If data is an empty dictionary, there wasn't any data in the tree.

        Else, we can plot the data by calling data_plotter.plot_all_data

        Args:
            data (dict): data dictionary with all of the signals to be plotted
        """
        # Finished acquiring data
        self.data = data
        self.acquiring_data = False

        # Clear all the axes
        axs = self.axs
        for axes in axs:
            for ax in axes:
                ax.cla()

        # Check if data was actually passed to this function.  Plot if it is.
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

        # Handle MDSplus shot number being zero
        if self.shot_number == 0:
            current_shot = mdsh.get_current_shot(self.server, self.tree)
            self.shot_number_label.setText("Shot {0:d}".format(current_shot))
        else:
            self.shot_number_label.setText("Shot {0:d}".format(self.shot_number))

        # Redraw GUI elements
        self.spinBox.setValue(self.shot_number)
        self.figure.tight_layout()
        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()
        self.progess_bar.setValue(0.0)

    def change_auto_update(self, state):
        """
        Toggles auto-update functionality with MDSplus events

        Args:
            state (QState): state emitted from action, (not used)
        """
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
        """
        Toggles the share-x axis functionality of the subplots

        Note: only axses listed in self.shared_axs can be shared
        """
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
        """
        Calls self.fetch_data if the shot_number in self.spinBox is different from self.shot_number or
        if self.data is None

        Otherwise, the data is just replotted.
        """
        shot_number = self.spinBox.value()
        if shot_number == self.shot_number and self.data is not None:
            # No change, just replot
            self.handle_mdsplus_data(self.data)
        else:
            print('im trying to fetch data')
            self.shot_number = shot_number
            self.fetch_data(shot_number)

    def save_as_configuration(self):
        """

        Returns:

        """
        self.save_as_dialog = QtWidgets.QFileDialog()
        self.save_as_dialog.fileSelected.connect(self._save_configuration)
        self.save_as_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.save_as_dialog.setNameFilter("Config Files (*.ini *.txt)")
        self.save_as_dialog.exec_()

    def save_configuration(self):
        """

        Returns:

        """
        if self.config_filename:
            self._save_configuration(self.config_filename)
        else:
            self.save_as_configuration()

    def _save_configuration(self, filename):
        """

        Args:
            filename:

        Returns:

        """
        self.config_filename = filename
        config_obj = ConfigObj(indent_type="    ")
        config_obj.filename = self.config_filename
        config_obj.update(self.config)
        config_obj.write()

    def open_change_downsample(self):
        """

        Returns:

        """
        xloc, yloc = self._new_dialog_positions()
        dlg = EditDownsampleDialog(self.downsampling_points, xloc=xloc, yloc=yloc)
        if dlg.exec_():
            self.downsampling_points = dlg.points

            if self.data is not None:
                self.handle_mdsplus_data(self.data)
            else:
                self.fetch_data(self.shot_number)

    def modify_shared_axes_list(self):
        """

        Returns:

        """
        self.shared_axs = []
        for pos in self.node_locs:
            if 'xshare' in self.node_locs[pos] and not strtobool(self.node_locs[pos]['xshare']):
                pass
            else:
                i, j = (int(x) for x in pos)
                self.shared_axs.append(self.axs[j][i])

    @QtCore.pyqtSlot(int)
    def handle_incoming_mds_event(self, shot_number):
        """

        Args:
            shot_number:

        Returns:

        """
        try:
            self.mds_update_event.cancel()
            self.mds_update_event = None
        except mds.mdsExceptions.SsSUCCESS as e:
            print(e)
            logger.error("STUPID MDSPLUS CANCEL ERROR in handle_incoming_mds_event, %s" % e.message)
        self.mds_update_event = MyEvent(self.event_name)
        self.mds_update_event.sender.emitter.connect(self.handle_incoming_mds_event)
        self.fetch_data(shot_number)
