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

"""GroundModelSuite class definition."""

import scipy.io as sio
import numpy as np
import warnings
import os
from swipp import GroundModel, Suite, DispersionSuite, regex
import logging
logger = logging.getLogger(name=__name__)


class GroundModelSuite(Suite):
    """Class for manipulating suites of `GroundModel` objects.

    Attributes
    ----------
    gms : list
        List of `GroundModel` objects, composing the suite.
    ids : list
        List of identifiers, one per `GroundModel` in the suite.
    misfits : list
        List of misfits, one per `GroundModel` in the suite.

    """
    @staticmethod
    def check_type(groundmodel, identifier, misfit):
        """Check input to `GroundModelSuite`.

        Specifically:
        1. `groundmodel` is of type `GroundModel`.
        2. cast `identifier` to `str`.
        3. cast `misfit` to `float`.
        
        """
        if not isinstance(groundmodel, GroundModel):
            msg = f"`groundmodel` must an instance of `GroundModel`, not {type(groundmodel)}."
            raise TypeError(msg)
        return (groundmodel, str(identifier), float(misfit))

    def __init__(self, groundmodel, identifier, misfit=0.0000):
        """Initialize a `GroundModelSuite` from a `GroundModelObject`.

        Parameters
        ----------
        groundmodel : GroundModel
            Instantiated `GroundModel` object.
        identifier : str
            Human-readable, unique identifier for `groundmodel`.
        misfit : [float, int], optional
            Misfit associated with `groundmodel`, default is 0.0000.

        Returns
        -------
        GroundModelSuite
            Initialized `GroundModelSuite`.

        """
        logger.info("Howdy!")
        super().__init__(*self.check_type(groundmodel, identifier, misfit))
    
    @property
    def gms(self):
        return self._items

    @property
    def size(self):
        return len(self.gms)

    def append(self, groundmodel, identifier, misfit=0.0000, sort=True):
        """Append `GroundModel` object to `GroundModelSuite` object.

        Parameters
        ----------
        groundmodel : GroundModel
            refer to 
            :meth: `__init__ <swipp.GroundModelSuite.__init__>`.
        identifier : str
            refer to
            :meth: `__init__ <swipp.GroundModelSuite.__init__>`.
        misfit : [float, int], optional
            refer to
            :meth: `__init__ <swipp.GroundModelSuite.__init__>`.
        sort : bool
            Sort models according to misfit (smallest to largest),
            default is `True` indicating sort will be performed.
            If it is known that the misfit of appended model is
            larger than those already part of the suite, setting
            `sort` to `False` can allow for a significant speed
            improvement.

        Returns
        -------
        None
            Instead updates the attributes `gms`, `ids`, and `misfits`.

        """
        super().append(*self.check_type(groundmodel, identifier, misfit), sort) 

    def _sort(self):
        """Define how to sort `GroundModelSuite`."""
        for attr in ["_items", "ids", "misfits"]:
            to_sort = getattr(self, attr)
            values = [x for _, x in sorted(zip(self.misfits, to_sort),
                                            key=lambda pair: pair[0])]
            setattr(self, attr, values)

    def vs30(self, nbest="all"):
        """Calculate Vs30 for `GroundModelSuite`.
        
        Parameters
        ----------
        nbest : {int, "all"}, optional
            Number of lowest misfit profiles to return.

        Returns
        -------
        list
            Of the `nbest` Vs30 values.

        See Also
        --------
        Refer to :meth: `vs30 <swipp.GroundModel.vs30>`.
        
        """
        nbest = self._handle_nbest(nbest)
        gms = self.gms[:nbest]
        vs30 = []
        for gm in gms:
            vs30.append(gm.vs30)
        return vs30

    def median_simple(self, nbest="all", parameter='vs'):
        """Calculate layer-by-layer median of a given parameter.

        Parameters
        ----------
        nbest : {int, "all"}, optional
            Number of best models to consider, default is 'all' so all
            models will be used.
        parameter : {'depth', 'vs', 'vp', 'rho'}, optional
            Parameter along which to calculate the median, default
            is 'vs' for shear-wave velocity.

        Returns
        -------
        tuple
            Of the form `(median_thickness, median_parameter)`
            where `median_thickness` is a `list` of the median
            thickness of each layer and `median_parameter` is a `list`
            of the median parameter of each layer.

        """
        nbest = self._handle_nbest(nbest)
        gms = self.gms[:nbest]

        thk, par = gms[0].simplify(parameter)
        thks = np.zeros((len(thk), nbest))
        pars = np.zeros((len(par), nbest))

        for ncol, gm in enumerate(gms):
            thk, par = gm.simplify(parameter)
            thks[:, ncol] = thk
            pars[:, ncol] = par

        return (np.median(thks, axis=1).tolist(),
                np.median(pars, axis=1).tolist())

    def median(self, nbest="all"):
        """Calculate the median `GroundModel` of the `GroundModelSuite`.

        Parameters
        ----------
        nbest : {int, 'all'}, optional
            Number of the best profiles to consider when calculating
            the median profile, default is 'all', meaning all
            available models will be used.

        Returns
        -------
        GroundModel
            Initialized `GroundModel` object.
        
        """
        med_vp_tk, med_vp = self.median_simple(nbest=nbest, parameter='vp')
        med_vs_tk, med_vs = self.median_simple(nbest=nbest, parameter='vs')
        med_rh_tk, med_rh = self.median_simple(nbest=nbest, parameter='rh')
        return self._gm().from_simple_profiles(med_vp_tk, med_vp,
                                               med_vs_tk, med_vs,
                                               med_rh_tk, med_rh)

    def write_to_txt(self, fname, nbest="all"):
        """Write to text file, following the Geopsy format.

        Parameters
        ----------
        fname : str
            Name of file, may be a relative or the full path.
        nbest : {int, 'all'}, optional
            Number of best models to write to file, default is 'all'
            indicating all models will be written.

        Returns
        -------
        None
            Writes file to disk.

        """
        nbest = self._handle_nbest(nbest)
        with open(fname, "w") as f:
            for cid, cmf, cgm in zip(self.ids[:nbest], self.misfits[:nbest], self.gms[:nbest]):
                cgm.write_model(f, cid, cmf)

    def sigma_ln(self, dmax=50, dy=0.5, nbest='all', parameter='vs'):
        """Lognormal standard deviation of a parameter.
        
        Parameters
        ----------
        dmax : float, optional
            Depth to which to discretize the parameter profiles in
            meters, default is 50.
        dy : float, optional
            Linear-spacing of depth samples in meters, default is 0.5.
        nbest : {int, 'all'}, optional
            Number of best profiles to consider for calculation, default
            is 'all'.
        parameter : {'vs', 'vp', 'rh', 'density', 'pr'}, optional
            Parameter to be used for the calculation, default is 'vs'.
        
        Returns
        -------
        Lognormal standard deviation of the nbest discretized profiles.
        
        """
        nbest = self._handle_nbest(nbest)        
        npar = np.empty((int(dmax/dy)+1, nbest))
        for ncol, gm in enumerate(self.gms[:nbest]):
            disc_depth, disc_par = gm.discretize(dmax=dmax, dy=dy,
                                                 parameter=parameter)
            npar[:, ncol] = disc_par
        sigma_ln = np.std(np.log(npar), axis=1, ddof=1)
        return (disc_depth, sigma_ln.tolist())

    @classmethod
    def _gm(cls):
        logger.info("Using swipp, GroundModel.")
        return GroundModel

    @classmethod
    def _gm_suite(cls):
        logger.info("Using swipp, GroundModelSuite.")
        return GroundModelSuite

    @classmethod
    def from_list(cls, groundmodels, identifiers, misfits):
        """Create from a `list` of `GroundModel` objects."""
        obj = cls._gm_suite()(groundmodels[0], identifiers[0], misfits[0])
        if len(groundmodels) > 1:
            for cgm, cid, cmf in zip(groundmodels[1:], identifiers[1:],
                                     misfits[1:]):
                obj.append(cgm, cid, cmf)
        return obj

    @classmethod
    def from_array(cls, tks, vps, vss, rhs, ids, misfits):
        """Create from an array of values.

        Parameters
        ----------
        tks, vps, vss, rhs : ndarray
            2D array representation of the ground models composing
            the suite. Each column represents a particular
            groundmodel and each row a layer in that ground model.
        ids, misfits : ndarray
            1D array where each entry corresponds to a ground model.

        Returns
        -------
        GroundModelSuite
            Instantiated `GroundModelSuite`.

        Raises
        ------
        ValueError
            If the size of the arrays are inconsistent.

        """

        cols = tks.shape[1]
        for other in (vps.shape[1], vss.shape[1], rhs.shape[1], ids.size, misfits.size):
            if cols != other:
                raise ValueError("Array sizes must be consistent.")

        for col in range(cols):
            tk = tks[:, col]
            vp = vps[:, col]
            vs = vss[:, col]
            rh = rhs[:, col]
            _id = ids[col]
            msf = misfits[col]

            obj = cls._gm()(tk, vp, vs, rh)

            if col == 0:
                suite = cls._gm_suite()(obj, _id, msf)
            else:
                suite.append(obj, _id, msf)

        return suite

    @classmethod
    def from_geopsy(cls, fname, nmodels="all"):
        """Create from a file following the `Geopsy` format.

        Parameters
        ----------
        fname : str
            Name of file, may contain a relative or the full path.
        nmodels : {int, 'all'}, optional
            Number of `GroundModels` to extract from file, default is
            `all`.

        Returns
        -------
        GroundModelSuite
            Initialized `GroundModelSuite`.

        """
        if nmodels == "all":
            nmodels = 1E9

        with open(fname, "r") as f:
            lines = f.read()

        identifiers, misfits, gms = [], [], []
        model_count = 0
        for model_info in regex.gm.finditer(lines):
            identifier, misfit, data = model_info.groups()

            identifiers.append(identifier)
            misfits.append(float(misfit))
            gms.append(cls._gm()._parse_gm(data))

            model_count += 1
            if model_count == nmodels:
                break

        return cls.from_list(gms, identifiers, misfits)

    def __getitem__(self, sliced):
        if isinstance(sliced, int):
            return self.gms[sliced]
        if isinstance(sliced, slice):
            return self._gm_suite().from_list(self.gms[sliced],
                                              self.ids[sliced],
                                              self.misfits[sliced])

    def __str__(self):
        """Human-readable representation of a `GroundModelSuite`."""
        return f"GroundModelSuite with {len(self.gms)} GroundModels."
