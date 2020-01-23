"""This file contains a base class Curve for handling x, y coordinates."""

import numpy as np
import scipy.interpolate as sp


class Curve():
    """Base class for handling sets x, y coordinates.

    Attributes:
        _x, _y = ndarray
            1D array of x, y coordinates defining the curve. These
            should, in general, not be accessed directly.
    """

    @staticmethod
    def check_types(x, y):
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
        
        Args:
            x, y : iterable
                Iterables of the same size definin the curve's x and y
                coordinates.
            check_fxn : function, optional
                Function that takes an x, y pair, checks if they are
                valid. If they are valid the function returns otherwise
                raises a `ValueError`, default is `None` meaning no
                function is used to check the x and y values.

                def checker(x, y):
                    if x < 0 or y < 0:
                        msg = 'x and y must be greater than 0.'
                        raise ValueError(msg)
        
        Returns:
            Instantiated `Curve` object.

        Raises:
            IndexError:
                If x and y do not have the same length.
            ValueError:
                If `check_fxn` is defined and any x, y pair fails to
                meet the defined criteria.
        """
        x, y = self.check_input(x, y, check_fxn)
        self._x = x
        self._y = y

    @classmethod
    def resample_function(cls, x, y, **kwargs):
        """Class method serving as a wrapper for interp1d from scipy."""
        return sp.interp1d(x, y, **kwargs)

    def resample(self, xx, inplace=False, res_fxn=None):
        """Resample Curve at select x values.

        Args:
            xx : {ndarray, None}
                1D array containing the locations in terms of x, of the
                desired interpolated y values.
            inplace : bool, optional
                Indicates whether resampling should be done in-place.
                If inplace the, attributes x and y are overwritten,
                otherwise the new values are returned, default is
                `False` resampling is not done inplace.
            res_fxn : func, optional
                Custom resampling function, default is `None` indicating
                the default resampling function is used.

        Returns:
            If `inplace=True`:
                `None`, instead update attributes `_x` and `_y`.
            If `inplace=False`:
                Resampled `x` and `y` as `(xx, yy)`.
        """
        # Perform resample
        res_fxn = self.resample_function(x, y, kind="cubic") if res_fxn is None else res_fxn
        yy = res_fxn(xx)

        # Update attributes or return values.
        if inplace:
            self._x = xx
            self._y = yy
        else:
            return (xx, yy)
