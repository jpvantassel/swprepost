"""This file contains a derived class DispersionCurve for handling a 
dispersion curve object.
"""

import re
from swipp import Curve


class DispersionCurve(Curve):
    """Class for handling a dispersion curve for a particualr 
    velocity model.

    Attributes:
        frequency: List of floats or ints denoting the dispersion 
            curve's frequency values.
        velocity: List of floats or ints denoting the dispersion curve's
            velocity values (one per velocity).
    """

    def __init__(self, frequency, velocity):
        """Initialize a DispersionCurve object, from a set of dispersion
        data.

        Args:
            frequency: List of floats or ints denoting the dispersion 
                curve's frequency values.
            velocity: List of floats or ints denoting the dispersion 
                curve's velocity values (one per velocity).

        Returns:
            Instantiated DispersionCurve object.

        Raises:
            This method raises no exceptions.
        """
        self.check_input(x=frequency, y=velocity, name_y="velocity")
        super().__init__(x=frequency, y=velocity)

    @property
    def frq(self):
        return self._x

    @property
    def vel(self):
        return self._y

    @property
    def wav(self):
        return [v/f for v, f in zip(self._y, self._x)]
