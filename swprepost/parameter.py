# This file is part of swprepost, a Python package for surface-wave
# inversion pre- and post-processing.
# Copyright (C) 2019-2020 Joseph P. Vantassel (jvantassel@utexas.edu)
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https: //www.gnu.org/licenses/>.

"""Parameter class definition."""

import warnings
import logging

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class Parameter():
    """Class for defining the bounds of an inversion parameter.

    Attributes
    ----------
    par_type : {'FX', 'FTL', 'LN', 'LR', 'CT', 'CD'}
        String to denote how the layering was defined. Specifically,
        'FX'  = Fixed
        'FTL' = Fixed Thickness Layers
        'LN'  = Layering by Number
        'LR'  = Layering Ratio
        'CT'  = Custom Thickness
        'CD'  = Custom Depth
    par_value, par_add_value : int or float
        Numerical values to provide context about the
        type of layering selected. `par_add_value` only used for
        three letter parameter types (i.e., 'FTL').
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

        return (list(lower), list(upper))

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

        return (list(par_rev))

    def __init__(self, lay_min, lay_max, par_min, par_max, par_rev,
                 lay_type="thickness"):
        """Initialize a `Parameter` object.

        Parameters
        ----------
        lay_min, lay_max : iterable
            Minimum and maximum thickness or depth of each layer,
            respectively.
        par_min, par_max : iterable
            Minimum and maximum potential value of the parameter,
            one `float` per layer.
        par_rev : iterable
            Indicate whether to allow parameter reversals, one
            `bool` per layer.
        lay_type : {'thickness', 'depth'}, optional
            Inidcate whether the layers are defined in terms of
            depth or thickness.
        """
        if lay_type == "thickness":
            self._par_type = "CT"
        elif lay_type == "depth":
            self._par_type = "CD"
        else:
            msg = f"lay_type={lay_type} not recognized, refer to documentation."
            raise NotImplementedError(msg)

        self.par_value = 0
        self.par_add_value = 0
        self.lay_min, self.lay_max = self.check_layers("lay_min", lay_min,
                                                       "lay_max", lay_max)
        self.par_min, self.par_max = self.check_layers("par_min", par_min,
                                                       "par_max", par_max)
        self.par_rev = self.check_rev(par_rev)
        self.linked = False

        if (len(self.lay_min) != len(self.par_min)) and (len(self.lay_min) != len(self.par_rev)):
            raise ValueError("Length of all inputs must be consistent.")

    @classmethod
    def from_fx(cls, value):
        """Instantiate `Parameter` object using Fixed (FX) layering.

        Parameters
        ----------
        value : {float, int}
            Value assigned to the parameter at all depths. Value
            will not be allowed to change with depth.
        Returns
        -------
            Instantiated `Parameter` object.
        """
        try:
            value = float(value)
        except:
            msg = f"`value` must be abel to be cast to `float`."
            raise TypeError(msg)

        if value <= 0:
            raise ValueError("`value` must be postive.")

        obj = cls(lay_min=[1824], lay_max=[1883],
                  par_min=[value], par_max=[value], par_rev=[False])
        obj._par_type = "FX"
        obj.par_value = value
        return obj

    @staticmethod
    def _check_wavelengths(wmin, wmax):
        """Check wavelength input.

        Specifically:
        1. Cast Wavelength to `float`.
        2. Wavelengths are > 0.
        3. Minimum wavelength is less than maximum wavelength.
        """
        wmin = float(wmin)
        wmax = float(wmax)

        # Check type and wavelength > 0.
        for val in [wmin, wmax]:
            if val <= 0:
                raise ValueError("Wavelength must be > 0.")

        # Compare wavelenghts
        if wmin > wmax:
            msg = "Minimum wavelength must be less than maximum wavelength. Swapping!"
            warnings.warn(msg)
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
            msg = "`factor` must be >=2. Setting `factor` equal to 2."
            warnings.warn(msg)
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
        """Calculate the minimum and maximum thicknesses for each layer
        using Fixed Thickness Layering (FTL).

        Parameters
        ----------
        nlayers : int
            Desired number of layers.
        thickness : float
            Thickness of each layer.

        Returns
        -------
        Tuple
            Tuple of lists indicating thicknesses of the form
            ([minthickness...], [maxthickness...]).

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

        Parameters
        ----------
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

        Returns
        -------
        Parameter
            Instantiated `Parameter` object.

        Note
        ----
        If a more detailed parameterization is desired than
        available here use the `dinver` user inferface to tweak the
        resulting `.param` file.

        """
        lay_min, lay_max = cls.depth_ftl(nlayers, thickness)
        par_min, par_max, par_rev = cls.min_max_rev(nlayers,
                                                    par_min, par_max, par_rev)

        obj = cls(lay_min, lay_max, par_min, par_max, par_rev)
        obj._par_type = "FTL"
        obj.par_value = nlayers
        obj.par_add_value = thickness

        return obj

    @staticmethod
    def depth_ln_thickness(wmin, wmax, nlayers, depth_factor=2,
                           increasing=False):
        """Calculate the minimum and maximum thickness for each layer
        using Layering by Number (LN).

        Parameters
        ----------
        wmin, wmax : float
            Minimum and maximum measured wavelengths from the
            fundemental mode Rayleigh wave dispersion respectively.
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

        Returns
        -------
        Tuple
            Tuple of lists indicating thicknesses of the form
            ([minthickness...], [maxthickness...]).

        """
        wmin, wmax = Parameter._check_wavelengths(wmin, wmax)

        if type(nlayers) != int:
            msg = f"`nlayers` must be `int`. Not {type(nlayers)}."
            raise TypeError(msg)
        if nlayers < 1:
            raise ValueError("Number of layers for must be >= 1.")

        depth_factor = Parameter.check_depth_factor(depth_factor)

        minthickness = wmin/3
        dmax = wmax/depth_factor
        maxthickness = dmax/nlayers if not increasing else dmax
        return ([minthickness]*nlayers, [maxthickness]*nlayers)

    @classmethod
    def from_ln_thickness(cls, wmin, wmax, nlayers, par_min, par_max, par_rev,
                          depth_factor=2, increasing=False,
                          increasing_factor=1.2):
        """Alternate constructor to instantiate a `Parameter` using
        LN or LNI.

        Use Layering by Number (LN) or Layering by Number Increasing
        (LNI) to define the `Parameter`.

        Parameters
        ----------
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

        Returns
        -------
        Parameter
            Instantiated `Parameter` object.
        """
        msg = "`from_ln_thickness` is deprecated use `from_ln_depth` instead"
        warnings.warn(msg, DeprecationWarning)

        if increasing:
            if type(increasing_factor) not in (int, float):
                msg = f"`increasing_factor` must be `int` or `float`, not {type(increasing_factor)}."
                raise TypeError(msg)
            if increasing_factor <= 0:
                raise ValueError("`increasing_factor` must be greater than 1.")

        lay_min, lay_max = cls.depth_ln_thickness(wmin, wmax, nlayers,
                                                  depth_factor, increasing)
        par_min, par_max, par_rev = cls.min_max_rev(nlayers,
                                                    par_min, par_max, par_rev)
        obj = cls(lay_min, lay_max, par_min, par_max, par_rev)
        obj._par_type = "LNI" if increasing else "LN-thickness"
        obj.par_value = nlayers if increasing else nlayers
        obj.par_add_value = increasing_factor if increasing else 0

        return obj

    @staticmethod
    def depth_ln_depth(wmin, wmax, nlayers, depth_factor=2):
        """Calculate the minimum and maximum depth for each layer
        using Layering by Number.

        Parameters
        ----------
        wmin, wmax : float
            Minimum and maximum measured wavelength from the
            fundemental mode Rayleigh wave disperison.
        nlayers : int
            Desired number of layers.
        depth_factor : [float, int], optional
            Factor by which the maximum wavelength is
            divided to estimate the maxium depth of profiling,
            default is 2.

        Returns
        -------
        Tuple
            Tuple of lists indicating depths of the form
            ([mindepth...], [maxdepth...]).
        """
        wmin, wmax = Parameter._check_wavelengths(wmin, wmax)

        if type(nlayers) != int:
            msg = f"`nlayers` must be `int`. Not {type(nlayers)}."
            raise TypeError(msg)
        if nlayers < 1:
            raise ValueError("Number of layers for must be >= 1.")

        depth_factor = Parameter.check_depth_factor(depth_factor)
        dmax = wmax/depth_factor
        dmin = wmin/3

        return ([dmin]*nlayers, [dmax]*nlayers)
        # minthickness = wmin/3

        # minthicknesses = []
        # for nlay in range(1, nlayers+1):
        #     minthicknesses.append(minthickness*nlay)

        # return (minthicknesses, [dmax]*nlayers)

    @classmethod
    def from_ln(cls, wmin, wmax, nlayers, par_min, par_max, par_rev,
                depth_factor=2):
        return cls.from_ln_depth(wmin=wmin, wmax=wmax, nlayers=nlayers,
                                 par_min=par_min, par_max=par_max,
                                 par_rev=par_rev, depth_factor=depth_factor)

    @classmethod
    def from_ln_depth(cls, wmin, wmax, nlayers, par_min, par_max, par_rev,
                      depth_factor=2):
        """Alternate constructor to instantiate a `Parameter` using LN.

        Use Layering by Number (LN) to define the `Parameter`.

        Parameters
        ----------
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

        Returns
        -------
        Parameter
            Instantiated `Parameter` object.

        """
        lay_min, lay_max = cls.depth_ln_depth(wmin, wmax, nlayers,
                                              depth_factor)
        par_min, par_max, par_rev = cls.min_max_rev(nlayers,
                                                    par_min, par_max, par_rev)

        obj = cls(lay_min, lay_max, par_min, par_max, par_rev)
        obj._par_type = "LN"
        obj.par_value = nlayers
        obj.par_add_value = 0

        return obj

    @staticmethod
    def depth_lr(wmin, wmax, lr, depth_factor=2):
        """Return minimum and maximum depth for each layer using the
        Layering Ratio approach developed by Cox and Teague (2016).

        Note that the Layering Ratio approach implemented here has been
        modified slightly to ensure the maximum depth of the last layer
        does not exceed dmax. Suggestions for solving this issue are
        hinted at in Cox and Teague (2016), but not provided explicitly.

        Parameters
        ----------
        wmin, wmax : float
            Minimum and maximum measured wavelength from the
            fundemental mode Rayleigh wave dispersion.
        lr : float
            Layering Ratio, this controls the number of layers and
            their potential thicknesses, refer to Cox and Teague
            2016 for details.
        depth_factor : [float, int], optional
            Factor by which the maximum wavelength is
            divided to estimate the maxium depth of profiling,
            default is 2.

        Returns
        -------
        Tuple
            Tuple of lists indicating depths of the form
            ([mindepth...], [maxdepth...]).

        """
        wmin, wmax = Parameter._check_wavelengths(wmin, wmax)

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
    def from_lr(cls, wmin, wmax, lr, par_min, par_max, par_rev,
                depth_factor=2):
        """Alternate constructor to instantiate a `Parameter` using LR.

        Use Layering Ratio (LR) to define the `Parameter`.

        Parameters
        ----------
        wmin, wmax : float
            Minimum and maximum measured wavelength from the
            fundemental mode Rayleigh wave dispersion.
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

        Returns
        -------
        Parameter
            Instantiated `Parameter` object.

        Note
        ----
        If a more detailed parameterization is desired than
        available here use the `dinver` user inferface to tweak the
        resulting `.param` file.

        """
        lay_min, lay_max = cls.depth_lr(wmin, wmax, lr, depth_factor)
        par_min, par_max, par_rev = cls.min_max_rev(len(lay_min),
                                                    par_min, par_max, par_rev)
        obj = cls(lay_min, lay_max, par_min, par_max, par_rev)
        obj._par_type = "LR"
        obj.par_value = lr
        return obj

    @property
    def lay_type(self):
        if self._par_type in ["FTL", "CT"]:
            return "thickness"
        else:
            return "depth"

    @classmethod
    def from_parameter_and_link(cls, par_min, par_max, par_rev,
                                existing_parameter, ptype="vs"):
        """Create `Parameter` from an existing `Parameter` and link.

        Parameters
        ----------
        par_min, par_max : float
            Minimum and maximum potential value of the parameter,
            applied to all layers.
        par_rev : bool, optional
            Indicate whether layers are allowed to reverse or not,
            default is `False` (i.e., no reversal allowed).
        existing_parameter : Parameter
            Instantiated `Parameter` object to which you wish to link
            the current parameter. 
        ptype : {'vs', 'pr', 'rh', 'vp'}, optional
            Inversion parameter, representated by the
            `existing_parameter`, default is `vs`.

        Returns
        -------
        Parameter
            Instantiated `Parameter` with the same layering as
            `existing_parameter`, but different bounds.

        Note
        ----
        If a more detailed parameterization is desired than
        available here use the `dinver` user inferface to tweak the
        resulting `.param` file.

        """
        obj = cls.clone(existing_parameter)

        length = len(obj.par_min)
        obj.par_min = [float(par_min) for _ in range(length)]
        obj.par_max = [float(par_max) for _ in range(length)]
        obj.par_rev = [float(par_rev) for _ in range(length)]

        linked_map = {"vs":"Vs", "vp":"Vp", "rh":"Rho", "pr":"Nu"}
        obj.linked = linked_map[ptype]
        return obj

    @classmethod
    def clone(cls, parameter):
        """Copy provided `Parameter` object."""
        return cls(parameter.lay_min, parameter.lay_max, parameter.par_min,
                   parameter.par_max, parameter.par_rev, parameter.lay_type)

    @staticmethod
    def make_rectangle(left, right, upper, lower):
        return ([left, left, right, right],
                [upper, lower, lower, upper])

    def plot(self, ax=None, show_example=True):
        # TODO (jpv): Add docstring.
        if ax is None:
            ax_was_none = True
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(3.5, 5))
        else:
            ax_was_none = False

        if show_example:
            depths = [0]
            values = []

        spacing = 0.1
        width = 1 - spacing
        for count, (upper, lower) in enumerate(zip(self.lay_min, self.lay_max)):
            left = count + spacing
            right = left + width

            if count == 1:
                label = "Permitted Domain for Each Layer"
            else:
                label = None

            if show_example:
                depths += [(upper+lower)/2]*2
                values += [left + width/2]*2

            ax.fill(*self.make_rectangle(left, right, upper, lower),
                    color="#3399ff", label=label)

            ax.text(left + width/2, upper, count+1,
                    horizontalalignment="center", verticalalignment="top")

        if show_example:
            depths = depths[:-2]
            depths.append(max(self.lay_max))
            ax.plot(values, depths, label="Example Profile",
                    color="#66ff66", linewidth=4)

        ax.text(0.95, 0.95, f"{len(self.lay_max)} Layers",
                horizontalalignment="right", verticalalignment="top",
                transform=ax.transAxes)
        ax.set_ylabel("Depth (m)")
        ax.set_ylim(max(self.lay_max), 0)
        ax.set_xticklabels([])
        ax.set_xticks([])

        if ax_was_none:
            ax.legend(loc="lower center",  bbox_to_anchor=(0.5, -0.15))
            fig.tight_layout(h_pad=1, w_pad=1, rect=(0, 0, 1, 1))

        return ax

    def __eq__(self, other):
        for attr in ["lay_min", "lay_max", "par_min", "par_max", "par_rev"]:
            my_vals = getattr(self, attr)
            ur_vals = getattr(other, attr)

            if len(my_vals) != len(ur_vals):
                return False
            for my_val, ur_val in zip(my_vals, ur_vals):
                if my_val != ur_val:
                    return False
        return True

    def __repr__(self):
        return f"Parameter(lay_min={self.lay_min}, lay_max={self.lay_max}, par_min={self.par_min}, par_max={self.par_max}, par_rev={self.par_rev}, lay_type={self._par_type})"
