"""This file contains a class DispersionSet for handling sets of
dispersion curves which belong to a common velocity model.
"""

import re
import copy
from swipp import CurveSet, DispersionCurve
# TODO (jpv): Refactor DispersionSuite.from_geopsy so that it calls
# a DispersionSet.from_geopsy rather than the other way around.


class DispersionSet(CurveSet):
    """Class for handling sets of DispersionCurve objects which all
    belong to a common velocity model.

    Attributes:
        rayleigh: Dictionary of the form:
                {0:disp_curve_obj0,
                 1:disp_curve_obj1,
                ...
                 N:disp_curve_objN}
            where each key, 0, 1, and N in this case, represent the
            rayleigh wave mode number and disp_curve_obj the
            corresponding instantiated DispersionCurve object.
        love: Same as rayleigh but for the love-wave modes.
        
    """

    @classmethod
    def check_input_local(cls, identifier, misfit):
        """Check inputs comply with the required format."""
        if not isinstance(identifier, str):
            raise TypeError(
                f"'{identifier}' must be of type str, not {type(identifier)}.")
        if misfit != None:
            if type(misfit) not in [int, float]:
                raise ValueError(
                    f"'misfit' must be of type int or float, not {type(misfit)}.")


    def __init__(self, identifier, misfit=None, rayleigh=None, love=None,):
        """Initializes a DispersionSet object from a dictionary
        containing instantiated DispersionCurve objects.

        Args:
            identifier: String uniquely identifying the DispersionSet.
            misfit: Float or int denoting the DispersionSet's misfit.
            rayleigh: Dictionary of the form:
                    {0:disp_curve_obj0,
                     1:disp_curve_obj1,
                    ...
                     N:disp_curve_objN}
                where each key, 0, 1, and N in this case, represent the
                rayleigh wave mode number and disp_curve_obj the
                corresponding instantiated DispersionCurve object.
            love: Same as rayleigh but for the love-wave modes.

        """
        self.check_input([rayleigh, love], DispersionCurve)
        self.check_input_local(identifier, misfit)
        self.rayleigh = copy.deepcopy(rayleigh)
        self.love = copy.deepcopy(love)
        self.identifier = identifier
        self.misfit = misfit

    @classmethod
    def from_geopsy(cls, fname):
        """Create an instance of the DispersionSet class from a text
        file created by the geopsy command `gpdc`.

        Args:
            fname: Name of file to be read, may contain a relative or
                full path if desired.
            nrayleigh: Number of rayleigh modes. Default is None and will
                extract all available mode.
            nlove: Number of love modes. Default is None and will
                extract all available modes.

        Returns:
            An instance of the DipersionSet class.

        Raises:
            This method raises no exceptions.
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
