"""This file contains the GroundModel class for handling ground model
(i.e. layered velocity model objects)."""

import scipy.io as sio
import copy
import warnings
import logging
import subprocess
import numpy as np
import re
from swipp import DispersionSet
import os
logging.Logger(name=__name__)


class GroundModel():
    """Class for manipulating ground model objects.

    Attributes:
        tk:
        vp:
        vs:
        rh:
    """

    @staticmethod
    def check_input_type(thickness, vp, vs, density):
        tmp_dict = {"thickness": thickness,
                    "vp": vp, "vs": vs, "density": density}
        tmp_len = len(thickness)
        for name, value in tmp_dict.items():
            if not isinstance(value, list):
                raise TypeError(f"{name} must be a list, not {type(value)}.")
            if tmp_len != len(value):
                raise TypeError(f"All inputs must have the same length.")
            for val in value:
                if (not isinstance(val, int)) and (not isinstance(val, float)):
                    raise TypeError(
                        f"{name} must be a list of int or float, not {type(val)}.")

    @staticmethod
    def check_input_value(thickness, vp, vs, density):
        tmp_dict = {"thickness": thickness,
                    "vp": vp, "vs": vs, "density": density}
        for name, value in tmp_dict.items():
            for val in value:
                if val < 0:
                    raise TypeError(f"{name} must always be >= 0.")
        for tmp_vp, tmp_vs in zip(vp, vs):
            if tmp_vs > tmp_vp:
                raise ValueError(
                    f"vp must be greater than vs, {tmp_vp}!>{tmp_vs}.")

    def __init__(self, thickness, vp, vs, density):
        """Initialize a ground model object

        Args:
            thickness: List of floats or ints denoting the layers
                thickness (one per layer) in meters starting from the
                ground surface.
            vp: List of floats or ints denoting the P-wave velocity of
                each layer in m/s.
            vs: List of floats or ints denoting the S-wave velocity of
                each layer in m/s.
            density: List of floats or ints denoting the mass density
                of each layer in kg/m3.

        Returns:
            An instantiated GroundModel object

        Raises:
            This method raises no exceptions.
        """
        self.check_input_type(thickness, vp, vs, density)
        self.check_input_value(thickness, vp, vs, density)
        self.nlay = len(thickness)
        self.tk = copy.deepcopy(thickness)
        self.vp = copy.deepcopy(vp)
        self.vs = copy.deepcopy(vs)
        self.rh = copy.deepcopy(density)

    @staticmethod
    def calc_pr(vp, vs):
        """Calculate Poisson's Ratio from lists of vp and vs.

        Args:
            vp: List of vp values.

            vs: List of vs values.

        Returns:
            List of Poisson's Ratio, calculated from each vp, vs pair.

        Raises:
            ValueError: If vs>vp.
            ValueError: If calculated Poisson's Ratio is negative.
        """
        if type(vp) in [int, float]:
            print("Warning: vp should be an iterable type.")
            vp = [vp]
        if type(vs) in [int, float]:
            print("Warning: vs should be an iterable type.")
            vs = [vs]
        pr = []
        for vp, vs in zip(vp, vs):
            # Make sure vp>vs
            if vp <= vs:
                raise ValueError(f"Vp={vp} must be greater than Vs={vs}.")
            pr += [(2-(vp/vs)**2)/(2-2*(vp/vs)**2)]
            # Make sure pr>0
            if pr[-1] <= 0:
                raise ValueError(
                    f"Poison's Raio cannot be negative. Vp/Vs={vp}/{vs} too close to unity.")
        return pr

    @classmethod
    def from_simple_profiles(cls, vp_tk, vp, vs_tk, vs, rh_tk, rh):
        """Create groundmodel object from simple profiles"""
        depths = list(dict.fromkeys(cls.thick_to_depth(vp_tk)[1:] +
                                    cls.thick_to_depth(vs_tk)[1:] +
                                    cls.thick_to_depth(rh_tk)[1:]
                                    ))
        depths.sort()
        depths.append(0)
        if depths == [0]:
            new_tk = [0]
        else:
            new_tk = cls.depth_to_thick(depths)

            
        def define_par(depths, new_par, tk, par):
            cnt = 0
            for cdepth in depths:
                if tk[cnt] == 0:
                    new_par += [par[cnt]]*(len(depths)-len(new_par))
                    break
                new_par.append(par[cnt])
                if cdepth >= sum(tk[:cnt+1]):
                    cnt += 1
                    
        new_vp, new_vs, new_rh = [], [], []
        define_par(depths, new_vp, vp_tk, vp)
        define_par(depths, new_vs, vs_tk, vs)
        define_par(depths, new_rh, rh_tk, rh)
        return cls(new_tk, new_vp, new_vs, new_rh)


    @property
    def depth(self):
        """Return stair-step version of depth profile."""
        return self.gm2()[0]

    @property
    def vp2(self):
        """Return stair-step version of Vp profile."""
        return self.gm2()[1]

    @property
    def vs2(self):
        """Return stair-step version of Vs profile."""
        return self.gm2()[2]

    @property
    def rh2(self):
        """Return stair-step version of density profile."""
        return self.gm2()[3]

    def gm2(self):
        """Convert standard ground model to stair step version, so the
        results can be easily plotted.

        Args:
            This method requires no arguements.

        Returns:
            Tuple of the form (depth2, vp2, vs2, rho2) where for example
            depth2 is a list of the top and bottom depths of each layer.

        Raises:
            This method raises no exceptions.
        """
        gm2 = [[0],
               [self.vp[0]],
               [self.vs[0]],
               [self.rh[0]]]
        lay = 1

        for pnt in range(1, 2*self.nlay):
            logging.debug(f"pnt = {pnt}, lay = {lay}")
            # If half-space
            if pnt == (2*self.nlay-1):
                gm2[0].append(9999.0)
                gm2[1].append(self.vp[-1])
                gm2[2].append(self.vs[-1])
                gm2[3].append(self.rh[-1])
            # Otherwise
            else:
                # Thickness to depth
                gm2[0].append(sum(self.tk[0:lay]))
                # If odd number point, append previous
                if pnt % 2 != 0:
                    gm2[1].append(self.vp[lay-1])
                    gm2[2].append(self.vs[lay-1])
                    gm2[3].append(self.rh[lay-1])
                # If even number point, start new layere
                else:
                    gm2[1].append(self.vp[lay])
                    gm2[2].append(self.vs[lay])
                    gm2[3].append(self.rh[lay])
                    lay += 1
        return (gm2[0], gm2[1], gm2[2], gm2[3])

    def gm2_par(self, param='depth'):
        """Similar to gm2 method, except only a single parameter is
        returned.

        Args:
            param: Select parameter of interest (i.e., 'depth', 'vp',
                'vs', 'rho', 'pr') to be returned as a stair-step
                version for ease of plotting.

        Returns:
            List of the selected parameter.

        Raises:
            This method raises no exceptions.
        """
        par_options = {'depth': 0, 'vp': 1, 'vs': 2, 'rho': 3, 'pr': 4}
        parameter = par_options[param]
        if parameter == par_options['pr']:
            return self.calc_pr(self.gm2()[par_options['vp']],
                                self.gm2()[par_options['vs']])
        else:
            return self.gm2()[parameter]

    def gm2_disc(self, dmax, dy=0.5, param='vs'):
        """Returns a discretized stair-step model.

        The stair step model is discretized by depth from the surface to
        dmax by dy such that depth will be a list of the forn
        [0:dy:dmax]. When the discretization encounters a stair tred
        (i.e., where two velocities are specified at a single depth) the
        velocity of the upper layer is assigned. Do not use these
        discretized models for plotting as they may be misleading.

        Args:
            dmax: Maximum depth of discretization.

            dy: Linear step of discretizaton in terms of depth.

            param: Parameter to be discretized.

        Returns:
            Tuple of the form (depth, param) where depth is a list of
            the discretized depths, and param is a list of the
            discretized param at those depths.

        Raises:
            This method raises no exceptions.
        """
        par_options = {'depth': 0, 'vp': 1, 'vs': 2, 'rho': 3, 'pr': 4}
        depth = self.gm2()[par_options['depth']]
        parameter = par_options[param]
        par_to_disc = self.gm2()[parameter]

        ddepth = []
        dpar = []
        cdepth = 0
        for n in range(len(depth)-1):
            dnp1 = depth[n+1]
            pn = par_to_disc[n]
            while ((cdepth <= dnp1) & (cdepth <= dmax)):
                ddepth += [cdepth]
                dpar += [pn]
                cdepth += dy
            if cdepth > dmax:
                break
        return (ddepth, dpar)

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

    def vs30(self):
        """Return Vs30 (i.e., time-averaged shear-wave velocity in the
        upper 30m).

        Args:
            This method requires no arguements.

        Returns:
            A float indicating Vs30.

        Raises:
            This method raises no exceptions.
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
        depth2, vp2, vs2, rh2 = self.gm2()
        sio.savemat(fname+".mat", {"thickness": self.tk,
                                   "vp1": self.vp,
                                   "vs1": self.vs,
                                   "rho1": self.rh,
                                   "depth": depth2,
                                   "vp2": vp2,
                                   "vs2": vs2,
                                   "rho2": rh2,
                                   })

    # TODO (jpv): Decide whether top or bottom of each layer is more desirable.
    @staticmethod
    def depth_to_thick(depths):
        """Return list of thicknesses from a list of depths (at bottom of each layer)."""
        thicknesses = [depths[0]]
        for cid in range(1, len(depths)-1):
            thicknesses.append(depths[cid]-depths[cid-1])
        thicknesses.append(0)
        return thicknesses

    @staticmethod
    def thick_to_depth(thicknesses):
        """Return list of depths (at the top of each layer)."""
        depths = [0]
        for clay in range(1, len(thicknesses)):
            depths.append(sum(thicknesses[:clay]))
        return depths

    def write_model(self, fileobj, model_num=1, misfit=0.0000):
        """Write/Append ground model to an existing fileobject."""
        fileobj.write(f"# Layered model {model_num}: value={misfit}\n")
        fileobj.write(f"{self.nlay}\n")
        for tk, vp, vs, rh in zip(self.tk, self.vp, self.vs, self.rh):
            fileobj.write(f"{tk} {vp} {vs} {rh}\n")

    def write_to_txt(self, fname, model_num=1, misfit=0.0000):
        """Write ground model to a text file that follows the geospy
        format."""
        with open(fname, "w") as f:
            f.write(f"# Layered model {model_num}: value={misfit}\n")
            f.write(f"{self.nlay}\n")
            for tk, vp, vs, rh in zip(self.tk, self.vp, self.vs, self.rh):
                f.write(f"{tk} {vp} {vs} {rh}\n")

    @classmethod
    def from_geopsy(cls, fname):
        """Alternate constuctor for instantiating a GroundModel
        from a file exported from Geopsy.

        Args:
            fname: Name of file to be read, may contain a relative or
                full path if desired.

        Returns:
            Initialized GroundModel object.

        Raises:
            Various errors if ground model file is not of the correct 
            format. See example files for details.
        """

        with open(fname, "r") as f:
            lines = f.read().splitlines()
        thk, vps, vss, rho = [], [], [], []
        first = True
        obj = None
        regex_one = r"(\d+.?\d*[eE]?[+-]?\d*)"
        sp = r"\s"
        regex_all = f"^{regex_one}{sp}{regex_one}{sp}{regex_one}{sp}{regex_one}$"
        # exp1 = r"^# Layered model (\d+): value=(\d+.?\d*)$"
        for line in lines:
            try:
                thk_i, vps_i, vss_i, rho_i = re.findall(regex_all, line)[0]
                thk.append(float(thk_i))
                vps.append(float(vps_i))
                vss.append(float(vss_i))
                rho.append(float(rho_i))
            except IndexError:
                if line.startswith("# "):
                    if line.startswith("# Layered model"):
                        if first == True:
                            first = False
                        elif obj == None:
                            return cls(thickness=thk, vp=vps, vs=vss, density=rho)
                        else:
                            break
        return cls(thickness=thk, vp=vps, vs=vss, density=rho)

    def __eq__(self, other):
        """Define when two ground models are equivalent."""
        vals1 = self.tk + self.vp + self.vs + self.rh
        vals2 = other.tk + other.vp + other.vs + other.rh
        for val1, val2 in zip(vals1, vals2):
            if val1 != val2:
                return False
        else:
            return True

    def __repr__(self):
        """Define official representation of an instantiated object."""
        return f"thickness = {self.tk}\nvp = {self.vp}\nvs = {self.vs}\nrh = {self.rh}\n"
