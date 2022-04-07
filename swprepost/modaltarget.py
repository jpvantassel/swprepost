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

"""Definition of ModalTarget class."""

import warnings

import matplotlib.pyplot as plt
import numpy as np

from swprepost import Curve
from swprepost import CurveUncertain
from swprepost.check_utils import check_geopsy_version
from .regex import polarization_exec, modenumber_exec, statpoint_exec, description_exec, mtargetpoint_exec
from .meta import __version__


class ModalTarget(CurveUncertain):
    """Target information for a surface wave mode.

    `ModalTarget` is a class for loading, manipulating, and writting
    surface wave target information for a single mode in preparation
    for surface wave inversion.

    """

    def __init__(self, frequency, velocity, velstd, description=(("rayleigh", 0),)):
        """Initialize a `ModalTarget` object.

        Parameters
        ----------
        frequency, velocity, velstd : array-like
            Arrays of frequency, velocity, and velocity standard
            deviation values to fully describe a mode of
            experimental dispersion data (one per point).
        description : tuple of tuples
            Each `ModalTarget` may describe one or more wavetypes and/or
            one or more modes. Each potential description of the
            ModalTarget is listed as tuple of the form
            `(wavetype, modenumber)` where `wavetype` is either
            "rayleigh" or "love" and `modenumber` is a non-negative
            integer. A mode number of zero refers to the fundamental
            mode. The potential descriptions of a mode are grouped into
            a tuple containing all possible descriptions. The default
            description is that of the fundamental Rayleigh mode
            expressed as `(("rayleigh", 0),)`.

        Returns
        -------
        ModalTarget
            Instantiated `ModalTarget` object.

        Raises
        ------
        TypeError
            If `frequency`, `velocity`, and `velstd` are not
            `array-like`.
        ValueError
            If `velstd` is `float` and the value is less than zero.

        """
        # TODO(jpv): To remove in version >2.0.0.
        if isinstance(velstd, float):
            msg = "Setting velstd as a float is deprecated and will be removed after v2.0.0"
            warnings.warn(msg, category=DeprecationWarning)
            velstd = np.array(velocity, dtype=np.double)*velstd

        super().__init__(x=frequency, y=velocity, yerr=velstd, xerr=None)

        self._sort_data()
        self.dc_weight = 1

        self.description = self._check_description(description)

    # TODO(jpv): Replace with Typing.
    @staticmethod
    def _check_description(description):
        """Check description complies with expected format."""
        polarizations = ["rayleigh", "love"]
        for _description in description:
            try:
                polarization, modenumber = _description
            # If tuple instead of tuple of tuples _description cannot be split
            # and will return ValueError.
            except ValueError:
                raise TypeError(
                    "description must be a iterable of tuples, not tuple.")

            if polarization not in polarizations:
                raise ValueError(
                    f"polarization={polarization} is not recognized, must be in {polarizations}.")
            if not isinstance(modenumber, (int,)):
                raise TypeError(
                    f"modenumber must be non-negative integer, not type {type(modenumber)}.")
            if modenumber < 0:
                raise ValueError(
                    f"modenumber={modenumber} is negative, must be non-negative integer.")
        return description

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
    def from_wavelength(cls, wavelength, velocity, velstd, description=(("rayleigh", 0,),)):
        """Create from data processed in terms of wavelength.

        Parameters
        ----------
        frequency, velocity, velstd : array-like
            Arrays of frequency, velocity, and velocity standard
            deviation values to fully describe a mode of
            experimental dispersion data (one per point).
        description : tuple of tuples
            Each `ModalTarget` may describe one or more wavetypes and/or
            one or more modes. Each potential description of the
            ModalTarget is listed as tuple of the form
            `(wavetype, modenumber)` where `wavetype` is either
            "rayleigh" or "love" and `modenumber` is a non-negative
            integer. A mode number of zero refers to the fundamental
            mode. The potential descriptions of a mode are grouped into
            a tuple containing all possible descriptions. The default
            description is that of the fundamental Rayleigh mode
            expressed as `(("rayleigh", 0),)`.

        Returns
        -------
        ModalTarget
            Instantiated `ModalTarget` object.

        """
        # Sterilize inputs.
        wavelength = np.array(wavelength)
        velocity = np.array(velocity)
        if velstd is None:
            velstd = np.zeros_like(velocity)
        elif isinstance(velstd, float):
            velstd = velocity*velstd
        else:
            velstd = np.array(velstd)

        frequency = velocity/wavelength
        upper = Curve(x=(velocity+velstd)/wavelength, y=velocity+velstd)
        lower = Curve(x=(velocity-velstd)/wavelength, y=velocity-velstd)

        # Average velstd
        a = upper.resample(xx=frequency, interp1d_kwargs=dict(
            fill_value="extrapolate"))[1]
        b = lower.resample(xx=frequency, interp1d_kwargs=dict(
            fill_value="extrapolate"))[1]
        velstd = (abs(a - velocity) + abs(b - velocity))/2
        return cls(frequency, velocity, velstd=velstd, description=description)

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
        update_ids = np.argwhere(self.cov < cov)
        self.velstd[update_ids] = self.velocity[update_ids]*cov
        self._isyerr = True

    def pseudo_depth(self, depth_factor=2.5):
        """Estimate depth based on the experimental dispersion data.

        This method, along with :meth: `pseudo-vs`, may be useful to
        create plots of pseudo-Vs vs pseudo-depth for selecting
        appropriate boundaries for parameter limits in the inversion
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
        appropriate boundaries for parameter limits.

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
            msg = "`velocity_factor` is outside the typical range. See documentation."
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
            return ModalTarget(new_frq, new_vel, new_velstd, description=self.description)

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

    def to_txt_dinver(self, fname, version="3.4.2"):
        """Write in text format accepted by `Dinver`.

        Parameters
        ----------
        fname : str
            Name of output file, may a relative or full path.
        version : {'3.4.2', '2.10.1'}, optional
            Version of Geopsy, default is version '3.4.2'.

        Returns
        -------
        None
            Write's geopsy-styled text file to disk.

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
            stddevs = self.slostd
        elif version == "3.4.2":
            stddevs = self.logstd
        else:  # pragma: no cover
            msg = "You updated the SUPPORTED_GEOPSY_VERSIONS, but need to update to_txt_dinver."
            raise NotImplementedError(msg)

        with open(fname, "w") as f:
            for frq, slo, std in zip(self.frequency, self.slowness, stddevs):
                f.write(f"{frq}\t{slo}\t{std}\n")

    @classmethod
    def from_txt_dinver(cls, fname, version="3.4.2"):
        """Create from text format accepted by `Dinver`.

        Parameters
        ----------
        fname : str
            Name of output file, may a relative or full path.
        version : {'3.4.2', '2.10.1'}, optional
            Version of Geopsy, default is version '3.4.2'.

        Returns
        -------
        ModalTarget
            Instantiated `ModalTarget` with information from file.

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

        with open(fname, "r") as f:
            lines = f.readlines()

        frqs, slos, stds = [], [], []
        for line in lines:
            if line.startswith("#"):
                continue

            frq, slo, std = line.split()[:3]
            frqs.append(frq)
            slos.append(slo)
            stds.append(std)

        frq = np.array(frqs, dtype=np.double)
        slo = np.array(slos, dtype=np.double)
        vel = 1/slo
        std = np.array(stds, dtype=np.double)

        if version == "2.10.1":
            velstd = (-1 + np.sqrt(1 + 4*std*std*vel*vel))/(2*std)
        elif version == "3.4.2":
            cov = std - np.sqrt(std*std - 2*std + 2)
            velstd = cov*vel
        else:  # pragma: no cover
            msg = "You updated the SUPPORTED_GEOPSY_VERSIONS, but need to update from_txt_dinver."
            raise NotImplementedError(msg)

        return cls(frq, vel, velstd)

    def to_csv(self, fname):
        """Write `ModalTarget` to csv.

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
            f.write(f"#swprepost v{__version__},,\n")
            f.write(f"#{len(self.description)} potential descriptions:,,\n")
            for (polarization, modenumber) in self.description:
                f.write(f"#{polarization} {modenumber},,\n")
            f.write(
                "#Frequency (Hz),Velocity (m/s),Velocity Standard Deviation (m/s)\n")
            for c_frq, c_vel, c_velstd in zip(self.frequency, self.velocity, self.velstd):
                f.write(f"{c_frq},{c_vel},{c_velstd}\n")

    @classmethod
    def from_csv(cls, fname, description=(("rayleigh", 0),)):
        """Read `ModalTarget` from csv.

        Read a comma seperated values (csv) file with header line(s) to
        construct a `ModalTarget`.

        Parameters
        ----------
        fname : str
            Relative or the full path to a file containing surface wave
            dispersion data. The field should have three columns:
            frequency in Hz, velocity in m/s, and velocity standard
            deviation in m/s.
        description : tuple of tuples
            Each `ModalTarget` may describe one or more wavetypes and/or
            one or more modes. Each potential description of the
            ModalTarget is listed as tuple of the form
            `(wavetype, modenumber)` where `wavetype` is either
            "rayleigh" or "love" and `modenumber` is a non-negative
            integer. A mode number of zero refers to the fundamental
            mode. The potential descriptions of a mode are grouped into
            a tuple containing all possible descriptions. The default
            description is that of the fundamental Rayleigh mode
            expressed as `(("rayleigh", 0),)`.

        Returns
        -------
        ModalTarget
            Initialized `ModalTarget` object.

        Raises
        ------
        ValueError
            If the format of the input file does not match that
            detailed above.

        """
        with open(fname, "r") as f:
            text = f.read()

        # Read header information
        descriptions = description_exec.findall(text)

        # TODO(jpv): Deprecate after v>2.0.0.
        if len(descriptions) == 0:
            msg = ".csv does not contain any metadata, this the default "
            msg += "in v2.0.0 and before, however with v2.0.0 metadata "
            msg += "is required. The provided description will be used. "
            msg += "Replacement with the provided description will be "
            msg += "deprecated after v2.0.0."
            warnings.warn(msg, DeprecationWarning)
        else:
            description = []
            for (polarization, modenumber) in descriptions:
                description.append((polarization, int(modenumber)))
            description = tuple(description)

        # Read data
        mtargetpoints = mtargetpoint_exec.findall(text)

        frequency, velocity, velstd = [], [], []
        for (frq, vel, std, additional) in mtargetpoints:

            # If a user provides more than three columns of data, this is a
            # problem. To handle this rigorously, capture the additional text
            # and raise an error to avoid any ambiguity.
            if additional != "":
                additional = True
                break

            frequency.append(float(frq))
            velocity.append(float(vel))
            # If std is not provided, regex will return '' and float('') will
            # return a ValueError, which is then caught and handled.
            # TODO(jpv): Consider for later deprecation.
            try:
                std = float(std)
            except ValueError:
                # msg = ".csv only contains two columns of information instead "
                # msg += "of three the ability to provide only two columns will "
                # msg += "be deprecated after v1.X.X."
                # warnings.warn(msg, DeprecationWarning)
                std = 0
            finally:
                velstd.append(std)

        if len(frequency) == 0 or additional:
            msg = f"Format of file {fname} not recognized. See documentation."
            raise ValueError(msg)

        return cls(frequency, velocity, velstd, description)

    def to_target(self, fname_prefix, version="3.4.2"):
        """Write info to the .target file format used by `Dinver`.

        Parameters
        ----------
        fname_prefix : str
            Name of target file without the .target suffix, a
            relative or full path may be provided.
        version : {'3.4.2', '2.10.1'}, optional
            Version of Geopsy, default is version '3.4.2'.

        Returns
        -------
        None
            Writes file to disk.

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
        from swprepost import TargetSet
        TargetSet([self]).to_target(fname_prefix=fname_prefix, version=version)

    @classmethod
    def from_target(cls, fname_prefix, version="3.4.2"):
        """Create from target file.

        Note that this method is still largely experimental and may
        not work for all cases.

        Parameters
        ----------
        fname_prefix : str
            Name of target file to be opened excluding the `.target`
            suffix, may include the relative or full path.
        version : {'2.10.1', '3.10.2'}, optional
            Major version of Geopsy that was used to write the target
            file, default is '3.4.2'.

        Returns
        -------
        ModalTarget
            Instantiated `ModalTarget` object.

        """
        from swprepost import TargetSet
        targetset = TargetSet.from_target(
            fname_prefix=fname_prefix, version=version)
        ntargets = len(targetset.targets)

        if ntargets > 1:
            msg = f"{fname_prefix}.target contains {ntargets} ModalTargets, only returning the first."
            warnings.warn(msg, category=RuntimeWarning)

        return targetset.targets[0]

    @staticmethod
    def _parse_modeltarget_from_text(mc_text, version):
        """Parse information from ModalCurveTarget text.

        Paramters
        ---------
        mc_text : str
            Text for ModalCurveTarget that spans from
            <ModalCurveTarget> to </ModalCurveTarget> in .target xml.
        version : {'2.10.1', '3.4.2'}
            Version of Geopsy that was used to write the target file.

        Returns
        -------
        Tuple
            Of the form `(frequency, velocity, velstd, description)`
            which can be used to create a `ModalTarget`.

        """
        version = check_geopsy_version(version)

        # Polarization -> return {rayleigh, love}
        polarizations = polarization_exec.findall(mc_text)

        # Mode -> return int
        modenumbers = modenumber_exec.findall(mc_text)

        # StatPoints {ndarray}
        statpoints = statpoint_exec.findall(mc_text)
        xs = np.empty(len(statpoints))
        means = np.empty(len(statpoints))
        stddevs = np.empty(len(statpoints))
        for cid, statpoint in enumerate(statpoints):
            _x, _mean, _stddev = statpoint
            xs[cid] = float(_x)
            means[cid] = float(_mean)
            stddevs[cid] = float(_stddev)

        frequency = xs
        velocity = 1/means
        if version == "2.10.1":
            inv_stddevs = 1/stddevs
            velstd = 0.5*(np.sqrt(inv_stddevs*inv_stddevs +
                                  4*velocity*velocity) - inv_stddevs)
        elif version == "3.4.2":
            cov = stddevs - np.sqrt(stddevs*stddevs - 2*stddevs + 2)
            velstd = cov*velocity
        else:
            pass

        description = []
        for polarization, modenumber in zip(polarizations, modenumbers):
            description.append((polarization.lower(), int(modenumber)))

        return (frequency, velocity, velstd, description)

    def __eq__(self, obj):
        """Check if two `ModalTarget`s are equal."""
        if not isinstance(obj, ModalTarget):
            return False

        if len(self.description) != len(obj.description):
            return False

        for pot_self_dsc, pot_obj_dsc in zip(self.description, obj.description):
            for _self_dsc, _obj_dsc in zip(pot_self_dsc, pot_obj_dsc):
                if _self_dsc != _obj_dsc:
                    return False

        for attr in ["frequency", "velocity", "velstd"]:
            if len(getattr(self, attr)) != len(getattr(obj, attr)):
                return False

            if not np.allclose(getattr(self, attr), getattr(obj, attr)):
                return False

        return True

    def __repr__(self):
        """Unambiguous representation of a `ModalTarget`."""
        frq_str = str(np.round(self.frequency, 2))
        vel_str = str(np.round(self.velocity, 2))
        std_str = str(np.round(self.velstd, 2))
        return f"ModalTarget(frequency={frq_str}, velocity={vel_str}, velstd={std_str}, description={self.description})"

    def __str__(self):
        """Human readable representation of a `ModalTarget`."""
        return f"ModalTarget with {len(self.frequency)} frequency points."

    def plot(self, x="frequency", y="velocity", yerr="velstd", ax=None,
             figkwargs=None, errorbarkwargs=None):  # pragma: no cover
        """Plot `ModalTarget` information.

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
            Additional keyword arguments defining the styling of the
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
            if figkwargs is None:
                figkwargs = {}
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
            xlabeltext = r"Frequency (Hz)"
        elif x == "wavelength":
            xlabeltext = r"Wavelength (m)"
        else:
            xlabeltext = ""

        if y == "velocity":
            ylabeltext = r"Phase Velocity (m/s)"
        elif y == "slowness":
            ylabeltext = r"Slowness (s/m)"
        else:
            ylabeltext = ""

        ax.set_xlabel(xlabeltext)
        ax.set_xscale("log")
        ax.set_ylabel(ylabeltext)

        if ax_was_none:
            return (fig, ax)


# TODO(jpv): remove in version after 2.0.0, here for backwards comptability.
Target = ModalTarget
