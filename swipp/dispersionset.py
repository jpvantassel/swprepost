"""This file contains the definition of the class `DispersionSet`."""

import re
import copy
from swipp import CurveSet, DispersionCurve, regex

class DispersionSet(CurveSet):
    """Class for handling sets of 
    :meth `DispersionCurve <swipp.DispersionCurve>`
    objects, which all belong to a common velocity model.

    Attributes:
        rayleigh, love : dict
            Container for `DispersionCurve` objects, of the form:
            {0:disp_curve_obj0, 1:disp_curve_obj1, ... N:disp_curve_objN}
            where each key is the mode number and the value is the
            corresponding instantiated DispersionCurve object.
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
                Container for `DispersionCurve` objects, of the form:
                {0:disp_curve_obj0,
                 1:disp_curve_obj1, 
                 ... N:disp_curve_objN}
                where each key is the mode number and the value is the
                corresponding `DispersionCurve` object.
        """
        self.check_input([rayleigh, love], DispersionCurve)
        self.check_input_local(identifier, misfit)
        self.rayleigh = copy.deepcopy(rayleigh)
        self.love = copy.deepcopy(love)
        self.identifier = identifier
        self.misfit = misfit

    # TODO (jpv): Add in Love and Rayleigh mode optimizations.
    @classmethod
    def _from_lines(cls, lines, nrayleigh="all", nlove="all"):
        """Create an instance of `DispersionSet` from a list of strings.

        Args:
            lines : list(str)
                List of strings, one per line, following the syntax of
                a geopy output file.
            nrayleigh, nlove : int, optional
                Number of Rayleigh and Love modes respectively, default
                is `None` so all available modes will be extracted.

        Returns:
            Instantiated `DispersionSet` object.
        """
        # Find line numbers
        modes = {"rayleigh": {}, "love": {}}
        # TODO (jpv): Add in the mode optimizations
        # stop_search_rayleigh = False if nrayleigh > 0 else True
        # mode_type = "rayleigh"
        identifier, misfit = regex.model.findall(lines[0])[0]
        for line_number, line in enumerate(lines):
            try:
                mode_type = regex.wave.findall(line)[0]
                mode_type = mode_type.lower()
            except IndexError:
                # if mode_type == "rayleigh" and stop_search_rayleigh:
                #     continue
                try:
                    mode_number = regex.mode.findall(line)[0]
                    mode_number = int(mode_number)

                    # check_rayleigh = (mode_type == "rayleigh" and mode_number == nrayleigh)
                    # check_love = (mode_type == "love" and mode_number == nlove)
                    # if check_rayleigh:
                    #     if nlove == 0:
                    #         break
                    #     else:
                    #         stop_search_rayleigh = True
                    # if check_love:
                    #     break
                    modes[mode_type].update({mode_number: line_number})

                except IndexError:
                    try:
                        c_identifier, c_misfit = regex.model.findall(line)[0]
                        if c_identifier != identifier:
                            break
                        else:
                            continue
                    except IndexError:
                        continue

        # Pass proper lines to DispersionCurve
        dcs = {"rayleigh":{}, "love":{}}
        for wave_type, mode_info in modes.items():
            for mode_number, starting_line in mode_info.items():
                dc = DispersionCurve._from_lines(lines[starting_line:])
                dcs[wave_type].update({mode_number:dc})

        rayleigh = None if dcs["rayleigh"]=={} else dcs["rayleigh"] 
        love = None if dcs["love"]=={} else dcs["love"] 
        return cls(identifier, float(misfit), rayleigh=rayleigh, love=love)

    @classmethod
    def from_geopsy(cls, fname, nrayleigh="all", nlove="all"):
        """Create an instance of `DispersionSet` from a text file
        created by the Geopsy command `gpdc`.

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
            lines = f.read().splitlines()

        # Start right after introduction of a layered model.
        model_regex = r"^# Layered model (\d+): value=(\d+.?\d*)$"
        for line_number, line in enumerate(lines):
            try:
                indentifier, misfit = re.findall(model_regex, line)[0]
                break
            except IndexError:
                continue

        return cls._from_lines(lines[line_number:], nrayleigh=nrayleigh, nlove=nlove)

    def __repr__(self):
        return f"DispersionSet(identifier={self.identifier}, rayleigh={self.rayleigh}, love={self.love}, misfit={self.misfit})"
