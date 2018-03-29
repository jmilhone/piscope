from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets
from matplotlib import rcParams
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from workers import Worker
from ..data import fetch
#import readline
import MDSplus as mds
from ..plotting import magnetics_plotting as plotting
import events

class MyWindow(QtWidgets.QWidget):

    def __init__(self, hall):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Big Red Ball PyScope")
        self.threadpool = QtCore.QThreadPool()  # This is where the grabbing of data will take place to not lock the gui
        self.mdsevent_threadpool = QtCore.QThreadPool()
        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(0, 999999)
        self.spinBox.setKeyboardTracking(False)
        self.spinBox.setValue(mds.tree.Tree.getCurrent("wipal"))
        self.shot_number = self.spinBox.value()
        self.hall = hall

        self.mds_update_event = None
        #self.mds_update_event = events.MyEvent("mag_data_ready")
        #self.mds_update_event.sender.emitter.connect(self.fetch_data)
        #self.mds_update_event.join()

        # Share x axis check box
        self.shareX = QtWidgets.QCheckBox("Share X-Axis", self)

        # Binned data check box
        self.binned = QtWidgets.QCheckBox("Binned?", self)

        # Auto Update Shot Number check box
        self.autoUpdate = QtWidgets.QCheckBox("Auto Update", self)

        # Update Plot Button
        self.updateBtn = QtWidgets.QPushButton("Update", self)

        # Status Label
        self.status = QtWidgets.QLabel("Idle", self)

        self.font = self.binned.font()
        self.font.setPointSize(18)

        self.spinBox.setFont(self.font)
        self.binned.setFont(self.font)
        self.autoUpdate.setFont(self.font)
        self.updateBtn.setFont(self.font)
        self.status.setFont(self.font)
        self.shareX.setFont(self.font)


        # Create matplotlib figures here
        self.figure, self.axs = plt.subplots(4, 4)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Handle Layout Here
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.spinBox)
        self.hbox.addWidget(self.binned)
        self.hbox.addWidget(self.shareX)
        self.hbox.addWidget(self.autoUpdate)
        self.hbox.addWidget(self.updateBtn)
        self.hbox.addWidget(self.status)
        self.hbox.addStretch(1)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.toolbar, 2)
        self.vbox.addWidget(self.canvas, 12)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

        # Timer for Auto Update from MDSplus Events
        #self.timer = QtCore.QTimer()
        #self.timer.setInterval(200)

        # Set up connections for the widgets
        #self.timer.timeout.connect(self.process_timeout)
        self.updateBtn.clicked.connect(self.update_pressed)
        self.autoUpdate.stateChanged.connect(self.change_auto_update)
        self.binned.stateChanged.connect(self.update_pressed)
        self.shareX.stateChanged.connect(self.change_sharex)

        # This is not needed, but I added it for Vader2
        self.setGeometry(100, 1200, 1200, 1200)
        self.show()

        # run the initial data grab
        self.fetch_data(self.shot_number)

    def change_auto_update(self, state):
        if state == QtCore.Qt.Checked:
            if self.mds_update_event is None:
                self.mds_update_event = events.MyEvent("mag_data_ready")
                self.mds_update_event.sender.emitter.connect(self.fetch_data)
        else:
            if self.mds_update_event is not None and self.mds_update_event.isAlive():
                self.mds_update_event.cancel()
                self.mds_update_event = None

    def change_sharex(self, state):
        axs = self.axs
        ax0 = axs[1][0]
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

    #def timer_start_stop(self, state):
    #    if state == QtCore.Qt.Checked:
    #        self.timer.start()
    #    else:
    #        self.timer.stop()
    #
    #def wait_for_mds_event(self, name, timeout):
    #    try:
    #        #print("starting to wait")
    #        shot_number = mds.Event.wfevent(name, timeout)
    #        return int(shot_number)
    #    except mds.MdsTimeout, e:
    #        #print("timed out")
    #        return None

    #def process_timeout(self):
    #    #worker = Worker(self.wait_for_mds_event, "raw_data_ready", 1)
    #    #worker.signals.result.connect(self.handle_mds_event)
    #    #self.mdsevent_threadpool.start(worker)

    #    try:
    #        shot_number = mds.Event.wfevent("mag_data_ready", 1)
    #        shot_number = int(shot_number)
    #        self.shot_number = shot_number
    #        self.spinBox.setValue(self.shot_number)
    #        self.fetch_data(shot_number)
    #    except mds.MdsTimeout, e:
    #        pass
    #        #print("timed out")
    #        # Moving on, no event yet

    #def handle_mds_event(self, shot_number):
    #    if shot_number:
    #        self.shot_number = shot_number
    #        self.spinBox.setValue(self.shot_number)
    #        self.fetch_data(shot_number)

    def update_pressed(self):
        shot_number = self.spinBox.value()
        self.shot_number = shot_number
        self.fetch_data(shot_number)

    @QtCore.pyqtSlot(int)
    def fetch_data(self, shot_number):
        self.spinBox.setValue(shot_number)
        self.shot_number = shot_number
        self.status.setText("Retrieving Data from Shot {0:d}".format(shot_number))
        worker = Worker(fetch.retrieve_linear_hall, shot_number, self.hall, binned=self.binned.isChecked())
        worker.signals.result.connect(self.handle_mdsplus_data)
        self.threadpool.start(worker)

    def handle_mdsplus_data(self, data):
        # Step 1 clear axes
        axs = self.axs
        for axes in axs:
            for ax in axes:
                ax.cla()

        # Step 2 Plot the data
        plotting.plot_magnetics(axs, data)
        self.figure.suptitle("Shot {0:d}".format(self.shot_number))
        self.figure.tight_layout()

        # Step 3 draw the canvas
        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()
        self.status.setText("Idle")




