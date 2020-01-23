"""This file contains the class definintion for `DispersionSuite`."""

import re
from swipp import Suite, DispersionCurve, DispersionSet, regex
import concurrent.futures
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
    def from_geopsy(cls, fname, ndc="all", nrayleigh="all", nlove="all"):
        """Create `DispersionSuite` from a text file created by the 
        Geopsy module `gpdc`.

        Args:
            fname : str
                Name of file to be read, may be a relative or full path.
            ndc : int, optional
                Number of sets to extract, default is "all" so all 
                available sets will be extracted.
            nrayleigh, nlove : int, optional
                Number of Rayleigh and Love modes respectively, default
                is "all" so all available modes will be extracted.

        Returns:
            Instantiated `DispersionSuite` object.
        """
        with open(fname, "r") as f:
            lines = f.read().splitlines()
        lines.append(" ")

        # Find line numbers
        found_models, found_misfits, line_numbers = [], [], []
        for line_number, line in enumerate(lines):
            try:
                model, misfit = regex.model.findall(line)[0]

                if model not in found_models:
                    found_models.append(model)
                    found_misfits.append(misfit)
                    line_numbers.append(line_number)

                if len(found_models) == ndc:
                    break

            except IndexError:
                continue
        line_numbers.append(line_number)

        dc_sets = []
        for start_line, end_line in zip(line_numbers[:-1], line_numbers[1:]):
            dc_sets.append(DispersionSet._from_lines(lines[start_line:end_line],
                                                    nrayleigh=nrayleigh,
                                                    nlove=nlove))

        # Slow Parallel code ...
        # with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        #     processes = []
        #     for start_line, end_line in zip(line_numbers[:-1], line_numbers[1:]):
        #         processes.append(executor.submit(DispersionSet.from_lines, lines[start_line:end_line]))

        # dc_sets = []
        # for process in processes:
        #     dc_sets.append(process.result())

        obj = cls(dc_sets[0])

        if len(dc_sets) > 1:
            for dc_set in dc_sets[1:]:
                obj.append(dc_set)

        return obj

    def __getitem__(self, aslice):
        return self.sets[aslice]
