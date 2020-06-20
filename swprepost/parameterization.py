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

"""Parameterization class definition."""

import warnings
import logging
import tarfile as tar
import os
import re

import numpy as np

from swprepost import Parameter

logging.Logger(name=__name__)


class Parameterization():
    """Class for developing inversion parameterizations.

    This class is intended to be used for developing various
    parameterization files for use in the open-source software Dinver.
    While parameterizations of various kinds can be built quickly using
    this tool, it does have limited functionality compared to the full
    user interface. It is recommended that the user use this tool to 
    batch create general parameterizations then fine tune them if
    necessary using the Dinver user interface.

    Attributes
    ----------
    vs, vp, pr, rh : Parameter
        Parameter objects defining shear-wave velocity,
        compression-wave velocity, Poisson's ratio, and mass density
        respectively.
    """

    @staticmethod
    def check_parameter(name, val):
        """Check input for the parameter."""
        if not isinstance(val, Parameter):
            msg = f"{name} must be an instance of `Parameter`, not `{type(val)}`."
            raise TypeError(msg)

    def __init__(self, vp, pr, vs, rh):
        """Initialize an instance of the `Parameterization` class.

        Initialize a `Parameterization` using instantiated `Parameter`
        objects. 

        Parameters
        ----------
        vp, pr, vs, rh : Parameter
            Instantiated `Parameter` objects, see :meth: `Parameter
            <swprepost.Parameter.__init__>`.

        Returns
        -------
        Parameterization
            An initialized `Parameterization` object.

        Raises
        ------
        TypeError
            If `vp`, `pr`, `vs`, and `rh` are not `Parameter`
            objects.
        """

        for name, par in zip(("vp", "pr", "vs", "rh"), [vp, pr, vs, rh]):
            self.check_parameter(name, par)

        self.vp = vp
        self.pr = pr
        self.vs = vs
        self.rh = rh

    @classmethod
    def from_min_max(cls, vp, pr, vs, rh, wv, factor=2):
        """Initialize an instance of the Parameterization class from
        a minimum and maximum value.

        This method compromises readability for pure character
        efficiency (which is almost always a bad idea!), however some
        users may find this method useful.

        Parameters
        ----------
        vp, pr, vs, rh : list
            Of the form `[type, value, min, max, bool]` where `type`
            is discussed below, `min` and `max` are the minimum and
            maximum values which the parameter may assume, and
            `bool` indicates whether the non-typical condition is
            allowed.

            Type:
                If type = 'FX'
                    Layering is Fixed, the next and only argument
                    is its value.

                Ex. ['FX', value]

                If type = 'FTL'
                    Layering follows Fixed Thickness Layering, the
                    second argument is the number of layers desired,
                    followed by their thickness, min, max, and bool.

                Ex. ['FTL', nlay, thickness, min, max, bool]

                If type = 'LN'
                    Layering follows Layering by Number, the next
                    argument is number of layers followed by min,
                    max, and bool. 

                Ex. ['LN', ln, min, max, reversal]

                If type = 'LR' 
                    Layering follows the Layering Ratio, the next
                    arguement is the layering ratio followed by
                    min, max, and bool.

                Ex. ['LR', lr, min, max, reversal]

        wv : iterable
            Of the form [min_wave, max_wave] where 
            `min_wave` and `max_wave` are of type `float` or `int`
            and indicate the minimum and maximum measured wavelength
            from the fundamental mode Rayleigh wave disperison.

        factor : float, optional
            Factor by which the maximum wavelength is
            divided to estimate the maximum depth of profiling,
            default is 2.

        Returns
        -------
        Parameterization
            Instantiated `Paramterization` object.

        Raises
        ------
        Various
            If values do not comply with the instructions listed.
        """

        input_arguements = {"vs": vs, "vp": vp, "pr": pr, "rh": rh}
        valid_options = ('FX', 'FTL', 'LN', 'LNI', 'LN-thickness', 'LR')
        for key, value in input_arguements.items():
            # Ensure entry is a list
            if type(value) != list:
                msg = f"Entry for argument {key} must be a list, not {type(value)}."
                raise TypeError(msg)

            # Ensure the first entry of that list is a valid option
            if value[0] not in valid_options:
                msg = f"{value[0]} entered for {key} not recognized use {valid_options}."
                raise ValueError(msg)

            if value[0] == "FX":
                input_arguements[key] = Parameter.from_fx(value[1])
            elif value[0] == "FTL":
                input_arguements[key] = Parameter.from_ftl(*value[1:])
            elif value[0] == "LN-thickness":
                input_arguements[key] = Parameter.from_ln_thickness(*wv,
                                                                    *value[1:],
                                                                    factor, False)
            elif value[0] == "LN":
                input_arguements[key] = Parameter.from_ln_depth(*wv,
                                                                *value[1:])
            elif value[0] == "LNI":
                input_arguements[key] = Parameter.from_ln_thickness(*wv,
                                                                    value[1],
                                                                    *value[3:],
                                                                    factor, True, value[2])
            elif value[0] == "LR":
                input_arguements[key] = Parameter.from_lr(*wv, *value[1:])
            else:
                raise NotImplementedError

        return cls(input_arguements["vp"], input_arguements["pr"],
                   input_arguements["vs"], input_arguements["rh"])

    def to_param(self, fname_prefix, version="3", full_version=None):
        """Write parameterization to `.param` file that can be imported
        into Dinver.

        Parameters
        ----------
        fname_prefix : str
            File name prefix (without the .param extension), may be
            a relative or the full path. 
        version : {'2', '3'}, optional
            Major version of Geopsy, default is '3'.
        full_version : str, optional
            Full version of Geopsy in the form Major.Minor.Micro,
            default is `None`. When equal to `None` the method
            will produce a warning if `full_version` is required
            to avoid ambiguity.

        Returns
        -------
        None
            Writes `.param` file to disk.

        Raises
        ------
        KeyError
            If `version` does not match those listed in the
            documentation.
        """
        available_versions = {'2': '2', '3': '3'}
        version = available_versions[version]

        contents = ['<Dinver>',
                    '  <pluginTag>DispersionCurve</pluginTag>',
                    '  <pluginTitle>Surface Wave Inversion</pluginTitle>',
                    '  <ParamGroundModel>']

        parameters = {"Vp": self.vp, "Nu": self.pr,
                      "Vs": self.vs, "Rho": self.rh}

        for key, value in parameters.items():
            if key == "Vp":
                contents += ['    <ParamProfile>',
                             '      <type>Param</type>',
                             '      <longName>Compression-wave velocity</longName>',
                             '      <shortName>Vp</shortName>',
                             '      <unit>m/s</unit>',
                             '      <defaultMinimum>200</defaultMinimum>',
                             '      <defaultMaximum>5000</defaultMaximum>',
                             '      <defaultCondition>LessThan</defaultCondition>']
            elif key == "Nu":
                contents += ['    <ParamProfile>',
                             '      <type>Condition</type>',
                             '      <longName>Poisson&apos;s Ratio</longName>',
                             '      <shortName>Nu</shortName>',
                             '      <unit></unit>',
                             '      <defaultMinimum>0.2</defaultMinimum>',
                             '      <defaultMaximum>0.5</defaultMaximum>',
                             '      <defaultCondition>GreaterThan</defaultCondition>']
            elif key == "Vs":
                contents += ['    <ParamProfile>',
                             '      <type>Param</type>',
                             '      <longName>Shear-wave velocity</longName>',
                             '      <shortName>Vs</shortName>',
                             '      <unit>m/s</unit>',
                             '      <defaultMinimum>150</defaultMinimum>',
                             '      <defaultMaximum>3500</defaultMaximum>',
                             '      <defaultCondition>LessThan</defaultCondition>']
            elif key == "Rho":
                contents += ['    <ParamProfile>',
                             '      <type>Param</type>',
                             '      <longName>Density</longName>',
                             '      <shortName>Rho</shortName>',
                             '      <unit>kg/m3</unit>',
                             '      <defaultMinimum>2000</defaultMinimum>',
                             '      <defaultMaximum>2000</defaultMaximum>',
                             '      <defaultCondition>LessThan</defaultCondition>']
            else:
                raise NotImplementedError(f"Selection {key} not implemented")

            if value._par_type in ["FX", "FTL", "LN-thickness", "LNI", "CT"]:
                isdepth = "false"
            elif value._par_type in ["LR", "CD", "LN", "LN-depth"]:
                isdepth = "true"
            else:
                msg = f"._par_type` {value._par_type} not recognized, refer to Parameter.__doc__."
                raise NotImplementedError(msg)          

            for lnum, (dhmin, dhmax, pmin, pmax, rev) in enumerate(zip(value.lay_min, value.lay_max, value.par_min, value.par_max, value.par_rev)):
                rev_check = 'true' if not rev else 'false'
                rev_check = 'true' if len(value.lay_min) == 1 else rev_check
                linkedto = f"{value.linked}{lnum}" if value.linked else "Not linked"
                contents += ['      <ParamLayer name="'+key+str(lnum)+'">',
                             '        <shape>Uniform</shape>',
                             '        <lastParamCondition>'+rev_check+'</lastParamCondition>',
                             '        <nSubayers>5</nSubayers>',
                             '        <topMin>'+str(pmin)+'</topMin>',
                             '        <topMax>'+str(pmax)+'</topMax>',
                             '        <linkedTo>'+linkedto+'</linkedTo>',
                             '        <isDepth>'+isdepth+'</isDepth>',
                             '        <dhMin>'+str(dhmin)+'</dhMin>',
                             '        <dhMax>'+str(dhmax)+'</dhMax>',
                             '      </ParamLayer>']
            contents += ['    </ParamProfile>']

        contents += ['    <ParamSpaceScript>',
                     '      <text>']

        for key, value in parameters.items():

            if value._par_type == "LNI":
                nlay = value.par_value
                if nlay > 2:
                    factor = value.par_add_value
                    for lay in range(nlay-2):
                        if lay == 0:
                            char = "D"
                            if version == "2" and full_version is None:
                                msg = "If `full_version` is '2.9.0' please so \
indicate by setting `full_version='2.9.0'`, otherwise no action is required."
                                warnings.warn(msg)
                            elif version == "2" and full_version == "2.9.0":
                                char = "H"
                            else:
                                pass
                        else:
                            char = "H"
                        contents += [
                            f'linear("H{key}{lay+1}", ">" ,{factor},"{char}{key}{lay}",0);']
            elif value._par_type == "LN":
                nlay = value.par_value
                min_thickness = np.round(value.lay_min[0], decimals=2)
                if nlay > 2:
                    for lay in range(nlay-2):
                        contents += [
                            f'linear("D{key}{lay+1}",">",{1},"D{key}{lay}",{min_thickness});']

        contents += ['      </text>',
                     '    </ParamSpaceScript>',
                     '  </ParamGroundModel>',
                     '</Dinver>']

        with open("contents.xml", "w") as f:
            for row in contents:
                f.write(row+"\n")
        with tar.open(fname_prefix+".param", "w:gz") as f:
            f.add("contents.xml")
        os.remove("contents.xml")

    @classmethod
    def from_param(cls, fname_prefix):
        """Instantitate a Parameterization object from a .param file.

        Parameters
        ----------
        fname_prefix : str
            File name prefix, may include a relative or the full
            path.

        Returns
        -------
        Parameterization
            Instantitated `Parameterization` object.

        Raises
        ------
        ValueError:
            If file encoding is not recognized.
        """
        with tar.open(fname_prefix+".param", "r:gz") as a:
            a.extractall()

        try:
            with open("contents.xml", "r", encoding="utf-8") as f:
                lines = f.read()
            if "<Dinver>" not in lines[:10]:
                raise RuntimeError
        except (UnicodeDecodeError, RuntimeError):
            with open("contents.xml", "r", encoding="utf_16_le") as f:
                lines = f.read()
            if "<Dinver>" not in lines[:10]:
                raise ValueError("File encoding not recognized.")
        os.remove("contents.xml")

        section_lines = []
        lines = lines.splitlines()
        for line_count, line in enumerate(lines):
            if "<shortName>" in line:
                section_lines.append(line_count)
        section_lines.append(len(lines))

        number = f"(-?\d+.?\d*[eE]?[+-]?\d*)"
        newline = r"\W+"
        reg_shape = "<shape>.*</shape>"
        reg_cond = "<lastParamCondition>(true|false)</lastParamCondition>"
        reg_nsub = "<nSubayers>\d+</nSubayers>"
        reg_pmin = f"<topMin>{number}</topMin>"
        reg_pmax = f"<topMax>{number}</topMax>"
        reg_link = "<linkedTo>.*</linkedTo>"
        reg_isdepth = "<isDepth>(true|false)</isDepth>"
        reg_lmin = f"<dhMin>{number}</dhMin>"
        reg_lmax = f"<dhMax>{number}</dhMax>"

        regex = ""
        for cond in [reg_shape, reg_cond, reg_nsub, reg_pmin, reg_pmax,
                     reg_link, reg_isdepth, reg_lmin, reg_lmax]:
            regex += f"{cond}{newline}"

        for section_start, section_end in zip(section_lines[:-1], section_lines[1:]):
            section_lines = lines[section_start:section_end]
            name = re.findall(
                "^\s+<shortName>(.*)</shortName>", section_lines[0])[0]
            section = "\n".join(section_lines)

            # Assume shape is uniform
            tmp_rev = []
            # Ignore sublayers
            tmp_pmin = []
            tmp_pmax = []
            # Assume unlinked
            tmp_depth = []
            tmp_lmin = []
            tmp_lmax = []

            for rev, pmin, pmax, depth, lmin, lmax in re.findall(regex, section):
                tmp_rev.append(False if rev == "true" else True)
                tmp_pmin.append(float(pmin))
                tmp_pmax.append(float(pmax))
                tmp_depth.append(True if depth == "true" else False)
                tmp_lmin.append(float(lmin))
                tmp_lmax.append(float(lmax))

            # Dont allow for mixed thickness and depth
            if len(tmp_depth) > 1:
                isdepth = tmp_depth[1]
                for val in tmp_depth[1:]:
                    if val != isdepth:
                        msg = "Parameterizations with layers defined in terms of thickness and depth cannot be parsed at this time."
                        raise ValueError(msg)
            else:
                isdepth = True

            lay_type = "depth" if isdepth else "thickness"
            par = Parameter(tmp_lmin, tmp_lmax, tmp_pmin,
                            tmp_pmax, tmp_rev, lay_type)
            if name == "Vp":
                vp = par
            elif name == "Vs":
                vs = par
            elif name == "Rho":
                rh = par
            elif name == "Nu":
                pr = par
            else:
                raise NotImplementedError
        return cls(vp, pr, vs, rh)

    def __eq__(self, other):
        for attr in ["vp", "pr", "vs", "rh"]:
            my_val = getattr(self, attr)
            ur_val = getattr(other, attr)
            if my_val != ur_val:
                return False
        return True

    def __repr__(self):
        return f"Parameterization(\nvp={self.vp},\npr={self.pr},\nvs={self.vs},\nrh={self.rh})"
