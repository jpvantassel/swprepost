"""This file includes an abstract parent class for `Suite` objects."""

import logging
logging.Logger(name=__name__)


class Suite():

    def __init__(self):
        pass

    @classmethod
    def check_input(cls, curveset, set_type, identifier, misfit):
        """Check inputs comply with the required format."""
        if not isinstance(curveset, set_type):
            msg = f"'{identifier}' must be an instance of {type(set_type)}, not {type(curveset)}."
            raise TypeError(msg)

        if not isinstance(identifier, str):
            msg = f"'{identifier}' must be of type str, not {type(identifier)}."
            raise TypeError(msg)

        if misfit != None:
            if type(misfit) not in [int, float]:
                msg = f"'misfit' must be of type int or float, not {type(misfit)}."
                raise ValueError(msg)
