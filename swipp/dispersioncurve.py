"""This file contains the class `DispersionCurve` which inherits from
`Curve`."""

import re
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
    def _from_lines(cls, lines):
        """Create an instance of `DispersionCurve` from a list of
        strings which follow the geopsy format.

        Args:
            lines : list(str)
                List of strings, one per line, following the syntax of
                a geopy output file.

        Returns:
            Instantiated `DispersionSet` object.
        """
        frequency, slowness, seen_data = [], [], False
        for line in lines:
            try:
                f, p = regex.data.findall(line)[0]
                seen_data=True
                frequency.append(f)
                slowness.append(p)
            except IndexError:
                if seen_data:
                    break
                else:
                    continue

        return cls(frequency=frequency, velocity=1/np.array(slowness, dtype=np.double))
                
    @classmethod
    def from_geopsy(cls, fname):
        """Instantiate a `DispersionCurve` object from a text file in
        the geopsy format.
        
        Args:
            fname : str
                Name of file to be read, may be a relative or full path.

        Returns:
            Instantiated `DispersionCurve` object.
        """
        with open(fname, "r") as f:
            lines = f.read().splitlines()
        return cls._from_lines(lines)

    def __repr__(self):
        return f"DispersionCurve(frequency={self.frequency}, velocity={self.velocity})"
