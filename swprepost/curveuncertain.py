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

"""Definition of CurveUncertain."""

import numpy as np

from swprepost import Curve


class CurveUncertain(Curve):
    """Curve object with arbitrary uncertainty in terms of x and y.

    Attributes
    ----------
    _isxerr, _isyerr : bool
        Flags to indicate if x and y error has been provided.
    _xerr, _yerr : ndarray
        Vector defining the error in x and y respectively.

    """

    @staticmethod
    def _check_error(error, npts):
        """Check error is compatable, specifically:

            1. Can be cast to a ndarray.
            2. Error has same length of the curve.

        """
        error = np.array(error, dtype=np.double)

        if error.size != npts:
            msg = f"Size of error and curve must match exactly. {error.size} != {npts}."
            raise IndexError(msg)

        return error

    def __init__(self, x, y, yerr=None, xerr=None):
        """Initialize a new `CurveUncertain` object.

        Parameters
        ----------
        x, y : iterable
            x and y coordinate which define the curves central
            trend.
        yerr, xerr : iterable, optional
            Relative error in the y- and x-direction respectively,
            default is `None` indicating no error is defined.

        Returns
        -------
        CurveUncertain
            Initialized `CurveUncertain` object.

        Raises
        ------
        IndexError
            If size of x, y, yerr (if provided) and xerr (if
            provided) are inconsistent.

        """
        # Pass x, y to `Curve`.
        super().__init__(x, y)

        # Handle x-error and y-error.
        npts = self._x.size
        self._yerr = None if yerr is None else self._check_error(yerr, npts)
        self._xerr = None if xerr is None else self._check_error(xerr, npts)
        self._isyerr = False if yerr is None else True
        self._isxerr = False if xerr is None else True

    def resample(self, xx, inplace=False, interp1d_kwargs=None, res_fxn=None):
        """Resample curve and its associated uncertainty.

        Parameters
        ----------
        xx : ndarray
            Desired x values after resampling.
        inplace : bool, optional
            Indicates whether resampling is performed inplace and
            the objects attributes are updated or if calculated
            values are returned.
        interp1d_settings : dict, optional
            Settings for use with the `interp1d` function from `scipy`.
            See documentation `here
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_
            for details.
        res_fxn : tuple of functions, optional
            Functions to define the resampling of the central
            x and y values, xerr and yerr respectively, default is
            `None` indicating default resampling function is used.

        Returns
        -------
        None or Tuple
            If `inplace=True`, returns `None`, instead update
            attributes `_x`, `_y`, `_xerr`, and `_yerr` if they exist.
            If `inplace=False`, returns `Tuple` of the form
            `(xx, yy, yyerr, xxerr)`. If `xerr` and/or `yerr` are not
            defined they are not resampled and omitted from the return
            statement.

        """
        # Unpack res_fxn
        if res_fxn is None:
            res_fxn_xerr, res_fxn_yerr = None, None
        else:
            res_fxn, res_fxn_xerr, res_fxn_yerr = res_fxn

        # Default interpolation kwargs
        if interp1d_kwargs is None:
            interp1d_kwargs = {"kind": "cubic"}

        # Define error resampling first.
        if self._isyerr and res_fxn_yerr is None:
            res_fxn_yerr = super().resample_function(self._x,
                                                     self._yerr,
                                                     **interp1d_kwargs)
        if self._isxerr and res_fxn_xerr is None:
            res_fxn_xerr = super().resample_function(self._x,
                                                     self._xerr,
                                                     **interp1d_kwargs)

        # Resample mean curve
        new_mean_curve = super().resample(xx=xx, inplace=inplace,
                                          interp1d_kwargs=interp1d_kwargs,
                                          res_fxn=res_fxn)
        if inplace:
            xx = self._x
        else:
            xx, yy = new_mean_curve

        # Resample error
        if self._isyerr:
            yerr = res_fxn_yerr(xx)
        if self._isxerr:
            xerr = res_fxn_xerr(xx)

        # Update attributes (if inplace=True).
        if inplace:
            if self._isyerr:
                self._yerr = yerr
            if self._isxerr:
                self._xerr = xerr
        # Or return values (if inplace=False)
        else:
            if self._isyerr and self._isxerr:
                return (xx, yy, yerr, xerr)
            elif self._isyerr:
                return (xx, yy, yerr)
            elif self._isxerr:
                return (xx, yy, xerr)
            else:
                return (xx, yy)
