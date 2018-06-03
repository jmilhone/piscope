from __future__ import print_function, division
from MDSplus.event import Event
from PyQt5 import QtCore


class SenderObject(QtCore.QObject):
    """

    """
    emitter = QtCore.pyqtSignal(int)


class MyEvent(Event):
    """

    """
    def __init__(self, event_name):
        """

        Args:
            event_name:
        """
        super(MyEvent, self).__init__(event_name)
        self.sender = SenderObject()

    def run(self):
        """

        Returns:

        """
        print("Event happened!")
        self.sender.emitter.emit(self.getData())

