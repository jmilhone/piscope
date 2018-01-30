from __future__ import division, print_function
from PyQt5 import QtCore, QtWidgets
from matplotlib import rcParams
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from workers import Worker
from ..data import fetch
import MDSplus as mds
from ..plotting import discharge_plotting

rcParams['xtick.direction'] = 'in'
rcParams['ytick.direction'] = 'in'


class MyWindow(QtWidgets.QWidget):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Big Red Ball PyScope")
        self.threadpool = QtCore.QThreadPool()  # This is where the grabbing of data will take place to not lock the gui

        # Shot Number Spin Box
        self.spinBox = QtWidgets.QSpinBox(self)
        self.spinBox.setRange(0, 999999)
        self.spinBox.setKeyboardTracking(False)
        self.spinBox.setValue(mds.tree.Tree.getCurrent("wipal"))
        self.shot_number = self.spinBox.value()

        # Share x axis check box
        self.shareX = QtWidgets.QCheckBox("Share X-Axis", self)

        # Auto Update Shot Number check box
        self.autoUpdate = QtWidgets.QCheckBox("Auto Update", self)

        # Update Plot Button
        self.updateBtn = QtWidgets.QPushButton("Update", self)

        # Status Label
        self.status = QtWidgets.QLabel("Idle", self)

        # Create matplotlib figures here
        self.figure, self.axs = plt.subplots(3, 3)
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
        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.process_timeout)

        self.updateBtn.clicked.connect(self.update_pressed)
        self.autoUpdate.stateChanged.connect(self.timer_start_stop)

        self.axs[0][0].plot([0, 1, 2], [1, -1, 3], '-or')
        self.canvas.draw()

        self.show()

    def timer_start_stop(self, state):
        if state == QtCore.Qt.Checked:
            self.timer.start()
        else:
            self.timer.stop()

    def process_timeout(self):
        try:
            shot_number = mds.Event.wfevent("raw_data_ready", 1)
            shot_number = int(shot_number)
            self.fetch_data(shot_number)
        except mds.MdsTimeout, e:
            # Moving on, no event yet
            pass

    def update_pressed(self):
        shot_number = self.spinBox.value()
        self.fetch_data(shot_number)

    def fetch_data(self, shot_number):
        self.status.setText("Processing Shot {0:d}".format(shot_number))
        worker = Worker(fetch.retrieve_all_data, shot_number, n_anodes=20, n_cathodes=12, npts=100)
        worker.signals.result.connect(self.handle_mdsplus_data)
        self.threadpool.start(worker)

    def handle_mdsplus_data(self, data):
        t, cathode_current, cathode_voltage, anode_current = data
        print(t.shape)
        print(cathode_current.keys())
        axs = self.axs

        # Step 1 clear axes
        for axes in axs:
            for ax in axes:
                ax.cla()

        # Step 2 plot the data
        cathode_axs = [axs[2][0], axs[2][1], axs[2][2]]
        discharge_plotting.plot_discharge(cathode_axs, t, cathode_voltage, cathode_current, anode_current)
        self.figure.suptitle("Shot {0:d}".format(self.shot_number))
        self.figure.tight_layout()
        # Step 3 draw the canvas
        self.canvas.draw()
        self.status.setText("Idle")





