"""This file contains an abstract class CurveSet for handling sets of
curves which share some common source."""


class CurveSet():
    """Abstract class to handle sets of `Curve` objects.

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
    def check_input(cls, curvesets, valid_type):
        """Check that arguements 'rayleigh' and 'love' comply with the
        proper formating.
        """
        none_count = 0
        for curveset in curvesets:
            try:
                for key, value in curveset.items():
                    if not isinstance(value, valid_type):
                        raise TypeError(
                            f"{key} must be type {valid_type}, not {type(value)}.")
            except AttributeError:
                if curveset == None:
                    none_count += 1
                else:
                    raise TypeError(f"{key} must be dict, not {type(value)}.")
        if none_count == len(curvesets):
            raise TypeError("All values cannot be None.")

    def __init__(self):
        """Initializes a CurveSet object from a dictionary or list of 
        dictionaries containing instantiated derived Curve objects.

        Args:
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
        pass
    
