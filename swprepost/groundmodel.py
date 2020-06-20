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

"""GroundModel class definiton."""

import logging

from scipy.io import savemat
import numpy as np

from swprepost import regex

logger = logging.getLogger(__name__)


class GroundModel():
    """Class for creating and manipulating `GroundModel` objects.

    Attributes
    ----------
    tk, vp, vs, rh : list
        Thickness, compression-wave velocity (Vp), shear-wave
        velcocity (Vs), and mass density defining each layer of the
        `GroundModel`, respectively.
    identifier : int, optional
        Model numeric identifier, default is 0.
    misfit : float, optional
        Model misfit, default is 0.0.

    """

    @staticmethod
    def check_input_type(**kwargs):
        """Check inputs are of the appropriate type.

        Specifically:
        1. Cast `GroundModel` input to a `list` of `float`.
        2. Cast meta-information (identifier and misfit to `int` and
        `float`).

        Parameters
        ----------
        **kwargs
            Keyword arguements containing name and value pairs.

        Raises
        ------
        TypeError
            If `values` do not pass the aforementioned criteria.

        """
        for key, value in kwargs.items():
            if key in ["thickness", "vp", "vs", "density"]:
                try:
                    kwargs[key] = [float(val) for val in value]
                except ValueError as e:
                    raise TypeError(f"{key} must be castable to float.", e)
            elif key in ["identifier"]:
                kwargs[key] = int(value)
            elif key in ["misfit"]:
                kwargs[key] = float(value)
            else:
                msg = f"Input arguement {key} not recognized."
                raise NotImplementedError(msg)
        return kwargs

    @staticmethod
    def check_input_value(**kwargs):
        """Check `values` have appropriate values.

        Specifically:
        1. Check that all `GroundModel` parameters are greater than
        zero.
        2. Check that identifer and misfit are greater than zero.
        3. Check that `vp` > `vs`.

        Parameters
        ----------
        **kwargs
            Keyword arguements containing name and value pairs.

        Raises
        ------
        ValueError
            If inputs does not pass the aforementioned criteria.

        """
        tmp_len = len(kwargs["thickness"])
        for key in ["thickness", "vp", "vs", "density"]:
            value = kwargs[key]
            if tmp_len != len(value):
                raise ValueError(f"All inputs must have the same length.")
            for _val in value:
                if _val < 0:
                    raise ValueError(f"{key} must always be >= 0.")

        for key in ["identifier", "misfit"]:
            value = kwargs[key]
            if value < 0:
                raise ValueError(f"{key} must always be >= 0.")

        for _vp, _vs in zip(kwargs["vp"], kwargs["vs"]):
            if _vp <= _vs:
                msg = f"vp must be greater than vs, {_vp}!>{_vs}."
                raise ValueError(msg)

    def check_input(self, **kwargs):
        """Check input values and types."""
        kwargs = self.check_input_type(**kwargs)
        self.check_input_value(**kwargs)
        return kwargs

    def __init__(self, thickness, vp, vs, density, identifier=0, misfit=0.0):
        """Initialize a `GroundModel` object.

        Parameters
        ----------
        thickness : iterable
            Container of `float` or `int` denoting layer thickness
            (one per layer) in meters starting from the ground
            surface.
        vp, vs : iterable
            Container of `float` or `int` denoting the P- and S-wave
            velocity of each layer in m/s.
        density : iterable 
            Container of `float` or `int` denoting the mass density
            of each layer in kg/m3.
        identifier : int, optional
            Model numeric identifier, default is 0.
        misfit : float, optional
            Model misfit, default is 0.0.

        Returns
        -------
        GroundModel
            Instantiated `GroundModel` object.

        Raises
        ------
        Various
            See
            :meth: `check_input_type <GroundModel.check_input_type` and
            :meth: `check_input_value <GroundModel.check_input_value`
            for details.

        """
        kwargs = self.check_input(thickness=thickness, vp=vp, vs=vs,
                                  density=density, identifier=identifier,
                                  misfit=misfit)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def tk(self):
        return self.thickness

    @property
    def rh(self):
        return self.density

    @property
    def nlay(self):
        return len(self.tk)

    @staticmethod
    def calc_pr(vp, vs):
        """Calculate Poisson's ratio from iterable of `vp` and `vs`.

        Parameters
        ----------
        vp, vs : float, int, or iterable
            Vp and Vs values, respectively

        Returns
        -------
        float or list
            Poisson's ratio, calculated from each vp, vs pair.

        Raises
        ------
        ValueError
            If vs>vp or Poisson's ratio is negative
            (i.e., vp/vs too close to 1).

        """
        if isinstance(vp, (float, int)):
            vp = [vp]
            vs = [vs]

        pr = []
        for _vp, _vs in zip(vp, vs):
            if _vp <= _vs:
                raise ValueError(f"`Vp` must be greater than `Vs`.")
            x = (_vp*_vp)/(_vs*_vs)
            pr.append((2-x)/(2-2*x))
            if pr[-1] <= 0:
                msg = f"Poison's ratio cannot be negative. Vp/Vs={_vp}/{_vs} too close to unity."
                raise ValueError(msg)
        if len(pr) == 1:
            return pr[0]
        else:
            return pr

    @classmethod
    def from_simple_profiles(cls, vp_tk, vp, vs_tk, vs, rh_tk, rh):
        """Instantiate `GroundModel` from simple profiles.

        Parameters
        ----------
        vp_tk, vs_tk, rh_tk : iterable
            Iterable denoting the thicknesses of each parameter, one
            per layer.
        vp, vs, rh : iterable
            Iterable denoting the value of Vp, Vs, and mass density
            respectively.

        Returns
        -------
        GroundModel
            Instantiated `GroundModel` object.

        """
        new_depths = (cls.thick_to_depth(vp_tk) +
                      cls.thick_to_depth(vs_tk) +
                      cls.thick_to_depth(rh_tk))
        new_depths = list(dict.fromkeys(new_depths))
        new_depths.sort()

        def define_par(new_depths, new_par, tk, par):
            c_lay = 0
            for cid in range(len(new_depths)):
                # When thickness=0, apply last value to all remaining entries.
                if tk[c_lay] == 0:
                    new_par += [par[c_lay]]*(len(new_depths)-len(new_par))
                    return
                # Otherwise append current par value
                new_par.append(par[c_lay])
                # When depth is greater than sum of thickness move to next.
                if new_depths[cid+1] >= sum(tk[:c_lay+1]):
                    c_lay += 1

        new_vp, new_vs, new_rh = [], [], []
        define_par(new_depths, new_vp, vp_tk, vp)
        define_par(new_depths, new_vs, vs_tk, vs)
        define_par(new_depths, new_rh, rh_tk, rh)
        new_tk = cls.depth_to_thick(new_depths)
        return cls._gm()(new_tk, new_vp, new_vs, new_rh)

    @property
    def depth(self):
        """Return stair-step version of depth profile."""
        return self.gm2(parameter="depth")

    @property
    def vp2(self):
        """Return stair-step version of Vp profile."""
        return self.gm2(parameter="vp")

    @property
    def vs2(self):
        """Return stair-step version of Vs profile."""
        return self.gm2(parameter="vs")

    @property
    def rh2(self):
        """Return stair-step version of density profile."""
        return self.gm2(parameter="rh")

    @property
    def pr2(self):
        """Return stair-step version of Poisson's ratio profile."""
        return self.gm2(parameter="pr")

    @staticmethod
    def _validate_parameter(parameter, valid_parameters):
        if parameter not in valid_parameters:
            msg = f"parameter={parameter} is invalid, valid parameters include: {valid_parameters}."
            raise ValueError(msg)

    def gm2(self, parameter):
        """Parameter of `GroundModel` in stair-step form.

        Parameters
        ----------
        parameter : {'depth', 'vp', 'vs', 'density', 'pr'}
            Desired parameter to transform to stair-step profile.

        Returns
        -------
        list
            Defining the specified parameter. 

        Raises
        ------
        KeyError
            If `parameter` is not one of those specified.

        """
        valid_parameters = ["depth", "vp", "vs", "rh", "density", "pr"]
        self._validate_parameter(parameter, valid_parameters)

        if parameter == "pr":
            vp = self.gm2(parameter="vp")
            vs = self.gm2(parameter="vs")
            return self.calc_pr(vp, vs)

        if parameter == "depth":
            gm2 = [0]
            lay = 1
            for pnt in range(1, 2*self.nlay):
                if pnt == (2*self.nlay-1):
                    gm2.append(9999.0)
                else:
                    depth = sum(self.tk[:lay])
                    gm2.append(depth)
                    if pnt % 2 == 0:
                        lay += 1
        else:
            par = getattr(self, parameter)
            gm2 = [par[0]]
            lay = 1
            for pnt in range(1, 2*self.nlay):
                if pnt % 2 != 0:
                    gm2.append(par[lay-1])
                else:
                    gm2.append(par[lay])
                    lay += 1
        return gm2

    def discretize(self, dmax, dy=0.5, parameter='vs'):
        """Discretize a parameter of the `GroundModel`.

        The `GroundModel` is discretized in terms of depth from the
        surface to `dmax` by `dy` such that depth will be a `list` of
        the form `[0:dy:dmax]`. When the discretization encounters a
        parameter boundary the velocity of the upper layer is assigned.

        Do not use these discretized models for plotting unless `dy` is
        very small, as they may be misleading.

        Parameters
        ----------
        dmax : float
            Maximum depth of discretization.
        dy : float, optional
            Linear step of discretizaton in terms of depth, default
            is 0.5 meter.
        parameter : {'vp', 'vs', 'rh', 'pr'}, optional
            Parameter to be discretized, default is 'vs'.

        Returns
        -------
        Tuple
            Tuple of the form `(depth, param)` where `depth` is a `list`
            of the discretized depths, and `parameter` is a `list` of
            the discretized parameter at those depths.

        Raises
        ------
        KeyError
            If `parameter` is not one of those options specified.

        """
        # Use linspace to ensure start, end, and number of samples.
        disc_depth = np.linspace(0, dmax, int(round(dmax/dy))+1)
        disc_par = np.empty_like(disc_depth, dtype=float)

        if parameter == "pr":
            disc_par = self.calc_pr(self.discretize(dmax, dy, "vp")[1],
                                    self.discretize(dmax, dy, "vs")[1])
            return (disc_depth.tolist(), disc_par)

        valid_parameters = ["depth", "vp", "vs", "rh", "density", "pr"]
        self._validate_parameter(parameter, valid_parameters)
        par_to_disc = getattr(self, parameter)

        # For each layer
        start_index = 1
        disc_par[0] = par_to_disc[0]
        residual = 0

        for c_lay, c_tk in enumerate(self.tk):

            # Half-space
            if c_tk == 0:
                disc_par[start_index:] = par_to_disc[c_lay]
                break

            float_disc = c_tk/dy
            int_disc = int(c_tk/dy)
            residual += (float_disc - int_disc)
            if residual >= 1:
                int_disc += 1
                residual -= 1
            stop_index = start_index + int_disc

            # Layer extends beyond dmax
            if stop_index > len(disc_par):
                disc_par[start_index:] = par_to_disc[c_lay]
                break
            # Typical iteration
            else:
                disc_par[start_index:stop_index] = par_to_disc[c_lay]

            start_index = stop_index

        return (disc_depth.tolist(), disc_par.tolist())

    def simplify(self, parameter='vs'):
        """Remove unecessary breaks in the parameter specified.

        This will typically be used for calculating the median across
        many profiles.

        Parameter
        ---------
        parameter : {'vs','vp','rh','density'}, optional
            String denoting parameter to be simplified, default is 'vs'.

        Returns
        -------
        tuple
            Of the form `(thickness, parameter)` where `thickness` is a
            `list` of simplified thicknesses and `parameter` is a `list`
            of the simplified parameter.

        """
        valid_parameters = ["depth", "vp", "vs", "rh", "density", "pr"]
        self._validate_parameter(parameter, valid_parameters)
        par = getattr(self, parameter)
        tk = []
        spar = [par[0]]
        sum_ctk = self.tk[0]
        for cpar, ctk in zip(par[1:], self.tk[1:]):
            if cpar == spar[-1]:
                sum_ctk += ctk
            else:
                tk.append(sum_ctk)
                spar.append(cpar)
                sum_ctk = ctk
        tk.append(0)
        return (tk, spar)

    @property
    def vs30(self):
        """Calcualte Vs30 of the `GroundModel`.

        Vs0 is the time-averaged shear-wave velocity in the upper 30m.

        Returns
        -------
        float
            Vs30 of `GroundModel`.

        """
        depth = 0
        travel_time = 0
        for thickness, vs in zip(self.tk, self.vs):
            if thickness == 0:
                thickness = 30
            depth += thickness
            if depth >= 30:
                travel_time += (thickness-(depth-30))/vs
                break
            else:
                travel_time += thickness/vs
        return 30/travel_time

    def write_to_mat(self, fname_prefix):
        """Save `GroundModel` information to `.mat` format.

        Parameters
        ----------
        fname_prefix : str
            Name of file (excluding the `.mat` extension) where the file
            should be saved, may be a relative or the full path.

        Returns
        -------
        None
            Writes file to disk.

        """
        savemat(fname_prefix+".mat", {"thickness": self.tk,
                                      "vp1": self.vp,
                                      "vs1": self.vs,
                                      "rho1": self.rh,
                                      "depth": self.depth,
                                      "vp2": self.vp2,
                                      "vs2": self.vs2,
                                      "rho2": self.rh2,
                                      })

    @staticmethod
    def depth_to_thick(depths):
        """Convert depths (top of each layer) to thicknesses

        Parameters
        ----------
        depth : list
            List of consecutive depths.

        Returns
        -------
        list
            Thickness for each layer. Half-space is defined with zero
            thickness.

        """
        if depths[0] != 0:
            msg = "`depths` are defined from the top of each layer."
            raise ValueError(msg)

        # Half-space/single-layered system
        if len(depths) == 1:
            return [0]

        # Two-layered system
        if len(depths) == 2:
            return [depths[1], 0]

        # Multi-layered system
        thicknesses = [depths[1]]
        for cid in range(2, len(depths)):
            thicknesses.append(depths[cid]-depths[cid-1])
        thicknesses.append(0)
        return thicknesses

    @staticmethod
    def thick_to_depth(thicknesses):
        """Convert thickness to depth (at top of each layer).

        Parameters
        ----------
        thickness : list
            List of thicknesses defining a ground model.

        Returns
        -------
        list
            List of depths at the top of each layer.

        """
        depths = [0]
        for clayer in range(1, len(thicknesses)):
            depths.append(sum(thicknesses[:clayer]))
        return depths

    @property
    def txt_repr(self):
        """Text representation of the current `GroundModel`."""
        lines = f"{self.nlay}\n"
        for tk, vp, vs, rh in zip(self.tk, self.vp, self.vs, self.rh):
            lines += f"{tk} {vp} {vs} {rh}\n"
        return lines

    def write_model(self, fileobj):
        """Write model to open file object following `Geopsy` format.

        Parameters
        ----------
        fileobj : _io.TextIOWrapper
            Name of file, may be a relative or the full path.

        Returns
        -------
        None
            Writes file to disk.

        """
        fileobj.write(f"# Layered model {self.identifier}: value={self.misfit}\n")
        fileobj.write(self.txt_repr)

    def write_to_txt(self, fname):
        """Write `GroundModel` to file that follows the `Geospy` format.

        Parameters
        ----------
        fname : str
            Name of file, may contain a relative or the full path.

        Returns
        -------
        None
            Writes file to disk.

        """
        with open(fname, "w") as f:
            f.write(f"# Layered model {self.identifier}: value={self.misfit}\n")
            for line in self.txt_repr:
                f.write(line)

    @classmethod
    def _gm(cls):
        """Helper to allow conveinient subclassing."""
        return GroundModel

    @classmethod
    def _parse_gm(cls, gm_data, identifier, misfit):
        """Instantiate a `GroundModel` from lines of ground model text.

        This method should not be accessed directly. Use `from_geopsy`
        instead.

        Paramters
        ---------
        gm_data : str
            Text defining a GroundModel in the Geopsy format. If text
            defining multiple GroundModels is provided only the first
            one is parsed.
        identifier : str
            Indentifier string.
        misfit : str
            Misfit string.

        Returns
        -------
        GroundModel
            Instantiated `GroundModel` object.

        """
        tks, vps, vss, rhs = [], [], [], []
        for gm in regex.gm_data.finditer(gm_data):
            tk, vp, vs, rh = gm.groups()

            tks.append(tk)
            vps.append(vp)
            vss.append(vs)
            rhs.append(rh)

            if tk == "0":
                break

        return cls._gm()(tks, vps, vss, rhs, identifier=identifier, misfit=misfit)

    @classmethod
    def from_geopsy(cls, fname):
        """Create from a text file following the `Geopsy` format.

        Parameters
        ----------
        fname : fname
            File name, may contain a relative or the full path.

        Returns
        -------
        GroundModel
            Initialized `GroundModel` object.

        Raises
        ------
        Various
            If file does not follow the `Geopsy` format.

        """
        with open(fname, "r") as f:
            lines = f.read()

        for model_info in regex.gm.finditer(lines):
            identifier, misfit, data = model_info.groups()
            break

        return cls._parse_gm(data, identifier, misfit)

    def __str__(self):
        """Human-readable representation of the `GroundModel`"""
        return self.txt_repr

    def __repr__(self):
        """Unambiguous representation of the `GroundModel`."""
        return f"GroundModel(thickness={self.tk}, vp={self.vp}, vs={self.vs}, density={self.rh})"

    def __eq__(self, other):
        """Define when GroundModel is equal to another object."""
        if not isinstance(self, GroundModel) or not isinstance(other, GroundModel):
            return False

        for attr in ["identifier", "misfit"]:
            my_val = getattr(self, attr)
            ur_val = getattr(other, attr)
            if my_val != ur_val:
                return False

        for attr in ["tk", "vp", "vs", "rh"]:
            my_vals = getattr(self, attr)
            ur_vals = getattr(other, attr)
            if len(my_vals) != len(ur_vals):
                return False
            else:
                for my_val, ur_val in zip(my_vals, ur_vals):
                    if my_val != ur_val:
                        return False
        return True
