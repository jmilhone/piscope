from __future__ import division, print_function


class Data:
    def __init__(self, name, time, data, color):
        self._time = time
        self._data = data
        self.name = name
        self.color = color

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, val):
        self._time = val

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = val

    def __repr__(self):
        if self._time is None or self._data is None:
            return self.name + "has no data " + repr(self._time) + " " + repr(self._data)

        return self.name + "\ntime: " + repr(self._time) + " shape:" + str(self.time.shape) + \
            "\ndata: " + repr(self._data) + " shape:" + str(self.data.shape)

    def __str__(self):
        return self.name

    def __bool__(self):
        if self._time is not None and self._data is not None:
            return True
        else:
            return False


