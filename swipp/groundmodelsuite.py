"""This file defines the class `GroundModelSuite`."""

import scipy.io as sio
import numpy as np
import warnings
import os
from swipp import GroundModel, Suite, DispersionSuite, regex
import logging
logging.Logger(name=__name__)


class GroundModelSuite(Suite):
    """Class for manipulating suites of `GroundModel` objects.

    Attributes:
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

        Args:
            groundmodel : GroundModel
                Instantiated `GroundModel` object.
            identifier : str
                Human-readable, unique identifier for `groundmodel`.
            misfit : [float, int], optional
                Misfit associated with `groundmodel`, default is 0.0000.

        Returns:
            Initialized `GroundModelSuite`.
        """
        gm, identifier, misfit = self.check_type(groundmodel, identifier,
                                                 misfit)
        self.gms = [gm]
        self.ids = [identifier]
        self.misfits = [misfit]

    def append(self, groundmodel, identifier, misfit=0.0000, sort=True):
        """Append `GroundModel` object to `DispersionSuite` object.

        Args:
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

        Returns:
            `None`, updates the attributes `gms`, `ids`, and `misfits`.
        """
        gm, identifier, misfit = self.check_type(groundmodel, identifier,
                                                 misfit)
        self.gms.append(gm)
        self.ids.append(identifier)
        self.misfits.append(misfit)

        if sort:
            self.gms = [cgm for _, cgm in sorted(zip(self.misfits, self.gms),
                                                 key=lambda pair: pair[0])]
            self.ids = [cid for _, cid in sorted(zip(self.misfits, self.ids),
                                                 key=lambda pair: pair[0])]
            self.misfits.sort()

    @staticmethod
    def mkgm(thk, vps, vss, rho):
        return GroundModel(thickness=thk, vp=vps, vs=vss, density=rho)

    def vs30(self, nbest="all"):
        """Returns a `list` of the nbest Vs30 values,
        refer to :meth: `vs30 <swipp.GroundModel.vs30>`."""
        if nbest == "all":
            gms = self.gms
        else:
            gms = self.gms[:nbest]
        vs30 = []
        for gm in gms:
            vs30.append(gm.vs30)
        return vs30

    def median_simple(self, nbest="all", parameter='vs'):
        """Calculate the simplified, layer-by-layer median of a given
        parameter.

        Args:
            nbest : int
                Number of best models to consider.
            parameter : {'depth', 'vs', 'vp', 'rho'}, optional
                Parameter along which to calculate the median, default
                is 'vs' for shear-wave velocity.

        Returns:
            A `tuple` of the form
            `([median_thickness], [median_parameter])`
            where `[median_thickness]` is a `list` of the median
            thickness of each layer and `[median_parameter]` is a `list`
            of the median parameter of each layer.
        """
        if str(nbest) == "all":
            nbest = len(self.gms)
            gms = self.gms
        else:
            gms = self.gms[0:nbest]

        thk, par = self.gms[0].simplify(parameter)
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

        Args:
            nbest : int, optional
                Number of the best profiles to consider when calculating
                the median profile, default is "all", meaning all
                available models will be used.

        Returns:
            Initialized `GroundModel` object.
        """
        med_vp_tk, med_vp = self.median_simple(nbest=nbest, parameter='vp')
        med_vs_tk, med_vs = self.median_simple(nbest=nbest, parameter='vs')
        med_rh_tk, med_rh = self.median_simple(nbest=nbest, parameter='rh')
        return self._gm().from_simple_profiles(med_vp_tk, med_vp,
                                               med_vs_tk, med_vs,
                                               med_rh_tk, med_rh)

    def write_to_txt(self, fname):
        """Write `GroundModelSuite` to text file, following the Geopsy
        format.

        Args:
            fname : str
                Name of file, may be a relative or the full path.

        Returns:
            `None`, instead writes file to disk.
        """
        with open(fname, "w") as f:
            for cid, cmf, cgm in zip(self.ids, self.misfits, self.gms):
                cgm.write_model(f, cid, cmf)

    @classmethod
    def _gm(cls):
        return GroundModel

    @classmethod
    def from_list(cls, groundmodels, identifiers, misfits):
        """Instantiate `GroundModelSuite` from `list` of `GroundModel`
        objects.
        """
        obj = cls(groundmodels[0], identifiers[0], misfits[0])
        if len(groundmodels) > 1:
            for cgm, cid, cmf in zip(groundmodels[1:], identifiers[1:],
                                     misfits[1:]):
                obj.append(cgm, cid, cmf)
        return obj

    @classmethod
    def from_mat(cls, fname, tk="thickness", vs="vs", vp="vp", rh="rho",
                 misfit="misfits", identifier="indices"):
        """Instantiate a `GroundModelSuite` from a `.mat` file.

        Note: This method is still largely experimental and is not
        guaranteed to work.

        Args:
            fname : str
                Name of file to be read, in general these files should
                end with th `.mat` extension.
            tk, vs, vp, rh, misfit, identifer : str, optional
                Custom variable names, for which the program will search
                to find the resulting values.

                In addtion to these custom names, which are searched
                first the program will also see if the values are under
                other common names:

                thickness : [tk, "thickness"]
                vs : [vs, "Vs1", "vs1"]
                vp : [vp, "Vp1", "vp1"]
                rh : [rh, "Rho1", "rho1", "density1"]
                misfit : [misfit, "misfit"]
                ids : [identifier, "indices"]

        Returns:
            Instantiated `GroundModelSuite` object.

        Raises:
            KeyError : 
                If required variables, can not be found in `.mat` file.
        """
        # Potential names for each parameter, from high to low priority.
        search_values = {"tk": [tk, "thickness"],
                      "vs": [vs, "Vs1", "vs1"],
                      "vp": [vp, "Vp1", "vp1"],
                      "rh": [rh, "Rho1", "rho1", "density1"],
                      "misfit": [misfit, "misfit"],
                      "ids": [identifier, "indices"]}

        # Load's matlab file as `dict`.
        data = sio.loadmat(fname)

        results = {}
        for par, keys in search_values.items():
            for key in keys:
                val = data.get(key)
                if val is not None:
                    results[par] = val
                    break
            else:
                if par == "misfit":
                    msg = f"Cound not find {par}, using keys={keys}, ignoring."
                    warnings.warn(msg)
                else:
                    msg = f"Could not find {par}, using keys={keys}."
                    raise KeyError(msg)

        if results.get("misfit") is None:
            results["misfit"] = np.zeros(results["ids"].shape)

        return cls.from_array(results["tk"], results["vp"],
                              results["vs"], results["rh"],
                              results["ids"][0], results["misfit"][0])

    @classmethod
    def from_array(cls, tks, vps, vss, rhs, ids, misfits):

        cols = tks.shape[1]
        for other in (vps.shape[1], vss.shape[1], rhs.shape[1],
                      ids.size, misfits.size):
            assert(cols == other)

        for col in range(cols):
            tk = tks[:, col]
            vp = vps[:, col]
            vs = vss[:, col]
            rh = rhs[:, col]
            _id = ids[col]
            msf = misfits[col]

            obj = GroundModel(tk, vp, vs, rh)

            if col == 0:
                suite = cls(obj, _id, msf)
            else:
                suite.append(obj, _id, msf)

        return suite

    @classmethod
    def from_geopsy(cls, fname, nmodels="all"):
        """Instantiate a `GroundModelSuite` from a file exported from
        Geopsy.

        Args:
            fname : str
                Name of file, may contain a relative or the full path.

        Returns:
            Initialized `GroundModelSuite`.
        """
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
            return GroundModelSuite.from_list(self.gms[sliced],
                                              self.ids[sliced],
                                              self.misfits[sliced])

    def __repr__(self):
        return f"GroundModelSuite with {len(self.gms)} GroundModels."
