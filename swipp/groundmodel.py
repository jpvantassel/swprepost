"""This file contains the class definiton for `GroundModel`."""

import scipy.io as sio
import copy
import warnings
import logging
import subprocess
import numpy as np
import re
from swipp import DispersionSet, regex
import os
logging.Logger(name=__name__)


class GroundModel():
    """Class for creating and manipulating `GroundModel` objects.

    Attributes:
        tk:
        vp:
        vs:
        rh:
    """
    # TODO (jpv): Complete documentation.
    
    @staticmethod
    def check_input_type(values, names):
        """Check `values` are of the appropriate type.

        Specifically:
            1. `values` are an interable of `list`. If necessary convert 
            interable of `ndarray` or `tuple` to interable of `list`.
            2. Entries of the inner `list` are of type `int` or `float`.

        Args:
            values : list
                Container of `list` one per parameter.
            names : list
                Container of `str` used for meaningful error messages.

        Raises:
            TypeError:
                If `values` does not pass the aforementioned criteria.
        """
        for cid, (value, name) in enumerate(zip(values, names)):
            if type(value) not in [list, tuple, np.ndarray]:
                msg = f"{name} must be of type `list`, not {type(value)}."
                raise TypeError(msg)
            if isinstance(value, tuple):
                values[cid] = list(value)
            if isinstance(value, np.ndarray):
                values[cid] = value.tolist()

        for value, name in zip(values, names):
            for val in value:
                if type(val) not in [int, float]:
                    msg = f"{name} must be a `list` of `int` or `float`, not {type(val)}."
                    raise TypeError(msg)

        return values

    @staticmethod
    def check_input_value(values, names):
        """Check `values` have appropriate values.

        Specifically:
            1. Check that all values are greater than zero.
            2. Check that `vp` > `vs`.

        Args:
            values : list
                Container of `list` one per parameter.
            names : list
                Container of `str` used for meaningful error messages.

        Raises:
            ValueError:
                If `values` does not pass the aforementioned criteria.
        """

        tmp_len = len(values[0])
        for value, name in zip(values, names):
            for val in value:
                if val < 0:
                    raise ValueError(f"{name} must always be >= 0.")
            if tmp_len != len(value):
                raise ValueError(f"All inputs must have the same length.")

        for tmp_vp, tmp_vs in zip(values[names == "vp"], values[names == "vs"]):
            if tmp_vs > tmp_vp:
                msg = f"vp must be greater than vs, {tmp_vp}!>{tmp_vs}."
                raise ValueError(msg)

    def __init__(self, thickness, vp, vs, density):
        """Initialize a ground model object

        Args:
            thickness : list
                Container of `float` or `int` denoting layer thickness
                (one per layer) in meters starting from the ground
                surface.
            vp, vs : list
                Container of `float` or `int` denoting the P- and S-wave
                velocity of each layer in m/s.
            density : list 
                Container of `float` or `int` denoting the mass density
                of each layer in kg/m3.

        Returns:
            Instantiated GroundModel object

        Raises:
            Various exceptions, see
            :meth: `check_input_type <GroundModel.check_input_type` and
            :meth: `check_input_value <GroundModel.check_input_value`
            for details.
        """
        thickness, vp, vs, density = self.check_input_type([thickness, vp, vs, density],
                                                           ["thickness", "vp", "vs", "density"])
        self.check_input_value([thickness, vp, vs, density],
                               ["thickness", "vp", "vs", "density"])
        self.nlay = len(thickness)
        self.tk = copy.deepcopy(thickness)
        self.vp = copy.deepcopy(vp)
        self.vs = copy.deepcopy(vs)
        self.rh = copy.deepcopy(density)

    @staticmethod
    def calc_pr(vp, vs):
        """Calculate Poisson's ratio from list of `vp` and `vs`.

        Args:
            vp, vs : iterable
                Container of vp and vs values.

        Returns:
            `List` of Poisson's ratio, calculated from each vp, vs pair.

        Raises:
            ValueError: 
                If vs>vp, or Poisson's ratio is negative.
        """
        if type(vp) in [int, float]:
            warnings.warn("`vp` should be an iterable type.")
            vp = [vp]
        if type(vs) in [int, float]:
            warnings.warn("`vs` should be an iterable type.")
            vs = [vs]
        pr = []
        for vp, vs in zip(vp, vs):
            if vp <= vs:
                raise ValueError(f"`Vp` must be greater than `Vs`.")
            pr += [(2-(vp/vs)**2)/(2-2*(vp/vs)**2)]
            if pr[-1] <= 0:
                msg = f"Poison's ratio cannot be negative. Vp/Vs={vp}/{vs} too close to unity."
                raise ValueError(msg)
        return pr

    @classmethod
    def from_simple_profiles(cls, vp_tk, vp, vs_tk, vs, rh_tk, rh):
        """Instantiate `GroundModel` from simple profiles.

        Args:
            vp_tk, vs_tk, rh_tk : list
                Container of `int` or `float` denoting the thicknesses
                of each parameter, one per layer.
            vp, vs, rh : list
                Container of `int` or `float` for the value of each
                parameter. 

        Returns:
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
                # When depth is greater than sum of thickness move to next layer.
                if new_depths[cid+1] >= sum(tk[:c_lay+1]):
                    c_lay += 1

        new_vp, new_vs, new_rh = [], [], []
        define_par(new_depths, new_vp, vp_tk, vp)
        define_par(new_depths, new_vs, vs_tk, vs)
        define_par(new_depths, new_rh, rh_tk, rh)
        new_tk = cls.depth_to_thick(new_depths)
        return cls.mkgm(new_tk, new_vp, new_vs, new_rh)

    @property
    def thickness(self):
        return self.tk

    @property
    def density(self):
        return self.rh

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
        return self.gm2(parameter="rho")
    
    @property
    def pr2(self):
        """Return stair-step version of Poisson's ratio profile."""
        return self.gm2(parameter="pr")

    def gm2(self, parameter):
        """Return parameter of `GroundModel` in stair-step form.

        Args:
            parameter : {'depth', 'vp', 'vs', 'rho', 'pr'}
                Desired parameter.

        Returns:
            List of defining the specified parameter. 

        Raises:
            KeyError if `parameter` is not one of those specified.
        """
        if parameter == "pr":
            vp = self.gm2(parameter="vp")
            vs = self.gm2(parameter="vs")
            return self.calc_pr(vp, vs)

        options = {"depth": self.tk, "vp": self.vp,
                   "vs": self.vs, "rho": self.rh}
        par = options[parameter]

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
        """Returns a discretized stair-step model.

        The stair step model is discretized by depth from the surface to
        dmax by dy such that depth will be a list of the forn
        [0:dy:dmax]. When the discretization encounters a stair tred
        (i.e., where two velocities are specified at a single depth) the
        velocity of the upper layer is assigned. Do not use these
        discretized models for plotting as they may be misleading.

        Args:
            dmax : float
                Maximum depth of discretization.
            dy : float, optional
                Linear step of discretizaton in terms of depth, default
                is 0.5 meter.
            parameter : {'vp', 'vs', 'rho', 'pr'}, optional
                Parameter to be discretized, default is 'vs'.

        Returns:
            Tuple of the form `(depth, param)` where `depth` is a `list`
            of the discretized depths, and `parameter` is a `list` of
            the discretized parameter at those depths.

        Raises:
            KeyError:
                If `param` is not one of those options specified.
        """
        disc_depth = np.linspace(0, dmax, int(dmax//dy)+1).tolist()

        if parameter == "pr":
            disc_par = self.calc_pr(self.discretize(dmax, dy, "vp")[1],
                                    self.discretize(dmax, dy, "vs")[1])
            return (disc_depth, disc_par)

        options = {"vp": self.vp, "vs": self.vs, "rho": self.rh}
        try:
            par_to_disc = options[parameter]
        except KeyError:
            msg = f"Bad `parameter`={parameter}, try 'vp', 'vs', 'rho', or 'pr'."
            raise KeyError(msg)
        
        # For each layer
        disc_par = [par_to_disc[0]]
        residual = 0
        if len(self.tk) > 1:
            for c_lay, c_tk in enumerate(self.tk[:-1]):
                float_disc = c_tk/dy
                int_disc = int(c_tk // dy)

                residual += (float_disc - int_disc)
                if residual >= 1:
                    int_disc += 1
                disc_par += [par_to_disc[c_lay]]*int_disc

        else:
            c_lay = -1
        # Half-space
        disc_par += [par_to_disc[c_lay+1]]*(len(disc_depth)-len(disc_par))

        # TODO (jpv): Properly account for the fact that the entire profile
        # may not be discretized (i.e., for loop should not extend to self.tk[:-1])
        disc_par = disc_par[:len(disc_depth)]
        
        return (disc_depth, disc_par)

    def simplify(self, param='vs'):
        """Remove unecessary breaks due to those parameters other than
        that specificed. This will typically be used for calculating the
        median across many profiles."""
        if param == 'vs':
            par = self.vs
        elif param == 'vp':
            par = self.vp
        elif param == 'rh':
            par = self.rh
        else:
            raise NotImplementedError(f"param={param} is unkown.")
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
        """Calcualte the time-averaged shear-wave velocity in the upper
        30m (Vs30).

        Returns:
            Vs30 of ground model as float.
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

    def write_to_mat(self, fname):
        """Save ground model information to .mat format.

        Args:
            fname: Name of file (excluding the .mat extension) where the
                file should be saved. A relative or full path may be
                specified if desired.

        Returns:
            This methods returns nothing, but write file with name fname
            to disk.

        Raises:
            This method raises no exceptions.
        """
        if fname.endswith(".mat"):
            fname = fname[:-4]
        sio.savemat(fname+".mat", {"thickness": self.tk,
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
        """`List` of thicknesses from a `list` of depths (at top of each
        layer)."""
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
        """Return `list` of depths (at the top of each layer)."""
        depths = [0]
        for clayer in range(1, len(thicknesses)):
            depths.append(sum(thicknesses[:clayer]))
        return depths

    @property
    def txt_repr(self):
        lines = f"{self.nlay}\n"
        for tk, vp, vs, rh in zip(self.tk, self.vp, self.vs, self.rh):
            lines += f"{tk} {vp} {vs} {rh}\n"
        return lines

    def write_model(self, fileobj, model_num=1, misfit=0.0000):
        """Write `GroundModel` to opened fileobj.
        
        Args:
            fileobj : _io.TextIOWrapper
                Name of file, may contain a relative or the full path.
            model_num : int, optional
                Model number, required to be consistent with Geopsy
                naming convention when exporting inversion results,
                default is 1.
            misfit : float, optional
                Misfit, required to be consistent with Geopsy
                naming convention when exporting inversion results,
                default is 0.0000.
        
        Returns:
            `None`, writes file to disk.
        """
        fileobj.write(f"# Layered model {model_num}: value={misfit}\n")
        for line in self.txt_repr:
            fileobj.write(line)

    def write_to_txt(self, fname, model_num=1, misfit=0.0000):
        """Write `GroundModel` to file that follows the Geospy format.
        
        Args:
            fname : str
                Name of file, may contain a relative or the full path.
            model_num : int, optional
                Model number, required to be consistent with Geopsy
                naming convention when exporting inversion results,
                default is 1.
            misfit : float, optional
                Misfit, required to be consistent with Geopsy
                naming convention when exporting inversion results,
                default is 0.0000.
        
        Returns:
            `None`, writes file to disk.
        """
        with open(fname, "w") as f:
            f.write(f"# Layered model {model_num}: value={misfit}\n")
            for line in self.txt_repr:
                f.write(line)

    @staticmethod
    def mkgm(thk, vps, vss, rho):
        # print("swipp GroundModel")
        return GroundModel(thickness=thk, vp=vps, vs=vss, density=rho)

    @classmethod
    def _gm(cls):
        return GroundModel

    @classmethod
    def _parse_gm(cls, gm_data):

        tks, vps, vss, rhs = [], [], [], []
        for gm in regex.gm_data.finditer(gm_data):
            tk, vp, vs, rh = gm.groups()

            tks.append(float(tk))
            vps.append(float(vp))
            vss.append(float(vs))
            rhs.append(float(rh))

            if tk == "0":
                break

        return cls._gm()(tks, vps, vss, rhs)

    @classmethod
    def from_geopsy(cls, fname):
        """Instantiate a `GroundModel` from a file exported from Geopsy.

        Args:
            fname : fname
                File name, may contain a relative or the full path.

        Returns:
            Initialized GroundModel object.

        Raises:
            Various errors if ground model file is not of the correct 
            format. See example files for details.
        """
        with open(fname, "r") as f:
            lines = f.read()
        return cls._parse_gm(lines)

    def __eq__(self, other):
        """Define when two ground models are equivalent."""
        vals1 = self.tk + self.vp + self.vs + self.rh
        vals2 = other.tk + other.vp + other.vs + other.rh
        for val1, val2 in zip(vals1, vals2):
            if val1 != val2:
                return False
        else:
            return True

    def __str__(self):
        """Define un-official representation of an instantiated object."""
        return self.txt_repr

    def __repr__(self):
        """Define official representation of an instantiated object."""
        return f"GroundModel(thickness={self.tk}, vp={self.vp}, vs={self.vs}, density={self.rh})"
    
    def __eq__(self, other):
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
