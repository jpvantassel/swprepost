"""This file includes the definition of the `Parameterization` class."""

import tarfile as tar
import os
from swipp import Parameter
import warnings
import logging
logging.Logger(name=__name__)


class Parameterization():
    """Class for developing inversion parameterizations.

    This class is intended to be used for developing various
    parameterization files for use in the open-source software Dinver.
    While parameterizations of various kinds can be built quickly using
    this tool, it does have limited functionality compared to the full
    user interface. It is recommended that the user, use this tool to 
    batch create general parameterizations, then fine tune them if
    necessary using the Dinver user interface.

    Attributes:
        This class contains no public attributes.
    """

    @staticmethod
    def check_parameter(name, val):
        """Check input for the parameter."""
        if not isinstance(val, Parameter):
            msg = f"{name} must be an instance of `Parameter`, not `{type(val)}`."
            raise TypeError(msg)

        # logging.info(f"Checking {name}...")

        # if val.get("type"):
        #     if val["type"] not in ["FX", "FTL", "LN", "LNI", "LR", "UserDefined"]:
        #         raise ValueError(f"Invalid type in {name}.")
        # else:
        #     val.update({"type": "UserDefined"})

        # if not val.get("value"):
        #     val.update({"value": "UserDefined"})

        # if val.get("thickness"):
        #     logging.info(f"{name} is defined with thickness.")
        #     if val.get("depth") is not None:
        #         raise ValueError(
        #             f"{name} must include either `thickness` or `depth`, not both.")
        #     keys = ["thickness"]
        #     test_len = len(val["thickness"]["min"])
        # elif val.get("depth"):
        #     logging.info(f"{name} is defined with depth.")
        #     if val.get("thickness") is not None:
        #         raise ValueError(
        #             f"{name} must include either `thickness` or `depth`, not both.")
        #     keys = ["depth"]
        #     test_len = len(val["depth"]["min"])
        # else:
        #     raise ValueError(f"{name} must have `thickness` or `depth`.")

        # logging.debug(f"len of parameters for {name} is {val}.")
        # keys.append("par")
        # for key in keys:
        #     for value in val[key].values():
        #         if test_len != len(value):
        #             raise ValueError(f"Length of {name} is not consistent.")

    def __init__(self, vp, pr, vs, rh):
        """Initialize an instance of the `Parameterization` class.

        Initialize a `Parameterization` using instantiated `Parameter`
        objects. 

        Args:
            vp, pr, vs, rh : Parameter
                Instantitated `Parameter` objects, see :meth: `Parameter
                <swipp.Parameter.__init__>`.

        Returns:
            An initialized Parameterization object.

        Raises:
            TypeError
                If `vp`, `pr`, `vs`, and `rh` are not instantiated
                `Parameter` objects.
        """

        for name, par in zip(("vp", "pr", "vs", "rh"), [vp, pr, vs, rh]):
            self.check_parameter(name, par)

        self.vp = vp
        self.pr = pr
        self.vs = vs
        self.rh = rh

    @classmethod
    def from_min_max(cls, vp, pr, vs, rh, wv, factor=2):
        """Intilize an instance of the Parameterization class from
        min/max.

        This method is left for backwards compatability.

        Args:
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
                        Layering follows Fixed Thickness Layinering, the
                        second argument is the number of layers desired,
                        followed by their thickness, min, max, and bool.

                    Ex. ['FTL', nlay, thickness, min, max, bool]

                    If type = 'LN'
                        Layering follows Layering by Number, the next
                        argument is number of layers followed by min,
                        max, and bool. 

                    Ex. ['LN', ln, min, max, reversal]

                    If type = 'LNI'
                        Layering follows Layering by Number with
                        Increasing thickness, which is similar to 'LN',
                        but with the requirement that the thickness of
                        each layer increases with depth.

                    Ex. ['LNI', ln, fac, min, max, reversal]

                    If type = 'LR' 
                        Layering follows the Layering Ratio, the next
                        arguement is the layering ratio followed by
                        min, max, and bool.

                    Ex. ['LR', lr, min, max, reversal]

                Example:

                    vs = ['LR', 3.0, 100, 300, False]

                Vs follows LR=3.0, with the minimum value of Vs set to
                100 m/s and the maximum value of Vs set to 300 m/s,
                with no velocity reversals permitted.

            wv : list
                Container of the form [min_wave, max_wave] where 
                `min_wave` and `max_wave` are of type `float` or `int`
                and indicate the minimum and maximum measured wavelength
                from the fundemental mode Rayleigh wave disperison.

            factor : [float, int], optional
                Factor by which the maximum wavelength is
                divided to estimate the maxium depth of profiling,
                default is 2.

        Returns:
            Instantiated `Paramterization` object.

        Raises:
            Various:
                If entered values do not comply with the instructions
                listed above.
        """

        input_arguements = {"vs": vs, "vp": vp, "pr": pr, "rh": rh}
        valid_options = ('FX', 'FTL', 'LN', 'LNI', 'LR')
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
            elif value[0] == "LN":
                input_arguements[key] = Parameter.from_ln(*wv,
                                                          *value[1:],
                                                          factor, False)
            elif value[0] == "LNI":
                input_arguements[key] = Parameter.from_ln(*wv,
                                                          value[1], *value[3:],
                                                          factor, True, value[2])
            elif value[0] == "LR":
                input_arguements[key] = Parameter.from_lr(*wv, *value[1:])
            else:
                raise NotImplementedError

        return cls(input_arguements["vp"], input_arguements["pr"],
                   input_arguements["vs"], input_arguements["rh"])

    def to_file(self, fname, version='2.9.0'):
        """Write paramterization file to disk that can be read by
        Dinver.

        Args:
            fname : str
                File name, may be a relative or the full path. 

            version : {'2.9.0', '2.10.1'}
                Version of Geopsy suite, being used.
                Note '2.9.0' is the version compiled on Stampede2.

        Returns:
            `None`, writes .param file to disk.

        Raises:
            KeyError: 
                If version does not match those specified exactly.
        """
        available_versions = {'2.9.0': '2.9.0', '2.10.1': '2.10.1'}
        version = available_versions[version]

        contents = ['<Dinver>',
                    '  <pluginTag>DispersionCurve</pluginTag>',
                    '  <pluginTitle>Surface Wave Inversion</pluginTitle>',
                    '  <ParamGroundModel>']

        parameters = {"Vp":self.vp, "Nu":self.pr, "Vs":self.vs, "Rho":self.rh}

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

            if value.par_type in ["FX", "FTL", "LN", "LNI", "CT" ]:
                isdepth = "false"
            elif value.par_type in ["LR", "CD"]:
                isdepth = "true"
            else:
                msg = f"`par_type` {value.par_type} not recognized, refer to Parameter.__doc__."
                raise NotImplementedError(msg)

            for lnum, (dhmin, dhmax, pmin, pmax, rev) in enumerate(zip(value.lay_min, value.lay_max, value.par_min, value.par_max, value.par_rev)):
                rev_check = 'true' if not rev else 'false'
                rev_check = 'false' if len(value.lay_min)==1 else rev_check
                contents += ['      <ParamLayer name="'+key+str(lnum)+'">',
                             '        <shape>Uniform</shape>',
                             '        <lastParamCondition>'+rev_check+'</lastParamCondition>',
                             '        <nSubayers>5</nSubayers>',
                             '        <topMin>' + str(pmin)+'</topMin>',
                             '        <topMax>' + str(pmax)+'</topMax>',
                             '        <linkedTo>Not linked</linkedTo>',
                             '        <isDepth>'+isdepth+'</isDepth>',
                             '        <dhMin>'+str(dhmin)+'</dhMin>',
                             '        <dhMax>'+str(dhmax)+'</dhMax>',
                             '      </ParamLayer>']
            contents += ['    </ParamProfile>']

        contents += ['    <ParamSpaceScript>',
                     '      <text>']

        for key, value in parameters.items():
            if value.par_type == "LNI":
                nlay = value.par_value
                factor = value.par_add_value
                if nlay > 2:
                    for lay in range(nlay-2):
                        if ((lay == 0) & (version == '2.10.1')):
                            contents[-1] += 'linear("H'+key+str(lay+1) + \
                                '", ">" ,'+str(factor)+',"D' + \
                                key+str(lay)+'",0);'
                        else:
                            contents += ['linear("H'+key+str(lay+1)+'", ">" ,' +
                                         str(factor)+',"H'+key+str(lay)+'",0);']

        contents += ['      </text>'
                     '    </ParamSpaceScript>',
                     '  </ParamGroundModel>',
                     '</Dinver>']

        with open("contents.xml", "w") as f:
            for row in contents:
                f.write(row+"\n")
        with tar.open(fname, "w:gz") as f:
            f.add("contents.xml")
        os.remove("contents.xml")
