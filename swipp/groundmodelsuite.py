"""This file defines the class GroundModelSuite."""

import re
import copy
import numpy as np
import os
from swipp import Suite, GroundModel, DispersionSuite
import logging
logging.Logger(name=__name__)


class GroundModelSuite(Suite):
    """Class for manipulating suites of `GroundModel` objects.

    Attributes:

    """

    @staticmethod
    def check_input(groundmodel, identifer, misfit):
        """Check input to `GroundModelSuite`.

        Specifically:
            1. `groundmodel` is of type `GroundModel`.
            2. `identifier` is `str`.
            3. `misfit` is `float` or `int`.
        """
        if not isinstance(groundmodel, GroundModel):
            msg = f"`groundmodel` must be of type `GroundModel`, not {type(groundmodel)}."
            raise TypeError(msg)
        if type(identifer) != str:
            msg = f"`identifier` must be of type `str`, not {type(identifer)}."
            raise TypeError(msg)
        if type(misfit) not in [float, int]:
            msg = f"`groundmodel` must be of type `float` or `int`, not {type(groundmodel)}."
            raise TypeError(msg)

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
        self.check_input(groundmodel, identifier, misfit)
        self.gms = [groundmodel]
        self.ids = [copy.deepcopy(identifier)]
        self.misfits = [copy.deepcopy(misfit)]

    def append(self, groundmodel, identifier, misfit=0.0000, sort=True):
        """Append `GroundModel` object to `DispersionSuite` object.

        Args:
            groundmodel : GroundModel
                refer to :meth: `__init__ <swipp.GroundModelSuite.__init__>`.
            identifier : str
                refer to :meth: `__init__ <swipp.GroundModelSuite.__init__>`.
            misfit : [float, int], optional
                refer to :meth: `__init__ <swipp.GroundModelSuite.__init__>`.
            sort : bool
                Sort models according to misfit (smallest to largest),
                default is `True` indicating sort will be performed.
                If it is known that the misfit of appended model is
                larger than those already part of the suite, setting
                `sort` to `False` may allow for a significant speed
                improvement.

        Returns:
            `None`, updates the attributes `gms`, `ids`, and `misfits`.
        """
        self.check_input(groundmodel, identifier, misfit)
        self.gms.append(groundmodel)
        self.ids.append(copy.deepcopy(identifier))
        self.misfits.append(copy.deepcopy(misfit))

        # Sort
        if sort:
            self.gms = [cgm for _, cgm in sorted(
                zip(self.misfits, self.gms), key=lambda pair: pair[0])]
            self.ids = [cid for _, cid in sorted(
                zip(self.misfits, self.ids), key=lambda pair: pair[0])]
            self.misfits.sort()

    @staticmethod
    def mkgm(thk, vps, vss, rho):
        # print("swipp GroundModel")
        return GroundModel(thickness=thk, vp=vps, vs=vss, density=rho)

    @classmethod
    def from_geopsy(cls, fname):
        """Instantiate a `GroundModelSuite` from a file exported from
        Geopsy.

        Args:
            fname : str
                Name of file, may contain a relative or the full path.

        Returns:
            Initialized `GroundModelSuite`.
        """

        with open(fname, "r") as f:
            lines = f.read().splitlines()

        thk, vps, vss, rho = [], [], [], []
        first = True
        obj = None
        regex_one = r"(\d+.?\d*[eE]?[+-]?\d*)"
        sp = r"\s"
        regex_all = f"^{regex_one}{sp}{regex_one}{sp}{regex_one}{sp}{regex_one}$"
        exp1 = r"^# Layered model (\d+): value=(\d+.?\d*)$"
        for line in lines:
            try:
                thk_i, vps_i, vss_i, rho_i = re.findall(regex_all, line)[0]
                thk.append(float(thk_i))
                vps.append(float(vps_i))
                vss.append(float(vss_i))
                rho.append(float(rho_i))
            except IndexError:
                if line.startswith("# "):
                    if line.startswith("# Layered model"):
                        if first == True:
                            mod_num, misfit = re.findall(exp1, line)[0]
                            c_misfit = float(misfit)
                            first = False
                        elif obj is None:
                            cgm = cls.mkgm(thk, vps, vss, rho)
                            obj = cls(cgm, mod_num, c_misfit)
                            mod_num, misfit = re.findall(exp1, line)[0]
                            c_misfit = float(misfit)
                            thk, vps, vss, rho = [], [], [], []
                        else:
                            cgm = cls.mkgm(thk, vps, vss, rho)
                            obj.append(cgm, mod_num, c_misfit)
                            mod_num, misfit = re.findall(exp1, line)[0]
                            c_misfit = float(misfit)
                            thk, vps, vss, rho = [], [], [], []
        cgm = cls.mkgm(thk, vps, vss, rho)
        if obj is None:
            obj = cls(cgm, mod_num, c_misfit)
        else:
            obj.append(cgm, mod_num, c_misfit)
        return obj

    def vs30(self, nbest=None):
        """Returns a `list` of Vs30 values (one per `GroundModel`),
        refer to :meth: `vs30 <swipp.GroundModel.vs30>`."""
        if nbest == None:
            gms = self.gms
        else:
            gms = self.gms[:nbest]
        vs30 = []
        for gm in gms:
            vs30.append(gm.vs30)
        return vs30

    def median_simple(self, nbest, parameter='vs'):
        """Calculate the simplified, layer-by-layer median of a given
        parameter.

        Args:
            nbest : int
                Number of best models to consider.
            parameter : {'depth', 'vs', 'vp', 'rho'}
                Parameter along which to calculate the median.

        Returns:
            A `tuple` of the form `(median_thickness, median_parameter)`
            where `median_thickness` is a `list` of the median thickness
            of each layer and `median_parameter` is a `list` of the
            median parameter of each layer.
        """
        thk, par = self.gms[0].simplify(parameter)
        thks = np.zeros((len(thk), nbest))
        pars = np.zeros((len(par), nbest))

        for ncol, gm in enumerate(self.gms[0:nbest]):
            thk, par = gm.simplify(parameter)
            thks[:, ncol] = thk
            pars[:, ncol] = par

        return (np.median(thks, axis=1).tolist(),
                np.median(pars, axis=1).tolist())

    def median(self, nbest):
        """Calculate the median `GroundModel` of the `GroundModelSuite`.

        Args:
            nbest : int
                Number of the best profiles to consider when calculating
                the median profile.

        Returns:
            Initialized `GroundModel` object.

        Example:
            >>> import swipp
            >>> gm1 = swipp.GroundModel(thickness=[1.0,0], vp=[200,500], vs=[100,250], density=[2000,2000])
            >>> gm2 = swipp.GroundModel(thickness=[2.5,0], vp=[500,900], vs=[200,300], density=[2000,2000])    
            >>> gm3 = swipp.GroundModel(thickness=[5.0,0], vp=[400,800], vs=[250,300], density=[2000,2000])    
            >>> mysuite = swipp.GroundModelSuite.from_list([gm1, gm2, gm3], ["gm1", "gm2", "gm3"], [0.0, 0.0, 0.0])
            >>> median = mysuite.median(nbest=3)
            >>> print(median)
            2
            2.5 400.0 200.0 2000.0
            0 800.0 300.0 2000.0
        """
        med_vp_tk, med_vp = self.median_simple(nbest=nbest, parameter='vp')
        med_vs_tk, med_vs = self.median_simple(nbest=nbest, parameter='vs')
        med_rh_tk, med_rh = self.median_simple(nbest=nbest, parameter='rh')
        return self.gm().from_simple_profiles(med_vp_tk, med_vp,
                                              med_vs_tk, med_vs,
                                              med_rh_tk, med_rh)

    # TODO (jpv): Clean up this method and calls.
    @classmethod
    def gm(cls):
        return GroundModel

    @classmethod
    def from_list(cls, groundmodels, ids, misfits):
        """Instantiate `GroundModelSuite` from `list` of `GroundModel`
        objects.
        """
        obj = cls(groundmodels[0], ids[0], misfits[0])
        for cgm, cid, cmf in zip(groundmodels[1:], ids[1:], misfits[1:]):
            obj.append(cgm, cid, cmf)
        return obj

    def write_to_txt(self, fname):
        """Write `GroundModelSuite` to text file, following the Geopsy
        format.

        Args:
            fname : str
                Name of file, may be a relative or the full path.

        Returns:
            `None`, writes file to disk.
        """
        with open(fname, "w") as f:
            for cid, cmf, cgm in zip(self.ids, self.misfits, self.gms):
                cgm.write_model(f, cid, cmf)

    def __getitem__(self, sliced):
        if isinstance(sliced, int):
            return self.gms[sliced]
        if isinstance(sliced, slice):
            return GroundModelSuite.from_list(self.gms[sliced],
                                          self.ids[sliced],
                                          self.misfits[sliced])

    def __repr__(self):
        return f"GroundModelSuite with {len(self.gms)} models."
