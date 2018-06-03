import re
from PyQt5 import QtWidgets, QtGui
import numpy as np

# Regular expression to find floats. Match groups are the whole string, the
# whole coefficient, the decimal part of the coefficient, and the exponent
# part.
_float_re = re.compile(r'(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)')


def valid_float_string(string):
    """

    Args:
        string:

    Returns:

    """
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


class FloatValidator(QtGui.QValidator):
    """

    """

    def validate(self, string, position):
        """

        Args:
            string:
            position:

        Returns:

        """
        if valid_float_string(string):
            state = QtGui.QValidator.Acceptable
        elif string == "" or string[position-1] in 'e.-+':
            state = QtGui.QValidator.Intermediate
        else:
            state = QtGui.QValidator.Invalid
        return (state, string, position)

    def fixup(self, text):
        """

        Args:
            text:

        Returns:

        """
        match = _float_re.search(text)
        return match.groups()[0] if match else ""


class ScientificDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    """

    """

    def __init__(self, *args, **kwargs):
        """

        Args:
            *args:
            **kwargs:
        """
        super(ScientificDoubleSpinBox, self).__init__(*args, **kwargs)
        self.setMinimum(-np.inf)
        self.setMaximum(np.inf)
        self.validator = FloatValidator()
        self.setDecimals(1000)

    def validate(self, text, position):
        """

        Args:
            text:
            position:

        Returns:

        """
        return self.validator.validate(text, position)

    def fixup(self, text):
        """

        Args:
            text:

        Returns:

        """
        return self.validator.fixup(text)

    def valueFromText(self, text):
        """

        Args:
            text:

        Returns:

        """
        return float(text)

    def textFromValue(self, value):
        """

        Args:
            value:

        Returns:

        """
        return format_float(value)

    def stepBy(self, steps):
        """

        Args:
            steps:

        Returns:

        """
        text = self.cleanText()
        groups = _float_re.search(text).groups()
        decimal = float(groups[1])
        decimal += steps
        new_string = "{:g}".format(decimal) + (groups[3] if groups[3] else "")
        self.lineEdit().setText(new_string)


def format_float(value):
    """

    Args:
        value:

    Returns:

    """
    """Modified form of the 'g' format specifier."""
    string = "{:g}".format(value).replace("e+", "e")
    string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
    return string
