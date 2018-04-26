from __future__ import print_function, division
#import readline
from MDSplus import Event
from PyQt5 import QtCore

class SenderObject(QtCore.QObject):
    emitter = QtCore.pyqtSignal(int)

class MyEvent(Event):
    def __init__(self, event):
        super(MyEvent, self).__init__(event)
        self.sender = SenderObject()

    def run(self):
        print("Event happened!")
        self.sender.emitter.emit(self.getData())

#e=MyEvent("twf")
#e.join()
