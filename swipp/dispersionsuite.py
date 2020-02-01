"""This file contains the class `DispersionSuite`."""

from swipp import DispersionSet, Suite, regex
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
            msg = f"Must be instance of {type(set_type)}, not {type(curveset)}."
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
            Refer to :meth: `__init__ <DispersionSuite.__init__>`.

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
        """Return the ids correspinding to `sets`."""
        ids = []
        for cset in self.sets:
            ids.append(cset.identifier)
        return ids

    @property
    def misfits(self):
        """Return the misfits correspinding to `sets`."""
        msft = []
        for cset in self.sets:
            msft.append(cset.misfit)
        return msft

    @classmethod
    def from_geopsy(cls, fname, nsets="all", nrayleigh="all", nlove="all"):
        """Create `DispersionSuite` from a text file following the
        Geopsy format.

        Args:
            fname : str
                Name of file to be read, may be a relative or full path.
            nsets : int, optional
                Number of sets to extract, default is "all" so all 
                available sets will be extracted.
            nrayleigh, nlove : int, optional
                Number of Rayleigh and Love modes respectively, default
                is "all" so all available modes will be extracted.

        Returns:
            Instantiated `DispersionSuite` object.
        """
        with open(fname, "r") as f:
            lines = f.read()

        dc_sets = []
        previous_id, previous_misfit = "start", "0"
        rayleigh, love = None, None
        model_count = 0
        for model_info in regex.dcset.finditer(lines):
            identifier, misfit, wave_type, data = model_info.groups()

            if identifier != previous_id and previous_id != "start":
                dc_sets.append(cls._dcset()(previous_id,
                                            float(previous_misfit),
                                            rayleigh=rayleigh, love=love))
                model_count += 1
                rayleigh, love = None, None

            if wave_type == "Rayleigh":
                rayleigh = cls._dcset()._parse_dcs(data, nmodes=nrayleigh)
            elif wave_type == "Love":
                love = cls._dcset()._parse_dcs(data, nmodes=nlove)
            else:
                raise NotImplementedError

            previous_id = identifier
            previous_misfit = misfit

            if model_count + 1 == nsets:
                break

        dc_sets.append(cls._dcset()(previous_id,
                                    float(previous_misfit),
                                    rayleigh=rayleigh, love=love))
        return cls.from_list(dc_sets)

    @classmethod
    def _dcset(cls):
        return DispersionSet

    @classmethod
    def from_list(cls, dc_sets):
        """Create `DispersionSuite` from a list of `DispersionSet`
        objects.

        Args:
            dc_sets : list
                List of `DispersionSet` objects.

        Returns:
            Instatiated `DispersionSuite`.
        """
        obj = cls(dc_sets[0])
        if len(dc_sets) > 1:
            for dc_set in dc_sets[1:]:
                obj.append(dc_set)
        return obj

    def __getitem__(self, slce):
        return self.sets[slce]

    def __repr__(self):
        return f"DispersionSuite with {len(self.sets)} DispersionSets."
