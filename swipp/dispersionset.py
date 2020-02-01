"""This file contains the class `DispersionSet`."""

import re
import copy
from swipp import CurveSet, DispersionCurve, regex


class DispersionSet(CurveSet):
    """Class for handling sets of 
    :meth: `DispersionCurve <swipp.DispersionCurve>`
    objects, which all belong to a common velocity model.

    Attributes:
        rayleigh, love : dict
            Container for `DispersionCurve` objects, of the form:
            {0:disp_curve_obj0, ... N:disp_curve_objN}
            where each key is the mode number and the value is the
            corresponding instantiated `DispersionCurve` object.
    """

    @classmethod
    def check_input_local(cls, identifier, misfit):
        """Check inputs comply with the required format.

        Specfically:
            1. `identifier` is a `str`.
            2. `misfit` is an `int` or `float`.
        """
        if not isinstance(identifier, str):
            msg = f"'{identifier}' must be `str`, not {type(identifier)}."
            raise TypeError(msg)
        if misfit != None:
            if type(misfit) not in [int, float]:
                msg = f"`misfit` must be `int` or `float`, not {type(misfit)}."
                raise TypeError(msg)

    def __init__(self, identifier, misfit=None, rayleigh=None, love=None,):
        """Initialize a `DispersionSet` object from a `dict` of 
        instantiated `DispersionCurve` objects.

        Args:
            identifier : str
                Unique identifier of the `DispersionSet`.
            misfit : float, int
                `DispersionSet` misfit.
            rayleigh, love : dict
                Container for `DispersionCurve` objectso of the form
                `{0:disp_curve_obj0, ... N:disp_curve_objN}` where each
                key is the mode number and the value is the
                corresponding `DispersionCurve` object.
        """
        self.check_input([rayleigh, love], DispersionCurve)
        self.check_input_local(identifier, misfit)
        self.rayleigh = copy.deepcopy(rayleigh)
        self.love = copy.deepcopy(love)
        self.identifier = identifier
        self.misfit = misfit

    @classmethod
    def _parse_dcs(cls, dcs_data, nmodes="all"):
        """Parse a group of modes into a `dict` of `DispersionCurves`"""
        modes = regex.mode.split(dcs_data)

        if nmodes == "all":
            modes = modes[1:]
        else:
            modes = modes[1:nmodes+1]

        dcs = {}
        for mode_number, dc_data in enumerate(modes):
            dcs.update({mode_number: cls._dc()._parse_dc(dc_data)})
        return dcs

    @classmethod
    def _from_full_file(cls, data, nrayleigh="all", nlove="all"):
        rayleigh, love = None, None
        previous_id, previous_misfit = "start", "0"
        for model_info in regex.dcset.finditer(data):
            identifier, misfit, wave_type, dcs_data = model_info.groups()

            if identifier == previous_id or previous_id == "start":
                if wave_type == "Rayleigh":
                    rayleigh = cls._parse_dcs(dcs_data, nmodes=nrayleigh)
                elif wave_type == "Love":
                    love = cls._parse_dcs(dcs_data, nmodes=nlove)
                else:
                    raise NotImplementedError
                previous_id = identifier
                previous_misfit = misfit
            else:
                break

        return cls(previous_id, float(previous_misfit),
                   rayleigh=rayleigh, love=love)

    @classmethod
    def _dc(cls):
        return DispersionCurve

    @classmethod
    def from_geopsy(cls, fname, nrayleigh="all", nlove="all"):
        """Create a `DispersionSet` object from a text file following
        the Geopsy format.

        Args:
            fname : str
                Name of file to be read, may be a relative or full path.
            nrayleigh, nlove : int, optional
                Number of Rayleigh and Love modes respectively, default
                is `None` so all available modes will be extracted.

        Returns:
            Instantiated `DispersionSet` object.
        """
        with open(fname, "r") as f:
            data = f.read()
        return cls._from_full_file(data, nrayleigh=nrayleigh, nlove=nlove)

    def __repr__(self):
        return f"DispersionSet(identifier={self.identifier},\
rayleigh={self.rayleigh}, love={self.love}, misfit={self.misfit})"
