"""This file contains the class definintion for `DispersionSuite`."""

import re
from swipp import Suite, DispersionCurve, DispersionSet
import logging
logging.Logger(name=__name__)


class DispersionSuite(Suite):
    """Class for handling suites of instantiated `DispersionSet`
    objects.

    Attributes:
        sets : list
            Container for instantiated `DispersionSet` objects.
        
        
    """
    @staticmethod
    def check_input(curveset, set_type):
        """Check inputs comply with the required format.
        
        Specifically:
            1. `curveset` is of type `set_type`.
        """
        if not isinstance(curveset, set_type):
            msg = f"Must be an instance of {type(set_type)}, not {type(curveset)}."
            raise TypeError(msg)

    def __init__(self, dispersionset):
        """Initialize a `DispersionSuite` object, from a `DispersionSet`
        object.

        Args:
            dispersionset : DispersionSet
                Initialized `DispersionSet` object.

        Returns:
            Instantiated DispersionSuite object.

        Raises:
            TypeError:
                If `dispersionset` is not of type `DispersionSet`.
        """
        self.check_input(dispersionset, DispersionSet)
        self.sets = [dispersionset]

    def append(self, dispersionset):
        """Append `DispersionSet` object to `DispersionSuite`.

        Args:
            Refer to meth: `__init__ <DispersionSuite.__init__>`.

        Returns:
            `None`, updates the attribute `sets`.

        Raises:
            TypeError:
                If `dispersionset` is not of type `DispersionSet`.
        """
        self.check_input(dispersionset, DispersionSet)
        self.sets.append(dispersionset)

    @property
    def ids(self):
        ids = []
        for cset in self.sets:
            ids.append(cset.identifier)
        return ids

    @property
    def misfits(self):
        msft = []
        for cset in self.sets:
            msft.append(cset.misfit)
        return msft

    @classmethod
    def from_geopsy(cls, fname):
        """Create `DispersionSuite` from a text file created by the 
        Geopsy command `gpdc`.

        Args:
            fname : str
                Name of file to be read, may be a relative or full path.
            ndc : int, optional
                Number of sets to extract, default is `None` so all 
                available sets will be extracted.
            nrayleigh, nlove : int, optional
                Number of Rayleigh and Love modes respectively, default
                is `None` so all available modes will be extracted.

        Returns:
            Instantiated `DispersionSuite` object.
        """
        with open(fname, "r") as f:
            lines = f.read().splitlines()
        c_model, c_mode, obj = None, None, None
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
                        # ray, lov, ell = {}, {}, {}
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
                            obj = cls(DispersionSet(identifier=str(
                                c_model), misfit=c_misfit, rayleigh=ray, love=lov))
                            c_model, c_misfit = model, misfit
                            set_count += 1
                        # If it is a new set, but not the first set, append.
                        elif model != c_model:
                            obj.append(DispersionSet(identifier=str(
                                c_model), misfit=c_misfit, rayleigh=ray, love=lov))
                            c_model, c_misfit = model, misfit
                            set_count += 1
                        # This must be the same model, so continue acquisition.
                        else:
                            continue
                elif line.endswith("Rayleigh dispersion mode(s)"):
                    modetype = "r"
                elif line.endswith("Love dispersion mode(s)"):
                    modetype = "l"
                elif line.endswith("Rayleigh ellipticity mode(s)"):
                    modetype = "e"
                elif line.startswith("# Mode"):
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

        # Either write or append data, depending if obj has been defined.
        if obj == None:
            obj = cls(DispersionSet(identifier=str(c_model),
                                    misfit=c_misfit, rayleigh=ray, love=lov))
        else:
            obj.append(DispersionSet(identifier=str(c_model),
                                     misfit=c_misfit, rayleigh=ray, love=lov))
        return obj

