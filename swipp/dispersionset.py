"""This file contains the definition of the class `DispersionSet`."""

import re
import copy
from swipp import CurveSet, DispersionCurve

class DispersionSet(CurveSet):
    """Class for handling sets of 
    :meth `DispersionCurve <swipp.DispersionCurve>`
    objects which all belong to a common velocity model.

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

    # TODO (jpv): Refactor DispersionSuite.from_geopsy so that it calls
    # DispersionSet.from_geopsy.

    @classmethod
    def from_geopsy(cls, fname):
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
        c_model, c_mode = None, None
        set_count = 0
        exp0 = r"^# Layered model (\d+): value=(\d+.?\d*)$"
        # exp1 = r"^# (\d+) (Rayleigh|Love) dispersion mode\(s\)$"
        exp2 = r"^# Mode (\d+)"
        exp3 = r"^(\d+.?\d*[eE]?[+-]?\d*) (\d+.?\d*[eE]?[+-]?\d*)$"
        # TODO (jpv) have this go by linenumber so it can skip ahead
        # when necessary
        for line in lines:
            # Assume we are on a data line.
            try:
                f, p = re.findall(exp3, line)[0]
                cfrq.append(float(f))
                camp.append(float(p))
            # If not, must be on a comment line.
            except IndexError:
                # Indicates a new model, or a change in type of dispersion.
                if line.startswith("# Layered model"):
                    model_string, misfit_string = re.findall(exp0, line)[0]
                    model, misfit = int(model_string), float(misfit_string)
                    # Run once at the start of the file, to initialize vars.
                    if c_model == None:
                        ray, lov = {}, {}
                        c_model, c_misfit = model, misfit
                    else:
                        # Update ray or lov dictionaries with captured values.
                        if modetype == "r":
                            ray.update({c_mode: DispersionCurve(
                                cfrq, [1/x for x in camp])})
                        elif modetype == "l":
                            lov.update({c_mode: DispersionCurve(
                                cfrq, [1/x for x in camp])})
                        # If first set, save a new object and prepare for next.
                        if (model != c_model) and (set_count == 0):
                            # if (modetype == "r") or (modetype == "l"):
                            return cls(identifier=str(c_model), misfit=c_misfit, rayleigh=ray, love=lov)
                        # This must be the same model, so continue acquisition.
                        else:
                            continue
                elif line.endswith("Rayleigh dispersion mode(s)"):
                    modetype = "r"
                elif line.endswith("Love dispersion mode(s)"):
                    modetype = "l"
                elif line.startswith("# Mode"):
                    # If this is not the first loop, update.
                    if c_mode != None:
                        if modetype == "r":
                            ray.update({c_mode: DispersionCurve(
                                cfrq, [1/x for x in camp])})
                        elif modetype == "l":
                            lov.update({c_mode: DispersionCurve(
                                cfrq, [1/x for x in camp])})
                    c_mode = int(re.findall(exp2, line)[0])
                    cfrq, camp = [], []
                else:
                    continue

        # Update from last loop.
        if modetype == "r":
            ray.update({c_mode: DispersionCurve(cfrq, [1/x for x in camp])})
        elif modetype == "l":
            lov.update({c_mode: DispersionCurve(cfrq, [1/x for x in camp])})
        return cls(identifier=str(c_model), misfit=c_misfit, rayleigh=ray, love=lov)
