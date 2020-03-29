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

"""The Suite class definition."""


__all__ = ["Suite"]


class Suite():

    def __init__():
        pass

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

    def misfit_repr(self, nmodels="all"):
        """Return string representation of misfit [min-max] or [min]."""
        if nmodels == 1:
            return f"[{round(self.misfits[0],2)}]"
        else:
            min_msft, max_msft = self.misfit_range(nmodels=nmodels)
            return f"[{round(min_msft,2)}-{round(max_msft,2)}]"
