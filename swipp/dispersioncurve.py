"""This file contains the class `DispersionCurve`."""

from swipp import Curve, regex
import numpy as np


class DispersionCurve(Curve):
    """Class to define a dispersion curve.

    Attributes:
        frequency, velocity : ndarray
            Vector of the dispersion curve's frequency and velocity
            values, respectively.
    """

    def __init__(self, frequency, velocity):
        """Initialize a `DispersionCurve` object, from dispersion data.

        Args:
            frequency, velocity : ndarray
                Vector of the dispersion curve's frequency and velocity
                values, respectively.

        Returns:
            Initialized `DispersionCurve` object.
        """
        frequency, velocity = self.check_input(x=frequency, y=velocity)
        super().__init__(x=frequency, y=velocity)

    @property
    def frequency(self):
        return self._x

    @property
    def velocity(self):
        return self._y

    @property
    def wavelength(self):
        return self._y/self._x

    @property
    def slowness(self):
        return 1/self._y

    @classmethod
    def _parse_dc(cls, dc_data):
        """Parse a `DispersionCurve` from a `str` of data."""
        frequency, slowness = [], []
        for curve in regex.data.finditer(dc_data):
            f, p = curve.groups()
            f = float(f)
            try:
                if f < frequency[-1]:
                    break
                else:
                    frequency.append(f)
                    slowness.append(float(p))
            except IndexError:
                frequency.append(f)
                slowness.append(float(p))

        return cls(frequency=frequency, velocity=1/np.array(slowness, dtype=np.double))

    @classmethod
    def from_geopsy(cls, fname):
        """Instantiate a `DispersionCurve` from a text file in the
        geopsy format.

        Args:
            fname : str
                Name of file to be read, may be a relative or full path.

        Returns:
            Instantiated `DispersionCurve` object.
        """
        with open(fname, "r") as f:
            lines = f.read()
        return cls._parse_dc(lines)

    def __eq__(self, other):
        attrs = ["frequency", "velocity"]
        for attr in attrs:
            my_vals = getattr(self, attr)
            ur_vals = getattr(other, attr)
            if len(my_vals) != len(ur_vals):
                return False
            for my, ur in zip(my_vals, ur_vals):
                if my != ur:
                    return False
        return True

    def __repr__(self):
        return f"DispersionCurve(frequency={self.frequency}, velocity={self.velocity})"
