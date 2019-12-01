"""This file contains an abstract base class Curve."""

import copy
import numpy as np


class Curve():

    @staticmethod
    def check_types(x, y, name_x="velocity", name_y="frequency"):

        for value, name in zip([x, y], [name_x, name_y]):
            if type(value) not in [np.ndarray, list, tuple]:
                msg = f"'{name}' must be an `ndarray`, not {type(value)}."
                raise TypeError(msg)
        
        # TODO (jpv): Find a cleaner way to perform type conversion.
        if type(x) in [list, tuple]:
            x = np.array(x)
        if type(y) in [list, tuple]:
            y = np.array(y)

        if x.size != y.size:
            msg = f"'{name_x}' and '{name_y}' must be the same size, currently {x.size} and {y.size}, respectively."
            raise IndexError(msg)

        return (x, y)

    @staticmethod
    def check_values(x, y, name_x="frequency", name_y="velocity"):
        for par in [x, y]:
            for val in par:
                if val <= 0:
                    msg = f"`{name_x}` and `{name_y}` must be >= 0, bad value={val}."
                    raise ValueError(msg)

    @classmethod
    def check_input(cls, x, y, name_x="frequency", name_y="velocity"):
        """Check inputs comply with the required formatting."""
        x, y = cls.check_types(x, y, name_x, name_y)
        cls.check_values(x, y, name_x, name_y)
        return (x,y)

    def __init__(self, x, y):
        """Intialize a curve object."""
        self._x = copy.deepcopy(x)
        self._y = copy.deepcopy(y)

    # TODO (jpv): Relocate resample.
    def resample(self, min, max, npts):
        pass
