from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets
from matplotlib import rcParams
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from workers import Worker
from ..data import fetch
import readline
import MDSplus as mds
from ..plotting import gun_plotting
import events


class MyWindow(QtWidgets.QWidget):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Big Red Ball PyScope")
        self.threadpool = QtCore.QThreadPool()  # This is where the grabbing of data will take place to not lock the gui
        self.mdsevent_threadpool = QtCore.QThreadPool()
        # Shot Number Spin Box
        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(0, 999999)
        self.spinBox.setKeyboardTracking(False)
        self.spinBox.setValue(mds.tree.Tree.getCurrent("wipal"))
        self.shot_number = self.spinBox.value()

        self.mds_update_event = events.MyEvent("mag_data_ready")
        self.mds_update_event.sender.emitter.connect(self.fetch_data)

        # Share x axis check box
        #self.shareX = QtWidgets.QCheckBox("Share X-Axis", self)

        # Auto Update Shot Number check box
        #self.autoUpdate = QtWidgets.QCheckBox("Auto Update", self)

        # Update Plot Button
        self.updateBtn = QtWidgets.QPushButton("Update", self)

        # Status Label
        self.status = QtWidgets.QLabel("Idle", self)

        self.font = self.updateBtn.font()
        self.font.setPointSize(18)

        self.status.setFont(self.font)
        self.updateBtn.setFont(self.font)
        self.spinBox.setFont(self.font)

        # Create matplotlib figures here
        #self.figure, self.axs = plt.subplots(3, 3)
        self.figure = plt.figure(0)
        # build figure grid spec
        self.axs = []
        self.axs.append(plt.subplot2grid((6,8), (0, 0), colspan=2, rowspan=2))
        self.axs.append(plt.subplot2grid((6,8), (2, 0), colspan=2, rowspan=2))
        self.axs.append(plt.subplot2grid((6,8), (4, 0), colspan=2, rowspan=2))

        self.axs.append(plt.subplot2grid((6,8), (0, 2), colspan=2, rowspan=3))
        self.axs.append(plt.subplot2grid((6,8), (3, 2), colspan=2, rowspan=3))

        self.axs.append(plt.subplot2grid((6,8), (0, 4), colspan=2, rowspan=3))
        self.axs.append(plt.subplot2grid((6,8), (3, 4), colspan=2, rowspan=3))

        self.axs.append(plt.subplot2grid((6,8), (0, 6), colspan=2, rowspan=3))
        self.axs.append(plt.subplot2grid((6,8), (3, 6), colspan=2, rowspan=3))

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Handle Layout Here
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.spinBox)
        #self.hbox.addWidget(self.shareX)
        #self.hbox.addWidget(self.autoUpdate)
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
        #self.autoUpdate.stateChanged.connect(self.timer_start_stop)

        self.fetch_data(self.shot_number)
        self.show()

    #def timer_start_stop(self, state):
    #    if state == QtCore.Qt.Checked:
    #        self.timer.start()
    #    else:
    #        self.timer.stop()

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
    #        shot_number = mds.Event.wfevent("gun_data_ready", 1)
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
        worker = Worker(fetch.retrieve_gun_data, shot_number, nguns=19, npts=1)
        worker.signals.result.connect(self.handle_mdsplus_data)
        self.threadpool.start(worker)

    def handle_mdsplus_data(self, data):
        self.status.setText("Plotting Data from Shot {0:d}".format(self.shot_number))

        t = data['t']

        Iarc = data['Iarc']
        Varc = data['Varc']

        Ibias = data['Ibias']
        Vbias = data['Vbias']

        Iarc_tot = data['Iarc_tot']
        Ibias_tot = data['Ibias_tot']

        Parc_tot = data['Parc_tot']
        Pbias_tot = data['Pbias_tot']
        valid_guns = data['valid_guns']
        locs = data['locs']

        #t, cathode_current, cathode_voltage, anode_current, total_power, total_cathode_current, total_anode_current = data[0:7]
        #tt, ne, te, vf = data[7:11]
        #t_mm, ne_mm = data[11:13]
        #t_mag, forward, reflected = data[13:16]
        #t_nn, nn = data[16:18]
        axs = self.axs

        # Step 1 clear axes
        for ax in axs:
            ax.cla()
        gun_plotting.plot_total_current(axs[0], t, Ibias_tot, Iarc_tot)
        gun_plotting.plot_total_power(axs[1], t, Pbias_tot, Parc_tot)
        gun_plotting.plot_locs(axs[2], locs, valid_guns)
        gun_plotting.plot_Iarc(axs[3], t, Iarc)
        gun_plotting.plot_Varc(axs[4], t, Varc)
        gun_plotting.plot_Ibias(axs[5], t, Ibias)
        gun_plotting.plot_Vbias(axs[6], t, Vbias)
    
        ## Step 2 plot the data
        #cathode_axs = [axs[2][0], axs[2][1], axs[2][2]]
        #probe_axs = [axs[0][0], axs[1][0], axs[1][1]]
        #discharge_plotting.plot_discharge(cathode_axs, t, cathode_voltage, cathode_current, anode_current)
        #discharge_plotting.plot_probes(probe_axs, tt, ne, te, vf)
        #discharge_plotting.plot_power(axs[0][2], t, total_power, t_mag, forward, reflected)
        #if total_anode_current is not None and total_cathode_current is not None:
        #    discharge_plotting.plot_cathode_hemisphere_currents(axs[1][2], t, cathode_current, [6, 7, 10, 12], [1, 2, 8, 9])
        #    discharge_plotting.plot_total_current(axs[1][2], t, total_cathode_current, total_anode_current)
        #if t_mm is not None and ne_mm is not None:
        #    discharge_plotting.plot_density(axs[0][1], t_mm, ne_mm)
        #if t_nn is not None and nn is not None:
        #    discharge_plotting.plot_neutral_density(axs[0][1], t_nn, nn)
        self.figure.suptitle("Shot {0:d}".format(self.shot_number))
        self.figure.tight_layout()
        # Step 3 draw the canvas
        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()
        self.status.setText("Idle")




