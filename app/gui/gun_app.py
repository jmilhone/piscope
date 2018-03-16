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

        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(0, 999999)
        self.spinBox.setKeyboardTracking(False)
        self.spinBox.setValue(mds.tree.Tree.getCurrent("wipal"))
        self.shot_number = self.spinBox.value()

        self.mds_update_event = None

        # Share x axis check box
        self.shareX = QtWidgets.QCheckBox("Share X-Axis", self)

        # Auto Update Shot Number check box
        self.autoUpdate = QtWidgets.QCheckBox("Auto Update", self)

        # Update Plot Button
        self.updateBtn = QtWidgets.QPushButton("Update", self)

        # Status Label
        self.status = QtWidgets.QLabel("Idle", self)

        # Change font size here
        self.font = self.updateBtn.font()
        self.font.setPointSize(18)

        self.status.setFont(self.font)
        self.updateBtn.setFont(self.font)
        self.spinBox.setFont(self.font)
        self.autoUpdate.setFont(self.font)
        self.shareX.setFont(self.font)

        # Create Matplotlib Stuff here
        self.figure, self.axs = plt.subplots(3, 4)
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

        self.updateBtn.clicked.connect(self.update_pressed)
        self.autoUpdate.stateChanged.connect(self.change_auto_update)
        self.shareX.stateChanged.connect(self.change_sharex)
        self.fetch_data(self.shot_number)
        self.show()

    def change_auto_update(self, state):
        if state == QtCore.Qt.Checked:
            if self.mds_update_event is None:
                self.mds_update_event = events.MyEvent("gun_data_ready")
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
                    if a != axs[2][0]:
                        a.get_shared_x_axes().join(a, ax0)
        else:
            for ax in axs:
                for a in ax:
                    if a != axs[2][0]:
                        ax0.get_shared_x_axes().remove(a)

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
        spiral_data = data['spiral_probe']

        axs = self.axs
        # Step 1 clear axes
        for ax in axs:
            for a in ax:
                a.cla()

        # Step 2 plot
        gun_plotting.plot_total_current(axs[0][0], t, Ibias_tot, Iarc_tot)
        gun_plotting.plot_total_power(axs[1][0], t, Pbias_tot, Parc_tot)
        gun_plotting.plot_locs(axs[2][0], locs, valid_guns)
        gun_plotting.plot_Iarc(axs[0][1], t, Iarc)
        gun_plotting.plot_Varc(axs[1][1], t, Varc)
        gun_plotting.plot_Ibias(axs[0][2], t, Ibias)
        gun_plotting.plot_Vbias(axs[1][2], t, Vbias)
        gun_plotting.plot_bdot([axs[0][3], axs[1][3], axs[2][3]], spiral_data)
        gun_plotting.plot_isat(axs[2][2], spiral_data)
        # old way
        #gun_plotting.plot_total_current(axs[0], t, Ibias_tot, Iarc_tot)
        #gun_plotting.plot_total_power(axs[1], t, Pbias_tot, Parc_tot)
        #gun_plotting.plot_locs(axs[2], locs, valid_guns)
        #gun_plotting.plot_Iarc(axs[3], t, Iarc)
        #gun_plotting.plot_Varc(axs[4], t, Varc)
        #gun_plotting.plot_Ibias(axs[5], t, Ibias)
        #gun_plotting.plot_Vbias(axs[6], t, Vbias)
        self.figure.suptitle("Shot {0:d}".format(self.shot_number))
        self.figure.tight_layout()

        # Step 3 draw the canvas
        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()
        self.status.setText("Idle")




