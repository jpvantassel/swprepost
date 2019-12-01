"""This file includes the defnition of the Parameter class."""

import warnings
import logging
logging.Logger(name=__name__)


class Parameter():
    """Class for defining the bounds of an inversion parameter.

    Attributes:
        par_type : {'FX', 'FTL', 'LN', 'LNI' 'LR', 'CT', 'CD'}
            String to denote how the layering was defined.
        par_value,  par_add_value : [int, float]
            Numerical values to provide context about the
            type of layering selected. `par_add_value` only used for
            three letter parameter types (i.e., 'FTL' and 'LNI').
        lay_min, lay_max : list
            Minimum and maximum thickness or depth of each layer,
            respectively.
        par_min, par_max : list
            Minimum and maximum potential value of the parameter, one
            `float` value per layer.
        par_rev : list
            Indicate whether to allow parameter reversals, one `bool`
            value per layer.
    """
    @staticmethod
    def check_layers(lower_name, lower, upper_name, upper):
        """Check layering input.

        Specifically:
            1. Check that `lower` and `upper` are the same length.
            2. Ensure that each value for `lower` is less than the
            corresponding value for `upper`.
        """
        # Check length.
        if len(lower) != len(upper):
            msg = f"`{lower_name}` and `{upper_name}` must be the same length."
            raise ValueError(msg)

        # Check values.
        for index, (clower, cupper) in enumerate(zip(lower, upper)):
            if clower > cupper:
                msg = f"`{upper_name}[{index}]` must be greater than `{lower_name}[{index}]`."
                raise ValueError(msg)

        return (lower, upper)

    @staticmethod
    def check_rev(par_rev):
        """Check reversal input.

        Specifically:
            1. `par_rev` is a list of `bool`s.
        """
        # Check type
        for cpar in par_rev:
            if type(cpar) != bool:
                msg = "`par_rev` must be an iterable composed of `bool`s."
                raise TypeError(msg)

        return (par_rev)

    def __init__(self, par_type, lay_min, lay_max, par_min, par_max, par_rev):
        """Initialize a `Parameter` object.

        Args:
            lay_min, lay_max : list
                Minimum and maximum thickness or depth of each layer,
                respectively.
            par_min, par_max : list
                Minimum and maximum potential value of the parameter,
                one `float` per layer.
            par_rev : list
                Indicate whether to allow parameter reversals, one 
                `bool` per layer.             
        """
        self.par_type = par_type
        self.par_value = 0
        self.par_add_value = 0
        self.lay_min, self.lay_max = self.check_layers("lay_min", lay_min,
                                                       "lay_max", lay_max)
        self.par_min, self.par_max = self.check_layers("par_min", par_min,
                                                       "par_max", par_max)
        self.par_rev = self.check_rev(par_rev)

        if (len(self.lay_min) != len(self.par_min)) and (len(self.lay_min) != len(self.par_rev)):
            msg = "Length of all inputs must be consistent."
            raise ValueError(msg)

    @classmethod
    def from_fx(cls, value):
        """Instantiate `Parameter` object using Fixed (FX) layering.

        Args:
            value : [float, int]
                Value assigned to the paramter at all depths, will not
                be allowed to change with depth.
        Returns:
            Instantiated `Parameter` object.
        """
        if type(value) not in [int, float]:
            msg = f"`value` must be an `int` or `float`, not {type(value)}."
            raise TypeError(msg)
        if value <= 0:
            raise ValueError("`value` must be postive.")

        obj = cls(par_type="FX", lay_min=[1824], lay_max=[1883],
                  par_min=[value], par_max=[value], par_rev=[False])
        obj.par_value = value
        return obj

    @staticmethod
    def check_wavelengths(wmin, wmax):
        """Check wavelength input.

        Specifically:
            1. Wavelengths are `int` or `float`.
            2. Wavelengths are > 0.
            3. Minimum wavelength is less than maximum wavelength.
        """
        # Check type and wavelength > 0.
        for val in [wmin, wmax]:
            if type(val) not in (int, float):
                msg = f"Wavelength must be of type `int` or `float`. Not `{type(val)}`."
                raise TypeError(msg)
            if val <= 0:
                raise ValueError("Wavelength must be > 0.")

        # Compare wavelenghts
        if wmin > wmax:
            msg = "Minimum wavelength must be less than maximum wavelength. Swapping!"
            logging.warning(msg)
            wmin, wmax = wmax, wmin

        return (wmin, wmax)

    @staticmethod
    def check_depth_factor(depth_factor):
        """Check input value for factor."""
        if type(depth_factor) not in (int, float):
            msg = f"`factor` must be `int` or `float`. Not {type(depth_factor)}."
            raise TypeError(msg)
        if depth_factor < 2:
            depth_factor = 2
            logging.warning(
                "`factor` must be >=2. Setting `factor` equal to 2.")
        return depth_factor

    @staticmethod
    def min_max_rev(nlayers, par_min, par_max, par_rev):
        """Create list for par_min, par_max, par_rev."""
        par_min = [par_min]*nlayers
        par_max = [par_max]*nlayers
        par_rev = [par_rev]*nlayers
        return (par_min, par_max, par_rev)

    @staticmethod
    def depth_ftl(nlayers, thickness):
        """Calculate the minimum and maximum thickness for each layer
        using Fixed Thickness Layering.

        Args:
            nlayers : int
                Desired number of layers.
            thickness : float
                Thickness of each layer.

        Returns:
            Tuple of lists indicating thicknesses of the form
            ([minthickness...], [maxthickness...]).

        Example:
        TODO (jpv): Example
        """
        if type(nlayers) != int:
            raise TypeError(f"`nlayers` must be `int`, not {type(nlayers)}.")
        if nlayers <= 0:
            raise ValueError("`nlayers` must be positive.")

        if type(thickness) not in (int, float):
            msg = f"`thickness` must be `int` or `float`, not {type(thickness)}."
            raise TypeError(msg)
        if thickness <= 0:
            raise ValueError("`thickness` must be postive.")

        return ([thickness]*nlayers, [thickness]*nlayers)

    @classmethod
    def from_ftl(cls, nlayers, thickness, par_min, par_max, par_rev=False):
        """Alternate constructor to instantiate a `Parameter` using FTL.

        Use Fixed Thickenss Layering (FTL) to define the
        parameterization.

        Args:
            nlayers : int
                Number of desired layers.
            thickness : float
                Thickness of all layers in meters.
            par_min, par_max : float
                Minimum and maximum potential value of the parameter,
                applied to all layers. 
            par_rev : bool, optional
                Indicate whether layers are allowed to reverse or not,
                default is `False` (i.e., no reversal allowed).

        Returns:
            Instantiated `Parameter` object.

        Note: 
            If a more detailed parameterization is desired than
            available here use the `dinver` user inferface to tweak the
            resulting `.target` file.
        """
        lay_min, lay_max = cls.depth_ftl(nlayers, thickness)
        par_min, par_max, par_rev = cls.min_max_rev(nlayers,
                                                    par_min, par_max, par_rev)

        obj = cls("FTL", lay_min, lay_max, par_min, par_max, par_rev)
        obj.par_value = nlayers
        obj.par_add_value = thickness

        return obj

    @staticmethod
    def depth_ln(wmin, wmax, nlayers, depth_factor=2, increasing=False):
        """Calculate the minimum and maximum thickness for each layer 
        using Layering by Number.

        Args:
            wmin, wmax : float
                Minimum and maximum measured wavelength from the
                fundemental mode Rayleigh wave disperison.
            nlayers : int
                Desired number of layers.
            depth_factor : [float, int], optional
                Factor by which the maximum wavelength is
                divided to estimate the maxium depth of profiling,
                default is 2.
            increasing : bool, optional
                Indicate whether the layering thickness should be 
                contrained to increase, default value is `False`
                meaning that layers are not contrained to increase.

        Returns:
            Tuple of lists indicating thicknesses of the form
            ([minthickness...], [maxthickness...]).

        Example:
            TODO (jpv): Example
        """
        wmin, wmax = Parameter.check_wavelengths(wmin, wmax)

        if type(nlayers) != int:
            msg = f"`nlayers` must be `int`. Not {type(nlayers)}."
            raise TypeError(msg)
        if nlayers < 2:
            raise ValueError("Number of layers for must be >= 2.")

        depth_factor = Parameter.check_depth_factor(depth_factor)

        minthickness = wmin/3
        dmax = wmax/depth_factor
        maxthickness = dmax/nlayers if not increasing else dmax
        return ([minthickness]*nlayers, [maxthickness]*nlayers)

    @classmethod
    def from_ln(cls, wmin, wmax, nlayers, par_min, par_max, par_rev, depth_factor=2, increasing=False, increasing_factor=1.2):
        """Alternate constructor to instantiate a `Parameter` using LN
        or LNI.

        Use Layering by Number (LN) or Layering by Number Increasing
        (LNI) to define the `Parameter`.

        Args:
            wmin, wmax : float
                Minimum and maximum measured wavelength from the
                fundemental mode Rayleigh wave disperison.
            nlayers : int
                Desired number of layers.
            par_min, par_max : float
                Minimum and maximum potential value of the parameter,
                applied to all layers. 
            par_rev : bool, optional
                Indicate whether layers are allowed to reverse or not,
                default is `False` (i.e., no reversal allowed).
            depth_factor : [float, int], optional
                Factor by which the maximum wavelength is
                divided to estimate the maxium depth of profiling,
                default is 2.
            increasing : bool, optional
                Determines whether LN or LNI layering is used, default
                is `False` meaning LN is used.
            increasing_factor : float, optional
                Factor by which each subsequent layer must be thicker
                than the previous layer previous layer, default is 1.2.
                Arguement is only used if `increasing=True`.

        Returns:
            Instantiated `Parameter` object.
        """

        if increasing:
            if type(increasing_factor) not in (int, float):
                msg = f"`increasing_factor` must be `int` or `float`, not {type(increasing_factor)}."
                raise TypeError(msg)
            # TODO (jpv): Consider whether this is really necessary.
            if increasing_factor <= 1:
                raise ValueError("`increasing_factor` must be greater than 1.")

        lay_min, lay_max = cls.depth_ln(wmin, wmax, nlayers,
                                        depth_factor, increasing)
        par_min, par_max, par_rev = cls.min_max_rev(nlayers,
                                                    par_min, par_max, par_rev)
        par_type = "LNI" if increasing else "LN"
        obj = cls(par_type, lay_min, lay_max, par_min, par_max, par_rev)
        obj.par_value = nlayers if increasing else nlayers
        obj.par_add_value = increasing_factor if increasing else 0
        
        return obj

    @staticmethod
    def depth_lr(wmin, wmax, lr, depth_factor=2):
        """Return minimum and maximum depth for each layer using the
        Layering Ratio approach developed by Cox and Teague (2016).

        Note that the Layering Ratio approach implemented here has been
        modified slightly to ensure the maximum depth of the last layer
        does not exceed dmax, as guidance on this particular issue is
        not provided explicitly in Cox and Teague (2016). 

        Args:
            wmin, wmax : float
                Minimum and maximum measured wavelength from the
                fundemental mode Rayleigh wave disperison.
            lr : float
                Layering Ratio, this controls the number of layers and
                their potential thicknesses, refer to Cox and Teague
                2016 for details.
            depth_factor : [float, int], optional
                Factor by which the maximum wavelength is
                divided to estimate the maxium depth of profiling,
                default is 2.

        Returns:
            Tuple of lists indicating depths of the form
            ([mindepth...], [maxdepth...]).

        Example:
            TODO (jpv): Example
        """
        wmin, wmax = Parameter.check_wavelengths(wmin, wmax)

        if type(lr) not in (int, float):
            msg = f"`lr` must be `int` or `float`, not {type(lr)}."
            raise TypeError(msg)
        if lr <= 1:
            raise ValueError("`lr` must be greater than 1.")
        depth_factor = Parameter.check_depth_factor(depth_factor)

        layer_mindepth = [wmin/3]
        layer_maxdepth = [wmin/2]
        dmax = wmax/depth_factor
        laynum = 1
        while layer_maxdepth[-1] < dmax:
            layer_mindepth.append(layer_maxdepth[-1])
            if laynum == 1:
                layer_maxdepth.append(
                    layer_maxdepth[-1]*lr + layer_maxdepth[-1])
            else:
                layer_maxdepth.append(
                    (layer_maxdepth[-1]-layer_maxdepth[-2])*lr + layer_maxdepth[-1])
            laynum += 1

        # If the distance between the deepest potential depth of the
        # bottom-most layer and dmax is greater than the potential
        # thickness of the bottom-most layer:
        # ---> Add a new layer
        if (dmax - layer_maxdepth[-2]) > (layer_maxdepth[-2] - layer_maxdepth[-3]):
            # Set the current max depth (which is > dmax) equal to dmax
            layer_maxdepth[-1] = dmax
            # Add half-space starting at dmax
            layer_mindepth.append(dmax)
            layer_maxdepth.append(dmax+1)  # Half-space
        # ---> Otherwise, extend the current last layer
        else:
            # Extend the deepest potential depth of the bottomost layer
            # to dmax.
            layer_maxdepth[-2] = dmax
            # Set the old last layer to the half-space
            layer_mindepth[-1] = dmax
            layer_maxdepth[-1] = dmax+1  # Half-space
        return (layer_mindepth, layer_maxdepth)

    @classmethod
    def from_lr(cls, wmin, wmax, lr, par_min, par_max, par_rev, depth_factor=2):
        """Alternate constructor to instantiate a `Parameter` using LR.

        Use Layering Ratio (LR) to define the `Parameter`.

        Args:
            wmin, wmax : float
                Minimum and maximum measured wavelength from the
                fundemental mode Rayleigh wave disperison.
            lr : float
                Layering Ratio, this controls the number of layers and
                their potential thicknesses, refer to Cox and Teague
                (2016) for details.                
            par_min, par_max : float
                Minimum and maximum potential value of the parameter,
                applied to all layers. 
            par_rev : bool, optional
                Indicate whether layers are allowed to reverse or not,
                default is `False` (i.e., no reversal allowed).
            depth_factor : [float, int], optional
                Factor by which the maximum wavelength is
                divided to estimate the maxium depth of profiling,
                default is 2.

        Returns:
            Instantiated `Parameter` object.

        Note: 
            If a more detailed parameterization is desired than
            available here use the `dinver` user inferface to tweak the
            resulting `.target` file.
        """
        lay_min, lay_max = cls.depth_lr(wmin, wmax, lr, depth_factor)
        par_min, par_max, par_rev = cls.min_max_rev(len(lay_min),
                                                    par_min, par_max, par_rev)
        obj = cls("LR", lay_min, lay_max, par_min, par_max, par_rev)
        obj.par_value = lr
        return obj
