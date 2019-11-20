"""This file contains methods to handle a ground model (i.e., layered
velocity model object) suite."""

import re
import copy
import numpy as np
import os
from swipp import Suite, GroundModel, DispersionSuite
import logging
logging.Logger(name=__name__)


class GroundModelSuite(Suite):
    """Class for manipulating suites of GroundModel objects.

    Attributes:
        This class contains no public attributes.
    """

    @staticmethod
    def check_input():
        pass

    def __init__(self, groundmodel, identifer, misfit=None):
        """Initialize a GroundModelSuite from a GroundModelObject.

        Args:
            groundmodel: Instantiated GroundModel object.
            identifier: String uniquely identifying the GroundModel.
            misfit: Float or int denoting the GroundModel's misfit.

        Returns:
            Initialized GroundModelSuite object.

        Raises:
            This method raises no exceptions.
        """
        # TODO add type checking here
        self.check_input()
        self.gms = [groundmodel]
        self.ids = [copy.deepcopy(identifer)]
        self.misfits = [copy.deepcopy(misfit)]

    def append(self, groundmodel, identifier, misfit=None, sort=False):
        """Append an instantiated GroundModel object to an existing
        DispersionSuite object.

        Args:
            Refer to :meth: `__init__` documentation.

        Returns:
            `None`, updates the attributes `gms`, `ids`, and `misfits`.
        """
        self.check_input()
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

    @classmethod
    def from_geopsy(cls, fname):
        """Alternate constuctor for instantiating a GroundModelSuite
        from a file exported from Geopsy.

        Args:
            fname: Name of file to be read, may contain a relative or
                full path if desired.

        Returns:
            Initialized FileGM object.

        Raises:
            Various errors if ground model file is not of the correct 
            format. See example files for details.
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
                        elif obj == None:
                            cgm = GroundModel(thickness=thk,
                                              vp=vps,
                                              vs=vss,
                                              density=rho)
                            obj = cls(cgm, mod_num, c_misfit)
                            mod_num, misfit = re.findall(exp1, line)[0]
                            c_misfit = float(misfit)
                            thk, vps, vss, rho = [], [], [], []
                        else:
                            cgm = GroundModel(thickness=thk,
                                              vp=vps,
                                              vs=vss,
                                              density=rho)
                            obj.append(cgm, mod_num, c_misfit)
                            mod_num, misfit = re.findall(exp1, line)[0]
                            c_misfit = float(misfit)
                            thk, vps, vss, rho = [], [], [], []

        cgm = GroundModel(thickness=thk, vp=vps, vs=vss, density=rho)
        if obj == None:
            obj = cls(cgm, mod_num, c_misfit)
        else:
            obj.append(cgm, mod_num, c_misfit)

        return obj

    def vs30(self, nbest=None):
        """Return a list of Vs30 (one per GroundModel), refer to :meth: `vs30`."""
        if nbest == None:
            gms = self.gms
        else:
            gms = self.gms[:nbest]
        vs30 = []
        for gm in gms:
            vs30.append(gm.vs30)
        return vs30

    def median_simple(self, nbest, param='vs'):
        """Returns simple median of a given parameter."""
        thk, par = self.gms[0].simplify(param)
        thks = np.zeros((len(thk), nbest))
        pars = np.zeros((len(par), nbest))

        for ncol, gm in enumerate(self.gms[0:nbest]):
            thk, par = gm.simplify(param)
            thks[:, ncol] = thk
            pars[:, ncol] = par

        return (np.median(thks, axis=1).tolist(),
                np.median(pars, axis=1).tolist())

    def median(self, nbest):
        """Returns intialized GroundModel object corresponding to median
        of the GroundModelSuite."""
        med_vp_tk, med_vp = self.median_simple(nbest=nbest, param='vp')
        med_vs_tk, med_vs = self.median_simple(nbest=nbest, param='vs')
        med_rh_tk, med_rh = self.median_simple(nbest=nbest, param='rh')
        return GroundModel.from_simple_profiles(med_vp_tk, med_vp,
                                                med_vs_tk, med_vs,
                                                med_rh_tk, med_rh)

    @classmethod
    def from_groundmodels(cls, groundmodels, ids, misfits):
        """Create GroundModel Suite from list of GroundModels"""
        obj = cls(groundmodels[0], ids[0], misfits[0])
        for cgm, cid, cmf in zip(groundmodels[1:], ids[1:], misfits[1:]):
            obj.append(cgm, cid, cmf)
        return obj

    def __getitem__(self, sliced):
        return GroundModelSuite.from_groundmodels(self.gms[sliced], self.ids[sliced], self.misfits[sliced])

    def write_to_txt(self, fname):
        """Write GroundModelSuite to text file."""
        with open(fname, "w") as f:
            for cid, cmf, cgm in zip(self.ids, self.misfits, self.gms):
                cgm.write_model(f, cid, cmf)
