from __future__ import division, print_function
import numpy as np


class Data:

    def __init__(self, name, time, data, color):
        self._time = np.array(time)
        self._data = np.array(data)
        self.name = name
        self.color = color

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, val):
        self._time = np.array(val)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = np.array(val)

    def __repr__(self):
        if self._time is None or self._data is None:
            return self.name + "has no data " + repr(self._time) + " " + repr(self._data)

        return self.name + "\ntime: " + repr(self._time) + " shape:" + str(self.time.shape) + \
            "\ndata: " + repr(self._data) + " shape:" + str(self.data.shape)

    def __str__(self):
        return self.name

    def __bool__(self):
        if len(self) > 1:
            # Note that a ValueError will be raised if the lengths don't match
            return True

        return False

    def __len__(self):
        time_length = len(self._time)
        data_length = len(self._data)

        if time_length == data_length:
            return time_length

        raise ValueError('Time and Data are not the same length')

    def __eq__(self, other):
        if not isinstance(other, Data):
            return False

        try:
            len1 = len(self)
            len2 = len(other)
        except ValueError:
            return False

        if len1 != len2:
            return False

        time_flag = all(x == y for x, y in zip(self._time, other.time))
        data_flag = all(x == y for x, y in zip(self._data, other.data))

        if time_flag and data_flag:
            return True

        return False

