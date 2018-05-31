from __future__ import division, print_function
from collections.abc import Iterable


class Data:
    def __init__(self, name, time, data, color):
        self._time = Data.iterable_validator(time, 'time')
        self._data = Data.iterable_validator(data, 'data')
        self.name = name
        self.color = color

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, val):
        if isinstance(val, Iterable):
            self._time = val
        else:
            raise ValueError('Time value must be an iterable')

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        if isinstance(val, Iterable):
            self._data = val
        else:
            raise ValueError('Data value must be an iterable')

    def __repr__(self):
        if self._time is None or self._data is None:
            return self.name + "has no data " + repr(self._time) + " " + repr(self._data)

        return self.name + "\ntime: " + repr(self._time) + " shape:" + str(self.time.shape) + \
            "\ndata: " + repr(self._data) + " shape:" + str(self.data.shape)

    def __str__(self):
        return self.name

    def __bool__(self):
        time_flag = isinstance(self._time, Iterable) and len(self._time) > 1
        data_flag = isinstance(self._data, Iterable) and len(self._data) > 1

        if time_flag and data_flag:
            return True

        return False

        # if self._time is not None and self._data is not None:
        #     return True
        # else:
        #     return False

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

        time_flag = all(x == y for x,y in zip(self._time, other.time))
        data_flag = all(x == y for x,y in zip(self._data, other.data))

        if time_flag and data_flag:
            return True

        return False

    @staticmethod
    def iterable_validator(val, name):
        if isinstance(val, Iterable):
            return val
        raise ValueError(f'{name} is not iterable')
