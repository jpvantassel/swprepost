"""This file includes a class for handling targets for surface wave
inversion."""

import tarfile as tar
import os
import numpy as np
import scipy.interpolate as sp
import warnings
import logging
import re
from swipp import CurveUncertain
logging.Logger(name=__name__)


class Target(CurveUncertain):
    """Class for manipulating inversion target information.

    `Target` is a class for loading, manipulating, and writting
    target information in preparation for surface-wave inversion. The
    class contains a number of methods for instantiating a `Target`
    object.

    Attributes:
        frequency : ndarray
            Vector of frequency values in the experimental dispersion
            curve (one per point).
        velocity : ndarray
            Vector of velocity values in the experimental dispersion
            curve (one per point).
        velstd : ndarray
            Vector of standard deviation values in the experimental
            dispersion curve (one per point).
    """

    def __init__(self, frequency, velocity, velstd=0.05):
        """Instantiate a Target object.

        Create a Target object from `ndarrays` of `frequency`,
        `velocity`, and optionally velocity standard deviation
        (`velstd`).

        Args:
            frequency : ndarray
                frequency values (one per point) in the experimental
                dispersion curve.
            velocity : ndarray
                velocity values (one per point) in the experimental
                dispersion curve.
            velstd : None, float, ndarray, optional
                velocity standard deviation in the experimental
                dispersion curve.
                If `None`, no standard deviation is defined.
                If `float`, a constant coefficient of variation (COV) is
                applied, the default is 0.05.
                If `ndarray`, standard deviation is defined point by
                point.

        Returns:
            Instantiated `Target` object.

        Raises:
            TypeError:
                If `frequency`, `velocity`, and `velstd` are not
                convertable to ndarrays.
            ValueError:
                If `velstd` is provided in the form of COV and the value
                is less than zero.
        """
        # Convert velstd input to vector, if necessary.
        frequency = np.array(frequency)
        velocity = np.array(velocity)
        if velstd is None:
            velstd = np.zeros(frequency.shape)
        elif type(velstd) == float:
            velstd = velocity*velstd

        super().__init__(x=frequency, y=velocity, yerr=velstd, xerr=None)
        self._sort_data()
        self.dc_weight = 1

    def _sort_data(self):
        """Sort Target attributes from smallest to largest."""
        if (self._y.size != self._x.size) and (self._y.size != self._yerr.size):
            msg = "`frequency`, `velocity`, and `velstd` must have the same size."
            raise ValueError(msg)

        sort_ids = np.argsort(self._x)
        self._yerr = self._yerr[sort_ids]
        self._y = self._y[sort_ids]
        self._x = self._x[sort_ids]

    @property
    def frequency(self):
        """Get frequency."""
        return self._x

    @frequency.setter
    def frequency(self, value):
        """Set frequency."""
        self._x = value

    @property
    def velocity(self):
        """Get velocity"""
        return self._y

    @velocity.setter
    def velocity(self, value):
        """Set velocity."""
        self._y = value

    @property
    def wavelength(self):
        """Get wavelength."""
        return self.velocity/self.frequency

    @property
    def velstd(self):
        """Get velocity standard deviation."""
        return self._yerr

    @velstd.setter
    def velstd(self, value):
        """Set velocity standard deviation."""
        self._yerr = value

    @property
    def cov(self):
        """Returns the coefficent of variation (COV) of each data point."""
        return self.velstd/self.velocity

    @property
    def slowness(self):
        """Returns the mean slowness of each data point."""
        return 1/self.velocity

    @property
    def slostd(self):
        """Get slowness standard deviation."""
        upper = self.velocity+self.velstd
        lower = self.velocity-self.velstd
        return 0.5*((1/lower - self.slowness) + (self.slowness - 1/upper))

    @property
    def logstd(self):
        """Get logarithmic slowness standard deviation."""
        p = self.slowness
        pstd = self.slowness * self.cov
        # From DispersionProxy.cpp Line 194
        return 0.5*(((p+pstd)/p) + (p/(p-pstd)))

    @classmethod
    def from_csv(cls, fname, commentcharachter="#"):
        """Construct instance of Target class from csv file.

        Read a comma seperated values (csv) file with header line(s) to
        construct a target object.

        Args:
            filename : str
                Name or path to file containing surface-wave dispersion.
                The file should have at a minimum a column for frequency
                in Hz and velocity in m/s. Velocity standard devaiton in
                m/s may also be provided.
            commentcharachter : str, optional
                Charachter at the beginning of a line denoting a
                comment, default value is '#'.

        Returns:
            An initialized instance of the Target class.

        Raises:
            ValueError:
                If the format of the input file does not match that
                detailed above.
        """
        with open(fname, "r") as f:
            lines = f.read().splitlines()

        frequency, velocity, velstd = [], [], []
        for line in lines:
            # Skip commented lines
            if line[0] == commentcharachter:
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
        measured or provided. In general, a COV between 0.05 and 0.15
        should provide a reasonable estimate of the uncertainty.

        If velocity standard deviations have already been provided this
        method will overwrite them. If this is not desired refer to
        :meth: `setmincov`.

        Args:
            cov : float
                Coefficient of variation to be used to replace `velstd`.

        Returns:
            `None`, updates attribute `velstd`.

        Raises:
            ValueError:
                If `cov` < 0.
        """
        if cov < 0:
            raise ValueError("`cov` must be greater than zero.")
        self.velstd = self.velocity*cov

    def setmincov(self, cov):
        """Set minimum coefficient of variation (COV) for targets.

        If uncertainty in the experimental data has been provided, this
        method allows the setting of a minimum COV, where all data
        points with uncertainty below this threshold will be modified
        and those above this threshold will be left alone.

        If no measure of uncertainty has been provided, use :meth:
        `setcov`.

        Args:
            cov : float
                Minimum allowable COV.

        Returns:
            `None`, may update attribute `velstd`.

        Raises:
            ValueError:
                If `cov` < 0.
        """
        if cov < 0:
            raise ValueError("`cov` must be greater than zero.")

        current_cov = self.cov
        update_ids = np.where(current_cov < cov)
        self.velstd[update_ids] = self.velocity[update_ids]*cov

    def is_no_velstd(self):
        """Indicates `True` if every point has zero `velstd`."""
        return all(std == 0 for std in self.velstd)

    def pseudo_depth(self, depth_factor=2.5):
        """Estimates depth based on the experimental dispersion data.

        This method, along with :meth: `pseudo-vs`, may be useful to
        create plots of pseudo-Vs vs pseudo-depth for selecting
        approprate boundaries for parameter limits in the inverison
        stage.

        Args:
            depth_factor : float
                Factor by which the mean wavelegnth is divided to
                produce an estimate of depth. Typical between 2 and 3,
                default 2.5.

        Returns:
            `ndarray` of pseudo-depth.
        """
        if (depth_factor > 3) | (depth_factor < 2):
            msg = "`depth_factor` is outside the typical range. See documenation."
            warnings.warn(msg)
        return self.wavelength/depth_factor

    def pseudo_vs(self, velocity_factor=1.1):
        """Estimates depth based on the experimental dispersion data.

        This method, along with :meth: `pseudo-depth`, may be useful to
        create plots of pseudo-Vs vs pseudo-depth for selecting
        approprate boundaries for parameter limits in the inverison
        stage.

        Args:
            velocity_factor : float
                Factor by which the mean Rayleigh wave velocity is
                multiplied to produce an estimate of shear-wave
                velocity. Typically between 1 and 1.2, and is dependent
                upon the expected Poisson's ratio, default is 1.1.

        Returns:
            `ndarray` of pseudo-depth.
        """
        if (velocity_factor > 1.2) | (velocity_factor < 1):
            msg = "`velocity_factor` is outside the typical range. See documenation."
            warnings.warn(msg)
        return self.velocity*velocity_factor

    def cut(self, pmin, pmax, domain="frequency"):
        """Remove data outside of the specified range.

        Args:
            pmin, pmax : float
                New minimum and maximum parameter value in the specified
                domain, respectively.

            domain : {'frequency', 'wavelength'}, optional
                Domain along which to perform the cut.

        Returns:
            `None`, may update attributes `frequency`, `velocity`, and
            `velstd`.
        """
        if domain == "wavelength":
            x = self.wavelength
        elif domain == "frequency":
            x = self.frequency
        else:
            raise NotImplementedError(f"domain={domain}, not recognized.")

        keep_ids = np.where((x >= pmin) & (x <= pmax))
        self.frequency = self.frequency[keep_ids]
        self.velocity = self.velocity[keep_ids]
        self.velstd = self.velstd[keep_ids]

    def resample(self, pmin, pmax, pn, res_type="log", domain="wavelength", inplace=False):
        """Resample dispersion curve.

        Resample dispersion curve over a specific range, using log or
        linear sampling in the frequency or wavelength domain.

        Args:
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
                place or if a new Target object should be returned.

        Returns:
            If `inplace=True`:
                `None`, may update attributes `frequency`, `velocity`,
                and `velstd`.
            If `inplace=False`:
                A new instantiated `Target` object is returned.

        Raises:
            NotImplementedError:
                If `res_type` and/or `domain` are not amoung the options
                specified.
        """
        # Check input.
        if pmax < pmin:
            pmin, pmax = (pmax, pmin)
        if type(pn) != int:
            raise TypeError(f"`pn` must be an `int`, not {type(pn)}")
        if pn <= 0:
            raise ValueError(f"`pn` must be greater than zero.")

        # Set location of resampled values.
        if res_type == "log":
            xx = np.logspace(np.log10(pmin), np.log10(pmax), pn)
        elif res_type == "linear":
            xx = np.linspace(pmin, pmax, pn)
        else:
            msg = f"`res_type`={res_type}, has not been implemented."
            raise NotImplementedError(msg)

        # Define x
        if domain == "frequency":
            x = self.frequency
        elif domain == "wavelength":
            x = self.wavelength
        else:
            msg = f"`domain`={domain}, has not been implemented."
            raise NotImplementedError(msg)

        # Define custom resampling functions
        res_fxn = self.resample_function(x, self.velocity, kind="cubic")
        res_fxn_yerr = self.resample_function(x, self.velstd, kind="cubic")

        results = super().resample(xx=xx, inplace=False, res_fxn=res_fxn,
                                   res_fxn_yerr=res_fxn_yerr)
        xx, new_vel, new_velstd, = results

        if domain == "frequency":
            new_frq = xx
        else:
            new_frq = new_vel/xx

        # Update attributes or return new object.
        if inplace:
            self.frequency = new_frq
            self.velocity = new_vel
            self.velstd = new_velstd
        else:
            return Target(new_frq, new_vel, new_velstd)

    @property
    def vr40(self):
        """Estimate the Rayleigh wave velocity at a wavelength of 40m."""
        wavelength = self.wavelength
        if (max(wavelength) > 40) & (min(wavelength) < 40):
            obj = self.resample(pmin=40, pmax=40, pn=1, res_type="linear",
                                domain="wavelength", inplace=False)
            return float(obj.velocity)
        else:
            warnings.warn("A wavelength of 40m is out of range")
            return None

    def to_txt_dinver(self, fname, version="3"):
        """Write `Target` to text format readily accepted by dinver's
        pre-processor.

        Args:
            fname : str
                Name of output file, may a relative or full path.
            version : {'3', '2'}, optional
                Major version of Geopsy, default is version
                3.

        Returns:
            `None`, writes a file to disk.
        """
        if version=="2":
            stddevs = self.slostd
        elif version=="3":
            stddevs = self.logstd
        else:
            msg = f"version={version} is not implemented, refer to documentation."
            raise NotImplementedError(msg)

        with open(fname, "w") as f:
            for frq, slo, std in zip(self.frequency, self.slowness, stddevs):
                f.write(f"{frq}\t{slo}\t{std}\n")

    def to_txt_swipp(self, fname):
        """Write `Target` to text format readily accepted by swipp.

        Args:
            fname : str
                Name of output file, may a relative or full path.

        Returns:
            `None`, writes a file to disk.
        """
        with open(fname, "w") as f:
            f.write("#Frequency,Velocity,Velstd\n")
            for c_frq, c_vel, c_velstd in zip(self.frequency, self.velocity, self.velstd):
                f.write(f"{c_frq},{c_vel},{c_velstd}\n")

    def to_target(self, fname_prefix, version="3"):
        """Write `Target` to `.target` file format that can be imported
        into dinver.

        Args:
            fname_prefix : str
                Name of target file without the .target suffix, a
                relative or full path may be provided.
            version : {'3', '2'}, optional
                Major version of Geopsy, default is version
                3.
        Returns:
            `None`, writes target file to disk.

        Raises:
            NotImplementedError
                If `version` does not match the options provided.
        """

        self._sort_data()

        # TODO (jpv): Decide on how best to include ell.
        self.__ell_weight = 1
        self.__ell_def = False
        self.__ell_mean = 0
        self.__ell_std = 0

        # TODO (jpv): Recode this writter to use json or xml libarary.
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
                         f"        <name>SWIPP</name>",
                         f"        <log>SWIPP by Joseph P. Vantassel</log>",
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
                         f"        <name>SWIPP</name>",
                         f"        <log>SWIPP written by J. Vantassel</log>",
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
        else:
            raise NotImplementedError

        contents += ["      </ModalCurve>"]

        if version in ["2"]:
            contents += ["    </ModalCurveTarget>"]

        elif version in ["3"]:
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
        else:
            raise NotImplementedError

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
    def from_target(cls, target_prefix, version="3"):
        """Create Target object from target file.

        Args:
            target_prefix : str
                Name of target file to be opened without the '.target'
                suffix, may include the relative or full path.
            version : {'2', '3'}, optional
                Major version of Geopsy used to write the target file,
                default is '3'.

        Returns:
            Instantiated `Target` object.
        """
        with tar.open(target_prefix+".target", "r:gz") as a:
            a.extractall()

        try:
            with open("contents.xml", "r", encoding="utf-8") as f:
                lines = f.read()
            if "<Dinver>" not in lines[:10]:
                raise RuntimeError
        except (UnicodeDecodeError, RuntimeError) as e:
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
        if self.frequency.size == obj.frequency.size:
            for attr in ["frequency", "velocity", "velstd"]:
                for f1, f2 in zip(np.round(getattr(self, attr), 6), np.round(getattr(obj, attr), 6)):
                    if f1 != f2:
                        return False
        else:
            return False
        return True

    def __repr__(self):
        frq_str = str(np.round(self.frequency,2))
        vel_str = str(np.round(self.velocity,2))
        std_str = str(np.round(self.velstd,2))
        return f"Target(frequency={frq_str}, velocity={vel_str}, velstd={std_str})"