# This file is part of swprepost, a Python package for surface wave
# inversion pre- and post-processing.
# Copyright (C) 2019-2021 Joseph P. Vantassel (jvantassel@utexas.edu)
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

"""Definition of TargetSet class."""

from typing import List
import tarfile as tar
import os

from swprepost import ModalTarget

class TargetSet():
    """Intelligent container for handling multiple inversion targets."""

    def __init__(self, targets: List[ModalTarget]) -> None:
        """Initialize a `TargetSet` object.

        Parameters
        ----------
        targets : list
            List of `ModalTargets` that define `TargetSet`.

        """
        self.targets = list(targets)

    def cut(self, pmin, pmax, domain="frequency"):
        """Remove data outside of the specified range.

        Parameters
        ----------
        pmin, pmax : float
            New minimum and maximum parameter value in the specified
            domain, respectively.
        domain : {'frequency', 'wavelength'}, optional
            Domain along which to perform the cut.

        Returns
        -------
        None
            May update attributes `frequency`, `velocity`, and
            `velstd`.

        """
        for target in self.targets:
            if isinstance(target, ModalTarget):
                target.cut(pmin=pmin, pmax=pmax, domain=domain)

    def _resample(self, xx, domain="wavelength", inplace=False):
        """Hidden resample function for custom resampling.

        Parameters
        ----------
        xx : ndarray, optional
            Array of new values in the chosen domain.
        domain : {'frequency','wavelength'}, optional
            Resampling domain, default is wavelength.
        inplace : bool, optional
            Determine whether resample is done in place or if the values
            are returned, default is False meaning resampled values are
            returned.

        Returns
        -------
        None or Tuple
            `None` if `resample=False` otherwise returns a `tuple` of
            the form `(frequency, velocity, velstd)`.

        """
        if inplace:
            for target in self.targets:
                if isinstance(target, ModalTarget):
                    target._resample(xx=xx, domain=domain, inplace=inplace)
        else:
            targets = []
            for target in self.targets:
                if isinstance(target, ModalTarget):
                    target = target._resample(xx=xx, domain=domain, inplace=inplace)
                targets.append(target)
            return TargetSet(targets)

    def easy_resample(self, pmin, pmax, pn, res_type="log", domain="wavelength", inplace=False):
        """Resample dispersion curve.

        Resample dispersion curve over a specific range, using log or
        linear sampling in the frequency or wavelength domain.

        Parameters
        ----------
        pmin, pmax : float
            Minimum and maximum parameter value in the resampled
            dispersion data.
        pn : int
            Number of points in the resampled dispersion data.
        res_type : {'log', 'linear'}, optional
            Resample using either logarithmic or linear sampling,
            default is logarithmic.
        domain : {'frequency', 'wavelength'}, optional
            Domain along which to perform the resampling.
        inplace : bool
            Indicating whether the resampling should be done in
            place or if a new `Target` object should be returned.

        Returns
        -------
        None or Target
            If `inplace=True` returns `None`, and may update attributes
            `frequency`, `velocity`, and `velstd`. If `inplace=False`
            a new `Target` object is returned.

        Raises
        ------
        NotImplementedError
            If `res_type` and/or `domain` are not among the options
            specified.

        """
        if inplace:
            for target in self.targets:
                if isinstance(target, ModalTarget):
                    target.easy_resample(pmin, pmax, pn, res_type=res_type, domain=domain, inplace=inplace)
        else:
            targets = []
            for target in self.targets:
                if isinstance(target, ModalTarget):
                    target = target.easy_resample(pmin, pmax, pn, res_type=res_type, domain=domain, inplace=inplace)
                targets.append(target)
            return TargetSet(targets)

    def to_target(self, fname_prefix, version="3"):
        """Write info to the .target file format used by `Dinver`.

        Parameters
        ----------
        fname_prefix : str
            Name of target file without the .target suffix, a
            relative or full path may be provided.
        version : {'3', '2'}, optional
            Major version of Geopsy, default is version 3.

        Returns
        -------
        None
            Writes file to disk.

        Raises
        ------
        NotImplementedError
            If `version` does not match the options provided.

        """
        # TODO (jpv): Handle ell properly.
        __ell_weight = 1
        __ell_def = False
        __ell_mean = 0
        __ell_std = 0

        contents = ["<Dinver>",
                    "  <pluginTag>DispersionCurve</pluginTag>",
                    "  <pluginTitle>Surface Wave Inversion</pluginTitle>"]

        if version in ["2"]:
            contents += [f"  <TargetList>",
                         f"    <ModalCurveTarget type=\"dispersion\">",
                         f"      <selected>true</selected>",
                         f"      <misfitWeight>{self.targets[0].dc_weight}</misfitWeight>",
                         f"      <minimumMisfit>0</minimumMisfit>",
                         f"      <misfitType>L2_Normalized</misfitType>",
                        ]
            # TODO (jpv): Fix dc_weight should be an attribute of all ModalTarget and not set individually for each mode.
            # Essentially it needs to be moved to the TargetSet class and out of the ModalTarget class. Take first one for now.

            for target in self.targets:
                target._sort_data()

                contents += [
                         f"      <ModalCurve>",
                         f"        <name>swprepost</name>",
                         f"        <log>swprepost by Joseph P. Vantassel</log>",
                         f"        <Mode>",
                         f"          <slowness>Phase</slowness>",
                         f"          <polarisation>{target.type.capitalize()}</polarisation>",
                         f"          <ringIndex>0</ringIndex>",
                         f"          <index>{target.mode[0]}</index>",
                         f"        </Mode>"]

            # TODO (jpv): Handle the case where a ModalTarget has multiple potential modes associated with it.

                for x, mean, stddev in zip(target.frequency, target.slowness, target.slostd):
                    contents += [
                                f"        <StatPoint>",
                                f"          <x>{x}</x>",
                                f"          <mean>{mean}</mean>",
                                f"          <stddev>{stddev}</stddev>",
                                f"          <weight>1</weight>",
                                f"          <valid>true</valid>",
                                f"        </StatPoint>",
                                ]
                contents += ["      </ModalCurve>",]
            contents += ["    </ModalCurveTarget>",]

        elif version in ["3"]:
            contents += [f"  <TargetList>",
                         f"    <position>0 0 0</position>",
                         f"    <DispersionTarget type=\"dispersion\">",
                         f"      <selected>true</selected>",
                         f"      <misfitWeight>{self.targets[0].dc_weight}</misfitWeight>",
                         f"      <minimumMisfit>0</minimumMisfit>",
                         f"      <misfitType>L2_LogNormalized</misfitType>",
            ]
            # TODO (jpv): Fix dc_weight should be an attribute of all ModalTarget and not set individually for each mode.
            # Essentially it needs to be moved to the TargetSet class and out of the ModalTarget class. Take first one for now.

            for target in self.targets:
                target._sort_data()

                contents +=[
                         f"      <ModalCurve>",
                         f"        <name>swprepost</name>",
                         f"        <log>swprepost written by J. Vantassel</log>",
                         f"        <enabled>true</enabled>",
                         f"        <Mode>",
                         f"          <slowness>Phase</slowness>",
                         f"          <polarization>{target.type.capitalize()}</polarization>",
                         f"          <ringIndex>0</ringIndex>",
                         f"          <index>{target.mode[0]}</index>",
                         f"        </Mode>"]

                for x, mean, stddev in zip(target.frequency, target.slowness, target.logstd):
                    contents += [f"        <RealStatisticalPoint>",
                                 f"          <x>{x}</x>",
                                 f"          <mean>{mean}</mean>",
                                 f"          <stddev>{stddev}</stddev>",
                                 f"          <weight>1</weight>",
                                 f"          <valid>true</valid>",
                                 f"        </RealStatisticalPoint>"]
                contents += [f"      </ModalCurve>"]
            contents += ["    </DispersionTarget>"]

        else:
            raise NotImplementedError

        contents += ["    <AutocorrTarget>",
                     "      <selected>false</selected>",
                     "      <misfitWeight>1</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_NormalizedBySigmaOnly</misfitType>",
                     "      <AutocorrCurves>",
                     "      </AutocorrCurves>",
                     "    </AutocorrTarget>"]

        contents += ["    <ModalCurveTarget type=\"ellipticity\">",
                     "      <selected>false</selected>",
                     "      <misfitWeight>1</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_Normalized</misfitType>",
                     "    </ModalCurveTarget>"]

        # TODO (jpv): Properly handle ell target.
        selected = "true" if __ell_def else "false"
        contents += [f"    <ValueTarget type=\"ellipticity peak\">",
                     f"      <selected>{selected}</selected>",
                     f"      <misfitWeight>{__ell_weight}</misfitWeight>",
                     f"      <minimumMisfit>0</minimumMisfit>",
                     f"      <misfitType>L2_LogNormalized</misfitType>"]

        if version in ["2"]:
            contents += [f"      <StatValue>",
                         f"        <mean>{__ell_mean}</mean>",
                         f"        <stddev>{__ell_std}</stddev>",
                         f"        <weight>1</weight>",
                         f"        <valid>{selected}</valid>",
                         f"      </StatValue>",
                         f"    </ValueTarget>"]
        elif version in ["3"]:
            contents += [f"      <RealStatisticalValue>",
                         f"        <mean>{__ell_mean}</mean>",
                         f"        <stddev>{__ell_std}</stddev>",
                         f"        <weight>1</weight>",
                         f"        <valid>{selected}</valid>",
                         f"      </RealStatisticalValue>",
                         f"    </ValueTarget>"]

        contents += ["    <RefractionTarget type=\"Vp\">",
                     "      <selected>false</selected>",
                     "      <misfitWeight>1</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_Normalized</misfitType>",
                     "    </RefractionTarget>"]

        contents += ["    <RefractionTarget type=\"Vs\">",
                     "      <selected>false</selected>",
                     "      <misfitWeight>1</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_Normalized</misfitType>",
                     "    </RefractionTarget>"]

        if version in ["3"]:
            contents += ["    <MagnetoTelluricTarget>",
                         "      <selected>false</selected>",
                         "      <misfitWeight>1</misfitWeight>",
                         "      <minimumMisfit>0</minimumMisfit>",
                         "      <misfitType>L2_Normalized</misfitType>",
                         "    </MagnetoTelluricTarget>"]

        contents += ["  </TargetList>",
                     "</Dinver>"]

        with open("contents.xml", "w", encoding="utf-8") as f:
            for row in contents:
                f.write(row+"\n")
        with tar.open(fname_prefix+".target", "w:gz") as f:
            f.add("contents.xml")
        os.remove("contents.xml")

    # TODO (jpv): Write from_target class method.
    # @classmethod
    # def from_target(cls, fname_prefix, version="3"):
    #     """Create from TargetSet from Target file.

    #     Note that this method is still largely experimental and may
    #     not work for all cases.

    #     Parameters
    #     ----------
    #     fname_prefix : str
    #         Name of target file to be opened excluding the `.target`
    #         suffix, may include the relative or full path.
    #     version : {'2', '3'}, optional
    #         Major version of Geopsy that was used to write the target
    #         file, default is '3'.

    #     Returns
    #     -------
    #         Instantiated `Target` object.

    #     """
    #     with tar.open(fname_prefix+".target", "r:gz") as a:
    #         a.extractall()

    #     try:
    #         with open("contents.xml", "r", encoding="utf-8") as f:
    #             lines = f.read()
    #         if "<Dinver>" not in lines[:10]:
    #             raise RuntimeError
    #     except (UnicodeDecodeError, RuntimeError):
    #         with open("contents.xml", "r", encoding="utf_16_le") as f:
    #             lines = f.read()
    #         if "<Dinver>" not in lines[:10]:
    #             raise ValueError("File encoding not recognized.")

    #     os.remove("contents.xml")

    #     number = f"(-?\d+.?\d*[eE]?[+-]?\d*)"
    #     newline = r"\W+"
    #     regex = f"<x>{number}</x>{newline}<mean>{number}</mean>{newline}<stddev>{number}</stddev>"
    #     search = re.findall(regex, lines)
    #     xs, means, stddevs = np.zeros(len(search)), np.zeros(
    #         len(search)), np.zeros(len(search))
    #     for cid, item in enumerate(search):
    #         tmp_x, tmp_mean, tmp_stddev = item
    #         xs[cid] = float(tmp_x)
    #         means[cid] = float(tmp_mean)
    #         stddevs[cid] = float(tmp_stddev)

    #     frequency = xs
    #     velocity = 1/means
    #     if version == "2":
    #         inv_stddevs = 1/stddevs
    #         velstd = 0.5*(np.sqrt(inv_stddevs*inv_stddevs +
    #                               4*velocity*velocity) - inv_stddevs)
    #     elif version == "3":
    #         cov = stddevs - np.sqrt(stddevs*stddevs - 2*stddevs + 2)
    #         velstd = cov*velocity
    #     else:
    #         msg = f"version={version}, is not recognized, refer to documentation for accepted versions."
    #         raise NotImplementedError(msg)

    #     return cls(frequecy, velocity, velstd)

    def __eq__(self, obj):
        """Check if two TargetSet objects are equal."""
        if len(self.targets) != len(obj.targets):
            return False

        for a, b in zip(self.targets, obj.targets):
            if a != b:
                return False
        return True

    def __repr__(self):
        """Unambiguous representation of a TargetSet object."""
        repr=""
        for target in self.targets:
            repr += f"{target.__repr__()}\n"
        return repr

    def __str__(self):
        """Human readable representation of a TargetSet object."""
        return f"TargetSet with {len(self.targets)} targets."
