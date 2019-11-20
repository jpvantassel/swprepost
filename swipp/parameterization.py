"""This file includes a class for developing parameterizations for use
in the open-source software Dinver, part of the Geopsy suite."""

import tarfile as tar
import os
from .parameter import Parameter
import warnings
import logging
logging.Logger(name=__name__)


class Parameterization():
    """Class for developing inversion parameterizations.

    `Parameter` is intended to be used for developing various simple
    parameterization files for use in the open-source software Dinver.
    While parameterizations can be built quickly using this tool, it
    does have limited functionality to that of the full user interface.
    And so it is recommended that the user, batch create general
    parameterizations using this tool, then fine tune any necessary
    using the Dinver user interface.

    Attributes:
        This class contains no public attributes.
    """

    @staticmethod
    def check_parameter(name, val):
        """Check input for the parameter."""
        logging.info(f"Checking {name}...")

        if val.get("type"):
            if val["type"] not in ["FX", "FTL", "LN", "LNI", "LR", "UserDefined"]:
                raise ValueError(f"Invalid type in {name}.")
        else:
            val.update({"type": "UserDefined"})

        if not val.get("value"):
            val.update({"value": "UserDefined"})

        if val.get("thickness"):
            logging.info(f"{name} is defined with thickness.")
            if val.get("depth") is not None:
                raise ValueError(
                    f"{name} must include either `thickness` or `depth`, not both.")
            keys = ["thickness"]
            test_len = len(val["thickness"]["min"])
        elif val.get("depth"):
            logging.info(f"{name} is defined with depth.")
            if val.get("thickness") is not None:
                raise ValueError(
                    f"{name} must include either `thickness` or `depth`, not both.")
            keys = ["depth"]
            test_len = len(val["depth"]["min"])
        else:
            raise ValueError(f"{name} must have `thickness` or `depth`.")

        logging.debug(f"len of parameters for {name} is {val}.")
        keys.append("par")
        for key in keys:
            for value in val[key].values():
                if test_len != len(value):
                    raise ValueError(f"Length of {name} is not consistent.")

    def __init__(self, vp, pr, vs, rh):
        """ Initialize an instance of the Parameter class.

        Initialize a parameterization using Shear Wave Velocity (Vs),
        Compression Wave Velocity (Vp), Poisson's Ratio, Mass Density,
        and minimum and maximum Wavelengths available.

        Args:
            vp, pr, vs, rh: Are dictionaries of the form:
                {'thickness':{'min':[min_thicknesses],
                              'max':[max_thicknesses]
                             },
                'depth':{'min':[min_depths],
                         'max':[max_depths]
                        },
                'par':{'min':[par_mins],
                        'max':[par_maxs],
                        'rev':[par_revs]
                      },
                'type':type
                'value':value
                }
                where either 'thickness' or 'depth' may exist for any
                given parameterization. 'par' is for the parameter so if
                this dictionary is for the vs parameter then the entries
                in 'par' will represent Vs values.

                All quanties represented by brackets are lists of floats
                or ints with the exception of [par_revs] which is a list
                of booleans.

                'type' and 'value' are optional keys corresponding to a 
                string that denotes the type and value of layering used.
                It should generally not be used as the correct default 
                value will be assigned if the appropriate constructor is
                used. Refer to the class methods `from_xlsx` and 
                `from_min_max` to understand how to use the alternate
                constructors.

        Returns:
            An initialized instance of the Parameter class.

        Raises:
            Various exceptions including: TypeError, ValueError,
                NotImplementedError with messages detailing the problem
                encountered and how to repair it.
        """

        for name, par in zip(("vp", "pr", "vs", "rh"), [vp, pr, vs, rh]):
            self.check_parameter(name, par)

        self.vp = vp
        self.pr = pr
        self.vs = vs
        self.rh = rh

    @classmethod
    def from_min_max(cls, vp, pr, vs, rh, wv, factor=2):
        """Intilize an instance of a Parameter class from an estimate of
        minimum and maximum values of Vp, Poisson's Ratio, Vs, and
        Mass Density.

        Args:
            vp, pr, vs, rh: Are lists of the form [type, value, min,
                max, bool] where type is discussed below, min and max
                are the minimum and maximum values which the parameter
                may assume, and bool indicates whether a non-typical
                condition (e.g., Vs decreasing with depth) is allowed.

                Type:
                    If type = 'FX' layinering is fixed, the next and only
                    argument is its value.
                    Ex. ['FX', value]

                    If type = 'FTL' layinering follows fixed thickness
                    layinering, the second argument is then the number of
                    layiners desired, followed by their thickness, min,
                    max, and bool for reversal condition.
                    Ex. ['FTL', nlay, thickness, min, max, bool]

                    If type = 'LN' layering follows layering by
                    number, the next argument is number of layers
                    followed by the min and max for those layers and
                    bool for reversal condition.
                    Ex. ['LN', ln, min, max, reversal]


                    If type = 'LNI' layering follows layering by number
                    with increasing thickness, which is similar to 'LN',
                    but with the requirement that the thickness of each
                    layer increases with depth.
                    Ex. ['LNI', ln, fac, min, max, reversal]


                    If type = 'LR' layering follows the layering ratio,
                    the next arguemnt is the layering ratio followed by
                    the min and max for those layers and bool for the
                    reversal conditon.
                    Ex. ['LR', lr, min, max, reversal]

                An Example:

                    vs = ['LR', 3.0, 100, 300, False]

                Vs is to follow a LR=3.0, with the minimum value of Vs
                set at 100 m/s and maximum value of Vs set at 300 m/s,
                with no velocity reversals permitted.

            wv: List of the form [min_wave, max_wave] where min_wave and
                max_wave are floats or ints idicating the minimum and
                maximum measured wavelength from the fundemental mode
                Rayleigh wave disperison.

            factor: Float or int by which the maximum wavelength is
                divided to estimate the maxium depth of profiling.

        Returns:
            An initialized instance of the Parameter class.

        Raises:
            Various exceptions including: TypeError, ValueError,
                NotImplementedError with messages detailing the problem
                encountered and how to repair it.
        """
        input_arguements = {"vs": vs, "vp": vp, "pr": pr, "rh": rh}
        valid_options = ('FX', 'FTL', 'LN', 'LNI', 'LR')
        for key, value in input_arguements.items():
            # Ensure entry is a list
            if type(value) not in (list,):
                raise TypeError("Entry for argument {} must be a list, not {}."
                                .format(key, type(value)))

            # Ensure the first entry of that list is a valid option
            if value[0] not in valid_options:
                raise ValueError("{} entered for {} not recognized use {}."
                                 .format(value[0], key, valid_options))

            # Fixed value must be positve integer or float
            if value[0] == 'FX':
                if type(value[1]) not in (int, float):
                    raise TypeError("Fixed value must be int or float. Not {}."
                                    .format(type(value[1])))
                if value[1] <= 0:
                    raise ValueError("Fixed value must be postive.")

            # Number layers must be an int where thickness is pos int or float.
            elif value[0] == 'FTL':
                pass
            # Number of layers is an integer greater than zero
            elif value[0] == 'LN':
                if type(value[1]) not in (int,):
                    raise TypeError("Number of layers must be integer.")
                if value[1] <= 0:
                    raise ValueError("Number of layers must be postive.")

            # Number of layers is integer and factor positive int or float > 1.
            elif value[0] == 'LNI':
                if type(value[1]) not in (int,):
                    raise TypeError(
                        "Number of layers for {} must be integer. Not {}."
                        .format(key, type(value[1])))
                if value[1] < 2:
                    raise ValueError("Number of layers for {} must be >= 2."
                                     .format(key))
                if type(value[2]) not in (int, float):
                    raise TypeError(
                        "layer factor for {} must be integer or float. Not {}."
                        .format(key, type(value[2])))
                if value[2] <= 1:
                    raise ValueError("layer factor {} must be greater than 1."
                                     .format(key))

            # layering ratio is integer or float greater than one.
            elif value[0] == 'LR':
                if type(value[1]) not in (int, float):
                    raise TypeError(
                        "layering ratio must be integer or float.")
                if value[1] <= 1:
                    raise ValueError(
                        "layering ratio must be greater than 1.")
            else:
                raise NotImplementedError(
                    "This functionality is not yet implemented.")

        vp_out, pr_out, vs_out, rh_out = {}, {}, {}, {}
        pars_out = [vp_out, pr_out, vs_out, rh_out]
        pars_in = [vp, pr, vs, rh]
        for par_in, par_out in zip(pars_in, pars_out):
            if par_in[0] == "FX":
                par_out.update({"type": "FX",
                                "value": "FX",
                                "depth": {"min": [1122],
                                          "max": [1994]},
                                "par": {"min": [par_in[1]],
                                        "max": [par_in[1]],
                                        "rev": [False]}})

            elif par_in[0] == "FTL":
                min_thk, max_thk = cls._set_depth_ftl(wv,
                                                      par_in[1],
                                                      par_in[2])
                par_out.update({"type": "FTL",
                                "value": str(par_in[1]),
                                "thickness": {"min": min_thk,
                                              "max": max_thk},
                                "par": {"min": [par_in[3]]*par_in[1],
                                        "max": [par_in[4]]*par_in[1],
                                        "rev": [par_in[5]]*par_in[1]}})
            elif par_in[0] == "LN":
                min_thk, max_thk = cls._set_depth_ln(wv,
                                                     par_in[1],
                                                     factor,
                                                     increasing=False)
                par_out.update({"type": "LN",
                                "value": str(par_in[1]),
                                "thickness": {"min": min_thk,
                                              "max": max_thk},
                                "par": {"min": [par_in[2]]*par_in[1],
                                        "max": [par_in[3]]*par_in[1],
                                        "rev": [par_in[4]]*par_in[1]}})
            elif par_in[0] == "LNI":
                min_thk, max_thk = cls._set_depth_ln(wv,
                                                     par_in[1],
                                                     factor,
                                                     increasing=True)
                par_out.update({"type": "LNI",
                                "value": f"{par_in[1]} {par_in[2]}",
                                "thickness": {"min": min_thk,
                                              "max": max_thk},
                                "par": {"min": [par_in[3]]*par_in[1],
                                        "max": [par_in[4]]*par_in[1],
                                        "rev": [par_in[5]]*par_in[1]}})
            elif par_in[0] == "LR":
                min_dpt, max_dpt = cls._depth_lr(wv, par_in[1], factor)
                par_out.update({"type": "LR",
                                "value": str(par_in[1]),
                                "depth": {"min": min_dpt,
                                          "max": max_dpt},
                                "par": {"min": [par_in[2]]*len(min_dpt),
                                        "max": [par_in[3]]*len(min_dpt),
                                        "rev": [par_in[4]]*len(min_dpt)}})
            else:
                raise NameError("Layering '{}' not found.".format(par_in[0]))
        return cls(vp_out, pr_out, vs_out, rh_out)

    def write_to_file(self, fname, version='2.9.0'):
        """Write paramterization to .param that can be read by DINVER.

        Args:
            fname: String, such that the file is named "fname.param".

            version: String, {'2.9.0', '2.10.1'}.
                Note '2.9.0' is the version compiled on Stampede2.

        Returns:
            This method returns no value, but writes .param file to disk.

        Raises:
            KeyError: If version does not match that required exactly.
        """
        avail_versions = {'2.9.0': '2.9.0', '2.10.1': '2.10.1'}
        version = avail_versions[version]

        contents = ['<Dinver>',
                    '  <pluginTag>DispersionCurve</pluginTag>',
                    '  <pluginTitle>Surface Wave Inversion</pluginTitle>',
                    '  <ParamGroundModel>']

        keys = ["Vp", "Nu", "Vs", "Rho"]
        values = [self.vp, self.pr, self.vs, self.rh]

        for key, value in zip(keys, values):
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
                             '      <defaultMinimum>0.2000000000000000111</defaultMinimum>',
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
                raise NotImplementedError(
                    "Selection {} not implemented".format(key))

            if value.get("thickness"):
                isdepth = "false"
                dh = value["thickness"]
            else:
                dh = value["depth"]
                isdepth = "true"
            par = value["par"]
            for lnum, (dhmin, dhmax, pmin, pmax, rev) in enumerate(zip(dh["min"], dh["max"], par["min"], par["max"], par["rev"])):
                rev_check = 'true' if not rev else 'false'
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

        for key, value in zip(keys, values):
            if value["type"] == "LNI":
                factor = value["value"]
                nlay = len(value["par"]["min"])
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
        with tar.open(fname+".param", "w:gz") as f:
            f.add("contents.xml")
        os.remove("contents.xml")
