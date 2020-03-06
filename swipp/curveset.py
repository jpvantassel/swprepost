"""This file contains the class `CurveSet`."""


#TODO (jpv): What is a curveset

class CurveSet():
    """Class for handling sets of `Curve` objects with some common
    source or purpose.
    """

    @classmethod
    def check_input(cls, curvesets, valid_type):
        """Check that the `curvesets` each comply with the proper
        formating.

        Specifically:
            1. Assume `curvesets` is an iterable container of `dicts`.
            2. Check that all values of those `dicts` are of type 
            `valid_type`.
            3. If the entry in `curvesets` is not `dict`, check if it is
            `None`. In this case there must be at least one non-None
            entry in `curvesets`.
            4. If entry is not `dict` or `None` raise `TypeError`.
        """
        none_count = 0
        for curveset in curvesets:
            try:
                for key, value in curveset.items():
                    if not isinstance(value, valid_type):
                        msg =f"{key} must be a {valid_type}, not {type(value)}."
                        raise TypeError(msg)
            except AttributeError:
                if curveset is None:
                    none_count += 1
                else:
                    msg = f"must be `dict`, not {type(curveset)}."
                    raise TypeError(msg)
        if none_count == len(curvesets):
            raise TypeError("All values cannot be `None`.")

    def __init__(self):
        pass
    
