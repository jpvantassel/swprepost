# This file is part of swipp, a Python package for surface-wave
# inversion pre- and post-processing.
# Copyright (C) 2019-2020 Joseph P. Vantassel (jvantassel@utexas.edu)
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https: //www.gnu.org/licenses/>.

"""The DispersionCurve class definition."""

from swipp import Curve, regex
import numpy as np


class DispersionCurve(Curve):
    """Class to define a `DispersionCurve` object.

    Attributes
    ----------
    frequency, velocity : ndarray
        1D array of the dispersion curve's frequency and velocity
        values, respectively.

    """

    def __init__(self, frequency, velocity):
        """Initialize a `DispersionCurve` object from dispersion data.

        Parameters
        ----------
        frequency, velocity : iterable
            Vector of the dispersion curve's frequency and velocity
            values, respectively.

        Returns
        -------
        DispersionCurve
            Initialized `DispersionCurve` object.
        """
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
        """Parse a single `DispersionCurve` from dispersion data.
        
        Parameters
        ----------
        dc_data : str
            Dispersion curve data of the form `frequency, slowness`.
            It is assumed that frequencies increases monitonically. If
            this assumption is not true, incorrect results may result.
            See example below.

        Returns
        -------
        DispersionCurve
            Instantiated `DispersionCurve` object.

        Example
        -------
        If `dc_data` is as follows:
            Line 1: # Frequency, Slowness
            Line 2: 0.1, 0.01
            Line 3: 0.2, 0.012
            Line 4: # Frequency, Slowness
            Line 5: 0.1, 0.011
            Line 6: 0.2, 0.013
        Only lines 2 and 3 will be parsed.

        """
        frequency, slowness = [], []
        for curve in regex.dc_data.finditer(dc_data):
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
        return cls(frequency=frequency, velocity=1/np.array(slowness,
                                                            dtype=np.double))

    @classmethod
    def from_geopsy(cls, fname):
        """Create `DispersionCurve` from text file in the Geopsy format.

        Parameters
        ----------
        fname : str
            Name of file to be read, may be a relative or full path.

        Returns
        -------
        DispersionCurve
            Instantiated `DispersionCurve` object.

        """
        with open(fname, "r") as f:
            lines = f.read()
        return cls._parse_dc(lines)

    def __eq__(self, other):
        """Check if the current and `other` object are equal."""
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
        """Unambiguous representation of a `DispersionCurve` object."""
        return f"DispersionCurve(frequency={self.frequency}, velocity={self.velocity})"

    def __str__(self):
        """Readable representation of a `DispersionCurve` object."""
        return f"DispersionCurve with {len(self.frequency)} points"