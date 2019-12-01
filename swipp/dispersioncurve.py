"""This file contains a derived class DispersionCurve."""

import re
from swipp import Curve
import numpy as np


class DispersionCurve(Curve):
    """Class for a dispersion curve from a particualr velocity model.

    Attributes:
        frequency : ndarray
            Vector of the dispersion curve's frequency values.
        velocity : ndarray
            Vector of the dispersion curve's velocity values, one per
            frequency.
    """

    def __init__(self, frequency, velocity):
        """Initialize a `DispersionCurve` object, from dispersion data.

        Args:
            frequency : ndarray
                Vector of the dispersion curve's frequency values.
            velocity : ndarray
                Vector of the dispersion curve's velocity values, one
                per velocity.

        Returns:
            Initialized `DispersionCurve` object.
        """
        frequency, velocity = self.check_input(x=frequency, y=velocity)
        super().__init__(x=frequency, y=velocity)

    @property
    def frq(self):
        return self._x

    @property
    def vel(self):
        return self._y

    @property
    def wav(self):
        return self._y/self._x
    
    @property
    def slo(self):
        return 1/self._y
