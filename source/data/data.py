from __future__ import division, print_function
import numpy as np
"""
Module Data
==============
Defines one class, Data.
You define Data by providing a name, time signal, data signal, and a color
for plotting purposes
"""


class Data:
    """
    Class for holding time series data

    >>> from source.data.data import Data
    >>> import numpy as np
    >>> time = np.linspace(0, 1, 100)
    >>> sig = np.random.random(len(time))
    >>> data_signal = Data('My Signal', time, sig, 'red')
    >>> print(len(data_signal))
    100
    >>> print(bool(data_signal))
    True

    Attributes:
        name (str): Name of the signal

        color (str): Color of signal when plotted
    """

    def __init__(self, name, time, data, color):
        """
        Args:
            name (str): Name of signal
            time (iterable): time signal
            data (iterable): data signal
            color (str): color to plot with
        """
        self._time = np.array(time)
        self._data = np.array(data)
        self.name = name
        self.color = color

    @property
    def time(self):
        """np.ndarray: time array"""
        return self._time

    @time.setter
    def time(self, val):
        self._time = np.array(val)

    @property
    def data(self):
        """np.ndarray: data array"""
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

