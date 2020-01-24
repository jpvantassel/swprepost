"""This file defines the class `GroundModelSuite`."""

import numpy as np
import os
from swipp import GroundModel, DispersionSuite, regex
import logging
logging.Logger(name=__name__)


class GroundModelSuite():
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

    def median_simple(self, nbest, parameter='vs'):
        """Calculate the simplified, layer-by-layer median of a given
        parameter.

        Args:
            nbest : int
                Number of best models to consider.
            parameter : {'depth', 'vs', 'vp', 'rho'}, optional
                Parameter along which to calculate the median, default
                is shear-wave velocity (i.e., 'vs').

        Returns:
            A `tuple` of the form 
            `([median_thickness], [median_parameter])`
            where `[median_thickness]` is a `list` of the median
            thickness of each layer and `[median_parameter]` is a `list`
            of the median parameter of each layer.
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
    def from_list(cls, groundmodels, ids, misfits):
        """Instantiate `GroundModelSuite` from `list` of `GroundModel`
        objects.
        """
        obj = cls(groundmodels[0], ids[0], misfits[0])
        if len(groundmodels) > 1:
            for cgm, cid, cmf in zip(groundmodels[1:], ids[1:], misfits[1:]):
                obj.append(cgm, cid, cmf)
        return obj

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
            lines = f.read().splitlines()

        line_numbers, identifiers, misfits = [], [], []
        for line_number, line in enumerate(lines):
            try:
                identifier, misfit = regex.model.findall(line)[0]
                line_numbers.append(line_number)
                identifiers.append(identifier)
                misfits.append(float(misfit))
                if len(identifiers) == nmodels:
                    break
            except IndexError:
                continue
            else:
                lines.append("")
        line_numbers.append(line_number+1)

        gms = []
        for start_line, end_line in zip(line_numbers[:-1], line_numbers[1:]):
            gms.append(GroundModel._from_lines(lines[start_line:end_line]))

        return cls.from_list(gms, identifiers, misfits)

    def __getitem__(self, sliced):
        if isinstance(sliced, int):
            return self.gms[sliced]
        if isinstance(sliced, slice):
            return GroundModelSuite.from_list(self.gms[sliced],
                                              self.ids[sliced],
                                              self.misfits[sliced])

    def __repr__(self):
        return f"GroundModelSuite with {len(self.gms)} models."
