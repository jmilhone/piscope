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
from ..plotting import mach_plotting
import events



class MyWindow(QtWidgets.QWidget):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Mach Probe PyScope")
        self.threadpool = QtCore.QThreadPool()  # This is where the grabbing of data will take place to not lock the gui
        # self.mdsevent_threadpool = QtCore.QThreadPool()
        # Shot Number Spin Box
        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(0, 999999)
        self.spinBox.setKeyboardTracking(False)
        self.spinBox.setValue(mds.tree.Tree.getCurrent("wipal"))
        self.shot_number = self.spinBox.value()
        
        self.mds_update_event = None
        #self.mds_update_event = events.MyEvent("mach_data_ready")
        #self.mds_update_event.sender.emitter.connect(self.fetch_data)

        # Share x axis check box
        self.shareX = QtWidgets.QCheckBox("Share X-Axis", self)

        # Auto Update Shot Number check box
        self.autoUpdate = QtWidgets.QCheckBox("Auto Update", self)

        # Update Plot Button
        self.updateBtn = QtWidgets.QPushButton("Update", self)

        # Status Label
        self.status = QtWidgets.QLabel("Idle", self)

        self.font = self.spinBox.font()
        self.font.setPointSize(18)
        
        self.spinBox.setFont(self.font)
        self.updateBtn.setFont(self.font)
        self.status.setFont(self.font)
        self.shareX.setFont(self.font)
        self.autoUpdate.setFont(self.font)

        # Create matplotlib figures here
        self.figure, self.axs = plt.subplots(5, 3)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Handle Layout Here
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.spinBox)
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
        #self.timer.timeout.connect(self.process_timeout)

        self.updateBtn.clicked.connect(self.update_pressed)
        self.autoUpdate.stateChanged.connect(self.change_auto_update)
        self.shareX.stateChanged.connect(self.change_sharex)

        self.fetch_data(self.shot_number)
        self.show()

    def change_auto_update(self, state):
        if state == QtCore.Qt.Checked:
            if self.mds_update_event is None:
                self.mds_update_event = events.MyEvent("mach_data_ready")
                self.mds_update_event.sender.emitter.connect(self.fetch_data)
        else:
            if self.mds_update_event is not None and self.mds_update_event.isAlive():
                self.mds_update_event.cancel()
                self.mds_update_event = None

    def change_sharex(self, state):
        axs = self.axs
        ax0 = axs[0][0]
        if state == QtCore.Qt.Checked:
            for ax in axs:
                for a in ax:
                    if True:#a != axs[0][0]:
                        a.get_shared_x_axes().join(a, ax0)
        else:
            for ax in axs:
                for a in ax:
                    if True:#a != axs[0][0]:
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
    #        shot_number = mds.Event.wfevent("mach_data_ready", 1)
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
        worker = Worker(fetch.retrieve_mach_data, shot_number, n_probes=5, npts=10)
        worker.signals.result.connect(self.handle_mdsplus_data)
        self.threadpool.start(worker)

    def handle_mdsplus_data(self, data):
        # SO SO TERRIBLE!
        # self.status.setText("Plotting Data from Shot {0:d}".format(self.shot_number))
        # t, cathode_current, cathode_voltage, anode_current, total_power, total_cathode_current, total_anode_current = data[0:7]
        # tt, ne, te, vf = data[7:11]
        # t_mm, ne_mm = data[11:13]
        t, mp1_mach, mp2_mach, mp1_A, mp1_B, mp2_A, mp2_B = data

        axs = self.axs

        # Step 1 clear axes
        for axes in axs:
            for ax in axes:
                ax.cla()

        # Step 2 plot the data
        # cathode_axs = [axs[2][0], axs[2][1], axs[2][2]]
        # probe_axs = [axs[0][0], axs[1][0], axs[1][1]]
        # discharge_plotting.plot_discharge(cathode_axs, t, cathode_voltage, cathode_current, anode_current)
        # discharge_plotting.plot_probes(probe_axs, tt, ne, te, vf)
        # discharge_plotting.plot_power(axs[0][2], t, total_power)
        # discharge_plotting.plot_total_current(axs[1][2], t, total_cathode_current, total_anode_current)
        # if t_mm is not None and ne_mm is not None:
        #     discharge_plotting.plot_density(axs[0][1], t_mm, ne_mm)
        mach_axs = [ax[2] for ax in axs]
        mach_plotting.plot_mach_number(mach_axs, t, mp1_mach, mp2_mach)

        mp1_axs = [ax[0] for ax in axs]
        mp2_axs = [ax[1] for ax in axs]

        mach_plotting.plot_currents(mp1_axs, t, mp1_A, mp1_B)
        mach_plotting.plot_currents(mp2_axs, t, mp2_A, mp2_B)

        self.figure.suptitle("Shot {0:d}".format(self.shot_number))
        #self.figure.tight_layout()
        # Step 3 draw the canvas
        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()
        self.status.setText("Idle")




