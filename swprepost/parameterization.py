# This file is part of swprepost, a Python package for surface wave
# inversion pre- and post-processing.
# Copyright (C) 2019-2022 Joseph P. Vantassel (jvantassel@utexas.edu)
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

import logging
import tarfile
import re
import io

import numpy as np

from .check_utils import check_geopsy_version
from .parameter import Parameter


logging.Logger(name=__name__)


class Parameterization():
    """Class for developing inversion parameterizations.

    This class is intended to be used for developing various
    parameterization files for use in the open-source software Dinver.
    While parameterizations of various kinds can be built quickly using
    this tool, it does have limited functionality compared to the full
    user interface. It is recommended that the you use this tool to
    create general parameterizations in batches and fine tune them if
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
    def from_min_max(cls, *args, **kwargs):  # pragma: no cover
        return DeprecationWarning("This method was depreacted after v1.0.0.")

    def to_param(self, fname_prefix, version="3.4.2"):
        """Write info to the .param used by Dinver.

        Parameters
        ----------
        fname_prefix : str
            File name prefix (without the .param extension), may be
            a relative or the full path.
        version : {'3.4.2', '2.10.1'}, optional
            Version of Geopsy, default is version '3.4.2'.

        Returns
        -------
        None
            Writes `.param` file to disk.

        Raises
        ------
        NotImplementedError
            If `version` does not match the options provided.

        Notes
        -----
        In previous versions of `swprepost` (v1.0.0 and earlier) an
        attempt was made to support all versions of Dinver's .target
        and .param formats. However, this has become untenable due to
        the number and frequency of breaking changes that occur to these
        formats. Therefore, in lieu of supporting all versions,
        `swprepost` will seek to support only those versions directly
        associated with the open-source high-performance computing
        application `swbatch`.

        """
        version = check_geopsy_version(version)

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
            else:  # pragma: no cover
                raise NotImplementedError(f"Selection {key} not implemented")

            if value._par_type in ["FX", "FTL", "CT"]:
                isdepth = "false"
            elif value._par_type in ["LR", "CD", "LN"]:
                isdepth = "true"
            else:  # pragma: no cover
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

            if value._par_type == "LN":
                nlay = value.par_value
                min_thickness = np.round(value.lay_min[0], decimals=2)
                if nlay > 2:
                    for lay in range(nlay-2):
                        contents += [
                            f'linear(&quot;D{key}{lay+1}&quot;,&quot;&gt;&quot;,{1},&quot;D{key}{lay}&quot;,{min_thickness});']

        contents += ['      </text>',
                     '    </ParamSpaceScript>',
                     '  </ParamGroundModel>',
                     '</Dinver>\n']
        # TODO (jpv): Check if final \n is required here.

        text = "\n".join(contents)

        if version == "2.10.1":
            encoding = "utf-8"
            file_format = tarfile.GNU_FORMAT
        elif version == "3.4.2":
            encoding = "utf_16_le"
            file_format = tarfile.DEFAULT_FORMAT
            text = u"\ufeff" + text
        else:  # pragma: no cover
            msg = "You updated the SUPPORTED_GEOPSY_VERSIONS, but need to update to_param."
            raise NotImplementedError(msg)

        # TODO (jpv): Factor out tarball writting process as this is shared
        # with to_target.
        text_b = text.encode(encoding)
        f_data = io.BytesIO(initial_bytes=text_b)

        f_contents = io.BytesIO()
        with tarfile.open(fileobj=f_contents, mode="w:gz", format=file_format) as tar:
            info = tarfile.TarInfo(name="contents.xml")
            info.size = len(text_b)
            tar.addfile(info, f_data)

        with open(f"{fname_prefix}.param", "wb") as f:
            f.write(f_contents.getvalue())

        f_data.close()
        f_contents.close()

    @classmethod
    def from_param(cls, fname_prefix, version="3.4.2"):
        """Create `Parameterization` from a .param file.

        Note this method is still largely experimental and may
        not work for all cases.

        Parameters
        ----------
        fname_prefix : str
            Name of param file to be opened excluding the `.param`
            suffix, may include the relative or full path.
        version : {'3.4.2', '2.10.1'}, optional
            Version of Geopsy, default is version '3.4.2'.

        Returns
        -------
        Parameterization
            Instantiated `Parameterization` object.

        Raises
        ------
        NotImplementedError
            If `version` does not match the options provided.

        Notes
        -----
        In previous versions of `swprepost` (v1.0.0 and earlier) an
        attempt was made to support all versions of Dinver's .target
        and .param formats. However, this has become untenable due to
        the number and frequency of breaking changes that occur to these
        formats. Therefore, in lieu of supporting all versions,
        `swprepost` will seek to support only those versions directly
        associated with the open-source high-performance computing
        application `swbatch`.

        """
        version = check_geopsy_version(version)

        if version == "2.10.1":
            encoding = "utf-8"
        elif version == "3.4.2":
            encoding = "utf_16_le"
        else:  # pragma: no cover
            msg = "You updated the SUPPORTED_GEOPSY_VERSIONS, but need to update from_param."
            raise NotImplementedError(msg)

        with tarfile.open(f"{fname_prefix}.param", "r:gz") as f:
            text = f.extractfile(f.getmember("contents.xml")
                                 ).read().decode(encoding)

        # TODO (jpv): Clean up regular expressions.
        # Place these in regex module.
        section_lines = []
        lines = text.splitlines()
        for line_count, line in enumerate(lines):
            if "<shortName>" in line:
                section_lines.append(line_count)
        section_lines.append(len(lines))

        number = "(-?\d+.?\d*[eE]?[+-]?\d*)"
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
                    if val != isdepth:  # pragma: no cover
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
            else:  # pragma: no cover
                raise NotImplementedError
        return cls(vp, pr, vs, rh)

    def __eq__(self, other):
        for attr in ["vp", "pr", "vs", "rh"]:
            my_val = getattr(self, attr)
            ur_val = getattr(other, attr)
            if my_val != ur_val:
                return False
        return True

    def __repr__(self):  # pragma: no cover
        return f"Parameterization(\nvp={self.vp},\npr={self.pr},\nvs={self.vs},\nrh={self.rh})"
