"""This file contains a class `Curve` for handling x, y coordinates."""

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
        Same as `_x`
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
            msg = f"""Abscissa and ordinate must be the same size,
                      currently {x.size} and {y.size}, respectively."""
            raise IndexError(msg)
        return (x, y)

    @staticmethod
    def check_values(x, y, check_fxn):
        """Use custom checking function to check the values of `x` and
        `y`.
        
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
        """Intialize a curve object from x, y coordinates.

        Parameters
        ----------
        x, y : iterable
            Iterables of the same size defining the curve's x and y
            coordinates.
        check_fxn : function, optional
            Function that takes an x, y pair, checks if they are
            valid.
            
            If they are valid the function returns `None`
            otherwise raises a `ValueError`, default is `None`
            meaning no function is used to check the x and y values.

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

    def resample(self, xx, inplace=False, res_fxn=None):
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
        res_fxn : function, optional
            Custom resampling function, default is `None` indicating
            the default resampling function is used. Custom
            resampling functions can be created using the :meth: 
            `resampling_function <Curve.resample_function>`.

        Returns
        -------
        None or (xx, yy)
            `None`, if `inplace=True`; `_x` and `_y` will be updated.
            `(xx,yy)` if `inplace=False`.
        """
        # Perform resample
        if res_fxn is None:
            res_fxn = self.resample_function(self._x,
                                            self._y,
                                            kind="cubic")
        yy = res_fxn(xx)

        # Update attributes or return values.
        if inplace:
            self._x = xx
            self._y = yy
        else:
            return (xx, yy)
