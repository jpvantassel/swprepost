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

"""Definition of Target class."""

import tarfile as tar
import os
import warnings
import re
import logging

import matplotlib.pyplot as plt
import numpy as np

from swprepost import CurveUncertain

logger = logging.getLogger(name=__name__)


class Target(CurveUncertain):
    """Class for manipulating inversion target information.

    `Target` is a class for loading, manipulating, and writting
    target information in preparation for surface-wave inversion.

    Attributes
    ----------
    frequency, velocity, velstd : array-like
        Vectors of frequency, velocity, and velocity standard
        deviation values in the experimental dispersion
        curve (one per point).

    """

    def __init__(self, frequency, velocity, velstd=0.05):
        """Instantiate a Target object.

        Parameters
        ----------
        frequency, velocity : array-like
            Vector of frequency and velocity values respectively
            in the experimental dispersion curve (one per point).
        velstd : None, float, array-like, optional
            Velocity standard deviation of the experimental
            dispersion curve. If `None`, no standard deviation is
            defined. If `float`, a constant coefficient of variation
            (COV) is applied, the default is 0.05. If `array-like`,
            standard deviation is defined point-by-point.

        Returns
        -------
        Target
            Instantiated `Target` object.

        Raises
        ------
        TypeError
            If `frequency`, `velocity`, and `velstd` are not
            `array-like`.
        ValueError
            If `velstd` is `float` and the value is less than zero.

        """
        logger.info("Howdy!")

        # if velstd is None:
        #     velstd = np.zeros_like(velocity, dtype=np.double).tolist()
        if isinstance(velstd, float):
            velstd = (np.array(velocity, dtype=np.double)*velstd).tolist()

        super().__init__(x=frequency, y=velocity, yerr=velstd, xerr=None)

        self._sort_data()
        self.dc_weight = 1

    def _sort_data(self):
        """Sort attributes by frequency from smallest to largest."""
        sort_ids = np.argsort(self._x)
        self._yerr = self._yerr[sort_ids] if self._isyerr else None
        self._y = self._y[sort_ids]
        self._x = self._x[sort_ids]

    def _check_new_value(self, value):
        value = np.array(value, dtype=np.double)
        if value.shape == self._x.shape:
            return value
        else:
            msg = "`frequency`, `velocity`, and `velstd` must be the same size."
            raise ValueError(msg)

    @property
    def frequency(self):
        return self._x

    @frequency.setter
    def frequency(self, value):
        self._x = self._check_new_value(value)

    @property
    def velocity(self):
        return self._y

    @velocity.setter
    def velocity(self, value):
        self._y = self._check_new_value(value)

    @property
    def wavelength(self):
        return self._y/self._x

    @property
    def velstd(self):
        if self._isyerr:
            return self._yerr
        else:
            self._isyerr = True
            self._yerr = np.zeros_like(self._x)
            return self._yerr

    @velstd.setter
    def velstd(self, value):
        self._yerr = self._check_new_value(value)

    @property
    def is_no_velstd(self):
        """Indicates `True` if every point has zero `velstd`."""
        return all(std == 0 for std in self.velstd)

    @property
    def cov(self):
        return self.velstd/self._y

    @property
    def slowness(self):
        return 1/self._y

    @property
    def slostd(self):
        """Get slowness standard deviation."""
        upper = self.velocity+self.velstd
        lower = self.velocity-self.velstd
        # return 0.5*((1/lower - self.slowness) + (self.slowness - 1/upper))
        return 0.5*(1/lower - 1/upper)

    @property
    def logstd(self):
        """Get logarithmic slowness standard deviation."""
        p = self.slowness
        pstd = self.slowness * self.cov
        # From DispersionProxy.cpp Line 194
        return 0.5*(((p+pstd)/p) + (p/(p-pstd)))

    @classmethod
    def from_csv(cls, fname, commentcharacter="#"):
        """Construct instance from csv file.

        Read a comma seperated values (csv) file with header line(s) to
        construct a target object.

        Parameters
        ----------
        fname : str
            Name or path to file containing surface-wave dispersion.
            The file should have at a minimum two columns of frequency
            in Hz and velocity in m/s. A third column velocity standard
            deviation in m/s may also be provided.
        commentcharacter : str, optional
            Character at the beginning of a line denoting a
            comment, default value is '#'.

        Returns
        -------
        Target
            Initialized `Target` object.

        Raises
        ------
        ValueError
            If the format of the input file does not match that
            detailed above.

        """
        with open(fname, "r") as f:
            lines = f.read().splitlines()

        frequency, velocity, velstd = [], [], []
        for line in lines:
            # Skip commented lines
            if line[0] == commentcharacter:
                continue
            # If three entries -> velstd is provided extract all three
            elif line.count(",") == 2:
                a, b, c = line.split(",")
            # If two entries provided -> assume freq and vel, velstd=0
            elif line.count(",") == 1:
                a, b = line.split(",")
                c = 0
            else:
                msg = "Format of input file not recognized. Refer to documentation."
                raise ValueError(msg)
            frequency.append(float(a))
            velocity.append(float(b))
            velstd.append(float(c))
        return cls(frequency, velocity, velstd)

    def setcov(self, cov):
        """Set coefficient of variation (COV) to a constant value.

        This method may be used if no velocity standard deviation was
        measured or provided. In general, a COV between 0.05 and 0.10
        should provide a reasonable estimate of the uncertainty.

        If velocity standard deviations have already been provided this
        method will overwrite them. If this is not desired refer to
        :meth: `setmincov`.

        Parameters
        ----------
        cov : float
            Coefficient of variation to be used to replace `velstd`.

        Returns
        -------
        None
            Updates attribute `velstd`.

        Raises
        ------
            ValueError:
                If `cov` < 0.

        """
        self._is_valid_cov(cov)
        self.velstd = self.velocity*cov
        self._isyerr = True

    @staticmethod
    def _is_valid_cov(cov):
        if cov < 0:
            raise ValueError(f"`cov` must be greater than zero, not {cov}.")

    def setmincov(self, cov):
        """Set minimum coefficient of variation (COV).

        If uncertainty in the experimental data has been provided, this
        method allows the setting of a minimum COV, where all data
        points with uncertainty below this threshold will be modified
        and those above this threshold will be left alone.

        If no measure of uncertainty has been provided, prefer :meth:
        `setcov`.

        Parameters
        ----------
        cov : float
            Minimum allowable COV.

        Returns
        -------
        None
            May update attribute `velstd`.

        Raises
        ------
        ValueError
            If `cov` < 0.

        """
        self._is_valid_cov(cov)
        update_ids = np.where(self.cov < cov)
        self.velstd[update_ids] = self.velocity[update_ids]*cov
        self._isyerr = True

    def pseudo_depth(self, depth_factor=2.5):
        """Estimate depth based on the experimental dispersion data.

        This method, along with :meth: `pseudo-vs`, may be useful to
        create plots of pseudo-Vs vs pseudo-depth for selecting
        approprate boundaries for parameter limits in the inverison
        stage.

        Parameters
        ----------
        depth_factor : float, optional
            Factor by which the mean wavelegnth is divided to
            produce an estimate of depth. Typical are between 2 and 3,
            default 2.5.

        Returns
        -------
        ndarray
            Of pseudo-depth.

        """
        if (depth_factor > 3) | (depth_factor < 2):
            msg = "`depth_factor` is outside the typical range. See docs."
            warnings.warn(msg)
        return self.wavelength/depth_factor

    def pseudo_vs(self, velocity_factor=1.1):
        """Estimate Vs based on the experimental dispersion data.

        This method, along with :meth: `pseudo-depth`, may be useful to
        create plots of pseudo-Vs vs pseudo-depth for selecting
        approprate boundaries for parameter limits.

        Parameters
        ----------
        velocity_factor : float, optional
            Factor by which the mean Rayleigh wave velocity is
            multiplied to produce an estimate of shear-wave
            velocity. Typically range between 1 and 1.2, and is
            dependent upon the expected Poisson's ratio, default is 1.1.

        Returns
        -------
        ndarray
            Of pseudo-vs.

        """
        if (velocity_factor > 1.2) | (velocity_factor < 1):
            msg = "`velocity_factor` is outside the typical range. See documenation."
            warnings.warn(msg)
        return self.velocity*velocity_factor

    def _set_domain(self, domain):
        if domain == "wavelength":
            return self.wavelength
        elif domain == "frequency":
            return self.frequency
        else:
            raise NotImplementedError(f"domain={domain}, not recognized.")

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
        x = self._set_domain(domain)
        keep_ids = np.where((x >= pmin) & (x <= pmax))
        self._x = self.frequency[keep_ids]
        self._y = self.velocity[keep_ids]
        self._yerr = self.velstd[keep_ids]

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
        x = self._set_domain(domain)
        res_fxn_y = self.resample_function(x, self.velocity, kind="cubic")
        res_fxn_yerr = self.resample_function(x, self.velstd, kind="cubic")

        results = super().resample(xx=xx, inplace=False,
                                   res_fxn=(res_fxn_y, None, res_fxn_yerr))
        xx, new_vel, new_velstd, = results

        if domain == "frequency":
            new_frq = xx
        elif domain == "wavelength":
            new_frq = new_vel/xx

        if inplace:
            self._x = new_frq
            self._y = new_vel
            self._yerr = new_velstd
        else:
            return Target(new_frq, new_vel, new_velstd)

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
        # Check input.
        if pmax < pmin:
            pmin, pmax = (pmax, pmin)
        pn = int(pn)
        if not pn > 0:
            raise ValueError(f"`pn` must be greater than zero, not {pn}.")

        if res_type == "log":
            xx = np.geomspace(pmin, pmax, pn)
        elif res_type == "linear":
            xx = np.linspace(pmin, pmax, pn)
        else:
            msg = f"`res_type`={res_type}, has not been implemented."
            raise NotImplementedError(msg)

        if inplace:
            self._resample(xx, domain=domain, inplace=inplace)
        else:
            return self._resample(xx, domain=domain, inplace=inplace)

    @property
    def vr40(self):
        """Estimate Rayleigh wave velocity at a wavelength of 40m."""
        wavelength = self.wavelength
        if (max(wavelength) > 40) & (min(wavelength) < 40):
            obj = self.easy_resample(pmin=40, pmax=40, pn=1, res_type="linear",
                                     domain="wavelength", inplace=False)
            return float(obj.velocity)
        else:
            warnings.warn("A wavelength of 40m is out of range.")

    def to_txt_dinver(self, fname, version="3"):
        """Write in text format accepted by `Dinver's` pre-processor.

        Parameters
        ----------
        fname : str
            Name of output file, may a relative or full path.
        version : {'3', '2'}, optional
            Major version of Geopsy, default is version 3.

        Returns
        -------
        None
            Writes file to disk.

        """
        if version == "2":
            stddevs = self.slostd
        elif version == "3":
            stddevs = self.logstd
        else:
            msg = f"version={version} is not implemented, refer to documentation."
            raise NotImplementedError(msg)

        with open(fname, "w") as f:
            for frq, slo, std in zip(self.frequency, self.slowness, stddevs):
                f.write(f"{frq}\t{slo}\t{std}\n")

    @classmethod
    def from_txt_dinver(cls, fname, version="3"):
        """Create from text format accepted by `Dinver's` pre-processor.

        Parameters
        ----------
        fname : str
            Name of output file, may a relative or full path.
        version : {'3', '2'}, optional
            Major version of Geopsy, default is version 3.

        Returns
        -------
        Target
            Instantiated `Target` with information from file.

        """
        with open(fname, "r") as f:
            lines = f.readlines()

        frqs, slos, stds = [], [], []
        for line in lines:
            frq, slo, std = line.split("\t")
            frqs.append(frq)
            slos.append(slo)
            stds.append(std)

        frq = np.array(frqs, dtype=np.double)
        slo = np.array(slos, dtype=np.double)
        vel = 1/slo
        std = np.array(stds, dtype=np.double)

        if version == "2":
            velstd = (1 - np.sqrt(1 - 4*std*std*vel*vel))/(2*std)
        elif version == "3":
            cov = std - np.sqrt(std*std - 2*std + 2)
            velstd = cov*vel
        else:
            msg = f"version={version} is not implemented, refer to documentation."
            raise NotImplementedError(msg)

        return cls(frq, vel, velstd)

    def to_csv(self, fname):
        """Write in text format readily accepted by `swprepost`.

        Parameters
        ----------
        fname : str
            Name of output file, may a relative or full path.

        Returns
        -------
        None
            Writes file to disk.

        """
        with open(fname, "w") as f:
            f.write("#Frequency,Velocity,Velstd\n")
            for c_frq, c_vel, c_velstd in zip(self.frequency, self.velocity, self.velstd):
                f.write(f"{c_frq},{c_vel},{c_velstd}\n")

    def to_txt_swipp(self, fname):
        """Write in text format readily accepted by `swprepost`.

        Parameters
        ----------
        fname : str
            Name of output file, may a relative or full path.

        Returns
        -------
        None
            Writes file to disk.

        """
        msg = "to_txt_swipp is deprecated, perfer to_csv instead."
        warnings.warn(msg, DeprecationWarning)
        self.to_csv(fname)

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

        self._sort_data()

        # TODO (jpv): Decide on how best to include ell.
        self.__ell_weight = 1
        self.__ell_def = False
        self.__ell_mean = 0
        self.__ell_std = 0

        contents = ["<Dinver>",
                    "  <pluginTag>DispersionCurve</pluginTag>",
                    "  <pluginTitle>Surface Wave Inversion</pluginTitle>"]

        if version in ["2"]:
            contents += [f"  <TargetList>",
                         f"    <ModalCurveTarget type=\"dispersion\">",
                         f"      <selected>true</selected>",
                         f"      <misfitWeight>{self.dc_weight}</misfitWeight>",
                         f"      <minimumMisfit>0</minimumMisfit>",
                         f"      <misfitType>L2_Normalized</misfitType>",
                         f"      <ModalCurve>",
                         f"        <name>swprepost</name>",
                         f"        <log>swprepost by Joseph P. Vantassel</log>",
                         f"        <Mode>",
                         f"          <slowness>Phase</slowness>",
                         f"          <polarisation>Rayleigh</polarisation>",
                         f"          <ringIndex>0</ringIndex>",
                         f"          <index>0</index>",
                         f"        </Mode>"]
        elif version in ["3"]:
            contents += [f"  <TargetList>",
                         f"    <position>0 0 0</position>",
                         f"    <DispersionTarget type=\"dispersion\">",
                         f"      <selected>true</selected>",
                         f"      <misfitWeight>{self.dc_weight}</misfitWeight>",
                         f"      <minimumMisfit>0</minimumMisfit>",
                         f"      <misfitType>L2_LogNormalized</misfitType>",
                         f"      <ModalCurve>",
                         f"        <name>swprepost</name>",
                         f"        <log>swprepost written by J. Vantassel</log>",
                         f"        <enabled>true</enabled>",
                         f"        <Mode>",
                         f"          <slowness>Phase</slowness>",
                         f"          <polarization>Rayleigh</polarization>",
                         f"          <ringIndex>0</ringIndex>",
                         f"          <index>0</index>",
                         f"        </Mode>"]
        else:
            raise NotImplementedError

        if version in ["2"]:
            for x, mean, stddev in zip(self.frequency, self.slowness, self.slostd):
                contents += [f"        <StatPoint>",
                             f"          <x>{x}</x>",
                             f"          <mean>{mean}</mean>",
                             f"          <stddev>{stddev}</stddev>",
                             f"          <weight>1</weight>",
                             f"          <valid>true</valid>",
                             f"        </StatPoint>"]

        elif version in ["3"]:
            for x, mean, stddev in zip(self.frequency, self.slowness, self.logstd):
                contents += [f"        <RealStatisticalPoint>",
                             f"          <x>{x}</x>",
                             f"          <mean>{mean}</mean>",
                             f"          <stddev>{stddev}</stddev>",
                             f"          <weight>1</weight>",
                             f"          <valid>true</valid>",
                             f"        </RealStatisticalPoint>"]

        contents += ["      </ModalCurve>"]

        if version in ["2"]:
            contents += ["    </ModalCurveTarget>"]

        elif version in ["3"]:
            contents += ["    </DispersionTarget>"]

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

        selected = "true" if self.__ell_def else "false"
        contents += [f"    <ValueTarget type=\"ellipticity peak\">",
                     f"      <selected>{selected}</selected>",
                     f"      <misfitWeight>{self.__ell_weight}</misfitWeight>",
                     f"      <minimumMisfit>0</minimumMisfit>",
                     f"      <misfitType>L2_LogNormalized</misfitType>"]

        if version in ["2"]:
            contents += [f"      <StatValue>",
                         f"        <mean>{self.__ell_mean}</mean>",
                         f"        <stddev>{self.__ell_std}</stddev>",
                         f"        <weight>1</weight>",
                         f"        <valid>{selected}</valid>",
                         f"      </StatValue>",
                         f"    </ValueTarget>"]
        elif version in ["3"]:
            contents += [f"      <RealStatisticalValue>",
                         f"        <mean>{self.__ell_mean}</mean>",
                         f"        <stddev>{self.__ell_std}</stddev>",
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

    @classmethod
    def from_target(cls, fname_prefix, version="3"):
        """Create from target file.

        Note that this method is still largely experimental and may
        not work for all cases.

        Parameters
        ----------
        fname_prefix : str
            Name of target file to be opened excluding the `.target`
            suffix, may include the relative or full path.
        version : {'2', '3'}, optional
            Major version of Geopsy that was used to write the target
            file, default is '3'.

        Returns
        -------
            Instantiated `Target` object.

        """
        with tar.open(fname_prefix+".target", "r:gz") as a:
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

        number = f"(-?\d+.?\d*[eE]?[+-]?\d*)"
        newline = r"\W+"
        regex = f"<x>{number}</x>{newline}<mean>{number}</mean>{newline}<stddev>{number}</stddev>"
        search = re.findall(regex, lines)
        xs, means, stddevs = np.zeros(len(search)), np.zeros(
            len(search)), np.zeros(len(search))
        for cid, item in enumerate(search):
            tmp_x, tmp_mean, tmp_stddev = item
            xs[cid] = float(tmp_x)
            means[cid] = float(tmp_mean)
            stddevs[cid] = float(tmp_stddev)

        frequency = xs
        velocity = 1/means
        if version == "2":
            inv_stddevs = 1/stddevs
            velstd = 0.5*(np.sqrt(inv_stddevs*inv_stddevs +
                                  4*velocity*velocity) - inv_stddevs)
        elif version == "3":
            cov = stddevs - np.sqrt(stddevs*stddevs - 2*stddevs + 2)
            velstd = cov*velocity
        else:
            msg = f"version={version}, is not recognized, refer to documentation for accepted versions."
            raise NotImplementedError(msg)

        return cls(frequency, velocity, velstd)

    def __eq__(self, obj):
        """Check if two target objects are equal."""
        if self.frequency.size == obj.frequency.size:
            for attr in ["frequency", "velocity", "velstd"]:
                for f1, f2 in zip(np.round(getattr(self, attr), 6), np.round(getattr(obj, attr), 6)):
                    if f1 != f2:
                        return False
        else:
            return False
        return True

    def __repr__(self):
        """Unambiguous representation of Target object."""
        frq_str = str(np.round(self.frequency, 2))
        vel_str = str(np.round(self.velocity, 2))
        std_str = str(np.round(self.velstd, 2))
        return f"Target(frequency={frq_str}, velocity={vel_str}, velstd={std_str})"

    def __str__(self):
        """Human readable represetnation of a Target object."""
        return f"Target with {len(self.frequency)} frequency/wavelength points"

    def plot(self, x="frequency", y="velocity", yerr="velstd", ax=None,
             figkwargs=None, errorbarkwargs=None):  # pragma: no cover
        """Plot `Target` information.

        Parameters
        ----------
        x : {'frequency', 'wavelength'}, optional
            Select what should be plotted along the x-axis, default
            is 'frequency'.
        y : {'velocity', 'slowness'}, optional
            Select what should be plotted along the y-axis, default
            is 'velocity'.
        yerr : {'velstd', 'slostd'}, optional
            Select what should be plotted as the y-error, default
            is 'velstd'.
        ax : Axis, optional
            Provide an axes on which to plot, default is `None`
            meaning an axes will be created on-the-fly.
        figkwargs : dict
            Additional keyword arguments defining the `Figure`. Ignored
            if `ax` is defined.
        errorbarkwargs : dict
            Additional keyword arguements defining the sytling of the
            errorbar plot.


        Returns
        -------
        None or Tuple
            If `ax` is defined this method returns returns `None`.
            If `ax=None` this method returns a `tuple` of the form
            `(fig, ax)` where `fig` is a `Figure` object and `ax` is an
            `Axes` object.

        """
        ax_was_none = False
        if ax is None:
            figdefaults = dict(figsize=(4, 3), dpi=150)
            _figkwargs = {**figdefaults, **figkwargs}
            fig, ax = plt.subplots(**_figkwargs)
            ax_was_none = True

        errorbardefaults = dict(color="#000000", label="Exp. Disp. Data",
                                capsize=2, linestyle="")

        if errorbarkwargs is None:
            errorbarkwargs = {}

        _errorbarkwargs = {**errorbardefaults, **errorbarkwargs}

        ax.errorbar(x=getattr(self, x), y=getattr(self, y),
                    yerr=getattr(self, yerr), **_errorbarkwargs)

        if x == "frequency":
            xlabeltext = "Frequency, "+r"$f$"+" "+r"$(Hz)$"
        elif x == "wavelength":
            xlabeltext = "Wavelength, "+r"$\lambda$"+" "+r"$(m)$"
        else:
            xlabeltext = ""

        if y == "velocity":
            ylabeltext = "Rayleigh Phase Velocity, "+r"$V_R$"+" "+r"$(m/s)$"
        elif y == "slowness":
            ylabeltext = "Slowness, "+r"$p$"+" "+r"$(s/m)$"
        else:
            ylabeltext = ""

        ax.set_xlabel(xlabeltext)
        ax.set_xscale("log")
        ax.set_ylabel(ylabeltext)

        if ax_was_none:
            return (fig, ax)
