"""Abstract parent class for Suite objects."""

# import matplotlib.pyplot as plt

class Suite():

    def __init__(self):
        pass
            
    @classmethod
    def check_input(cls, curveset, set_type, identifier, misfit):
        """Check inputs comply with the required format."""
        if not isinstance(curveset, set_type):
            raise TypeError(
                f"'{identifier}' must be an instance of {type(set_type)}, not {type(curveset)}.")
        if not isinstance(identifier, str):
            raise TypeError(
                f"'{identifier}' must be of type str, not {type(identifier)}.")
        if misfit != None:
            if type(misfit) not in [int, float]:
                raise ValueError(
                    f"'misfit' must be of type int or float, not {type(misfit)}.")
