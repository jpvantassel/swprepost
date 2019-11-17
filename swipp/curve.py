"""This file contains an abstract base class Curve for which specific
instances are derived.
"""

import copy

class Curve():

    @classmethod
    def check_types(cls, x, y, name_x="velocity", name_y="frequency"):
        if (type(x) != list) or (type(y) != list):
            raise TypeError(
                f"'{name_x}' and '{name_y}' must be of type list, not {type(x)} and {type(y)}.")
        if len(x) != len(y):
            raise IndexError(
                f"'{name_x}' and '{name_y}' must be of the same length, currently 'len(x)={len(x)}' and 'len(y)={len(y)}', respectively.")
        for val in x+y:
            if type(val) not in [int, float]:
                raise TypeError(
                    f"'{name_x}' and '{name_y}' must be lists of floats or ints, not {type(val)}.")

    @classmethod
    def check_values(cls, x, y, name_x="frequency", name_y="velocity"):
        for val in x+y:
            if val <= 0:
                raise ValueError(
                    f"'{name_x}' and '{name_y}' must be >= 0, bad value={val}.")

    @classmethod
    def check_input(cls, x, y, name_x="frequency", name_y="velocity"):
        """Check inputs comply with the required formatting."""
        cls.check_types(x, y, name_x, name_y)
        cls.check_values(x, y, name_x, name_y)

    def __init__(self, x, y):
        """Intialize a curve object."""
        self._x = copy.deepcopy(x)
        self._y = copy.deepcopy(y)

    def resample(self, min, max, npts):
        pass
