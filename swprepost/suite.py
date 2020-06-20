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

"""Suite class definition."""

from abc import ABC, abstractmethod
import warnings

import numpy as np

__all__ = ["Suite"]


class Suite(ABC):

    @abstractmethod
    def __init__(self, item):
        """Create `Suite` from `item`."""
        self._items = [item]

    def _append(self, item, sort=True):
        """Append item to `Suite`."""
        self._items.append(item)
        if sort:
            self._sort()

    def _sort(self):
        """Define how to sort `Suite`."""
        self._items = [x for _, x in sorted(zip(self.misfits, self._items),
                                            key=lambda pair: pair[0])]

    @property
    def size(self):
        return len(self._items)

    @property
    def misfits(self):
        return [_items.misfit for _items in self._items]

    @property
    def identifiers(self):
        return [_items.identifier for _items in self._items]

    def _handle_nbest(self, nbest):
        """Accept common `nbest` values and return the logical result."""
        if nbest is None:
            msg = "nbest=None is deprecated, use 'all' instead."
            warnings.warn(msg, DeprecationWarning)
            nbest = "all"

        max_avail = self.size

        if nbest == "all":
            return max_avail
        else:
            try:
                nbest = int(nbest)
            except ValueError as e:
                msg = "`nbest` must be cast-able to `int`."
                raise ValueError(msg) from e

            if nbest > max_avail:
                msg = f"Requested ({nbest}) > Available ({max_avail})"
                msg += f", setting requested to available."
                warnings.warn(msg)
                return max_avail
            else:
                return nbest

    def misfit_range(self, nmodels="all"):
        """Return range of misfits for nmodels.

        Parameters
        ----------
        nmodels : {int, "all"}, optional
            Number of models to consider, default is 'all' so all
            avaiable models will be considered.

        Returns
        -------
        float, tuple
            If `nmodels==1`, returns `float` corresponding to the single
            best misfit, otherwise returns `tupele` of the form 
            (min_msft, max_msft).

        """
        if nmodels == "all":
            return (self.misfits[0], self.misfits[-1])
        elif nmodels == 1:
            return self.misfits[0]
        else:
            return (self.misfits[0], self.misfits[nmodels-1])

    def misfit_repr(self, nmodels="all", **kwargs):
        """String representation of misfit [min-max] or [min].

        Parameters
        ----------
        nmodels : {int, "all"}, optional
            Number of models to consider, default is 'all' so all
            avaiable models will be considered.
        **kwargs
            Optional keyword arguements for `np.format_float_positional`
            https://docs.scipy.org/doc/numpy-1.15.1/reference/generated/numpy.format_float_positional.html

        Returns
        -------
        str
            Representation of the misfit values for the selected suite.

        """
        format_kwargs = {"unique": False, "precision": 2, "fractional": True}
        for key, value in kwargs.items():
            format_kwargs[key] = value

        def prep(x): return np.format_float_positional(x,  **format_kwargs)
        if nmodels == 1:
            return f"[{prep(self.misfit_range(nmodels=1))}]"
        else:
            min_msft, max_msft = self.misfit_range(nmodels=nmodels)
            return f"[{prep(min_msft)}-{prep(max_msft)}]"

    def __eq__(self, other):
        """Define when two Suite objects are equal."""
        if self.size != other.size:
            return False
        for my, ur in zip(self._items, other._items):
            if my != ur:
                return False
        return True
        