# This file is part of swprepost, a Python package for surface-wave
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

"""The Curve class definition."""

import numpy as np
import scipy.interpolate as sp


class Curve():
    """Base class for handling sets of x, y coordinates.

    Attributes
    ----------
    _x : ndarray
        1D array of x coordinates defining the curve. These
        should, in general, not be accessed directly.
    _y : ndarray
        Same as `_x` but for the y coordiantes of the curve.

    """

    @staticmethod
    def check_types(x, y):
        """Check type of x and y

        Specifically:
            1. Cast x and y to `ndarray` of type `double`.
            2. Check x and y have the same length.

        """
        try:
            x = np.array(x, dtype=np.double)
            y = np.array(y, dtype=np.double)
        except ValueError:
            msg = f"x and y must be numeric."
            raise TypeError(msg)

        if x.size != y.size:
            msg = f"""x and y must be the same size, currently {x.size} and {y.size}, respectively."""
            raise IndexError(msg)
        return (x, y)

    @staticmethod
    def check_values(x, y, check_fxn):
        """Apply custom checking function on the values of `x` and `y`.

        Parameters
        ----------
        x, y : iterable
            x and y value of curve respectively.
        check_fxn : function
            Function that takes an x, y pair, checks if they are
            valid. If they are valid the function returns `None`
            otherwise raises a `ValueError`.

        Returns
        -------
        None
            If `x` and `y` pass

        Raises
        ------    
        ValueError
            If `x` and `y` fail.

        """
        if check_fxn is not None:
            for _x, _y in zip(x, y):
                check_fxn(_x, _y)

    @classmethod
    def check_input(cls, x, y, check_fxn=None):
        """Check inputs comply with the required formatting."""
        x, y = cls.check_types(x, y)
        cls.check_values(x, y, check_fxn)
        return (x, y)

    def __init__(self, x, y, check_fxn=None):
        """Initialize a curve object from x, y coordinates.

        Parameters
        ----------
        x, y : iterable
            Iterables of the same size defining the curve's x and y
            coordinates.
        check_fxn : function, optional
            Function that takes an x, y pair, and checks if they are
            valid.

            If they are valid the function returns `None`
            otherwise raises a `ValueError`, default is `None`
            meaning no function is used to check the `x` and `y` values.

        Returns
        -------
        Curve
            Instantiated `Curve` object.

        Raises
        ------
        IndexError
            If `x` and `y` do not have the same length.
        ValueError
            If `check_fxn` is defined and any `x`, `y` pair fails to
            meet the defined criteria.

        """
        x, y = self.check_input(x, y, check_fxn)
        self._x = x
        self._y = y

    @classmethod
    def resample_function(cls, x, y, **kwargs):
        """Wrapper for `interp1d` from `scipy`."""
        return sp.interp1d(x, y, **kwargs)

    def resample(self, xx, inplace=False, interp1d_kwargs=None, res_fxn=None):
        """Resample Curve at select x values.

        Parameters
        ----------
        xx : ndarray
            1D array containing the locations in terms of x, of the
            desired interpolated y values.
        inplace : bool, optional
            Indicates whether resampling should be done in-place.
            If inplace the, attributes `_x` and `_y` are
            overwritten. Otherwise the new values are returned,
            default is `False` resampling is not done inplace.
        interp1d_settings : dict, optional
            Settings for use with the `interp1d` function from `scipy`.
            See documentation `here
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_
            for details.
        res_fxn : function, optional
            Define a custom resampling function. It should accept an
            ndarray of resampling x-coordinates and return the
            interpolated y-coordinates as an ndarray.

        Returns
        -------
        None or (xx, yy)
            `None`, if `inplace=True`; `_x` and `_y` will be updated.
            `(xx, yy)` if `inplace=False`.

        """
        xx = np.array(xx, dtype=np.double)

        if res_fxn is None:
            if interp1d_kwargs is None:
                interp1d_kwargs = {"kind": "cubic"}
            res_fxn = self.resample_function(self._x,
                                             self._y,
                                             **interp1d_kwargs)
        yy = res_fxn(xx)

        if inplace:
            self._x, self._y = xx, yy
        else:
            return (xx, yy)

    def __eq__(self, other):
        """Compare whether two curve objects are equal."""
        if not isinstance(other, Curve):
            return False

        for attr in ["_x", "_y"]:
            my = getattr(self, attr)
            ur = getattr(other, attr)

            if my.size != ur.size:
                return False

            if not np.allclose(my, ur):
                return False

        return True

    def __repr__(self):
        """Unambiguous representation of a `Curve` object."""
        return f"Curve(x={self._x}, y={self._y})"

    def __str__(self):
        """Human-readable representation of a `Curve` object."""
        return f"Curve with {self._x.size} points."