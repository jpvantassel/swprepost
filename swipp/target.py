"""
This file includes a class for handling targets for surface wave
inversion. In particluar the surface-wave dispersion curves and
the ellipticity peak.
"""

import tarfile as tar
import os
import numpy as np
import scipy.interpolate as sp


class Target:
    """Class containing various functions for manipulating target
    information.

    Target class is to be used for loading, manipuatling, and writting
    target information. In particular, target class in the form of
    surface wave dispersion can be loaded form a csv file, manipulated
    using various methods provided, and written to a .target format
    accepted by the Dinver module of the open-source software Geopsy.
    This class also allows for an ellipticity peak with uncertainty to
    supplement the experimental disperison data previously mentioned.

    Attributes:
      This class contains no public attributes.
    """

    def __init__(self, filename, headerlines=1):
        """Construct instance of Target class from csv file.

        Read a comma seperated file (csv) with header line(s) to
        construct a target object.

        Args:
          filename: Name or path to file containig surface-wave
            disperion. The file should have columns for frequency in
            hertz and velocity in m/s. Velocity standard devaiton in m/s
            may also be provided. Each value should be listed in the
            order presented previously. For example a valid input file
            may be:

                frequency (Hz), velocity (m/s), velstd (m/s)
                10, 100, 5
                5, 120, 6
                1, 150, 7

          headerlines: Number of lines that should be ignored at the
            The head of the provided csv file. By default = 1.

        Returns:
            An initialized instance of the Target class.

        Raises:
            ValueError: If the format of the provided input file does not
                match the required format detailed above.
        """
        with open(filename, "r") as f:
            rows = f.read().splitlines(False)
        freq = []
        vel = []
        velstd = []
        for row in rows[headerlines:]:
            # If three entries -> vel_std is provided extract all three
            if row.count(",") == 2:
                a, b, c = row.split(",")
            # If two entries provided -> assume freq and vel, vel_std=0
            elif row.count(",") == 1:
                a, b = row.split(",")
                c = 0
            else:
                raise ValueError("Format of input file not recognized.")
            freq += [float(a)]
            vel += [float(b)]
            velstd += [float(c)]

        self.__frequency = []
        self.__velocity = []
        self.__velstd = []
        self.__wavelength = []
        for f, v, std in sorted(zip(freq, vel, velstd), key=lambda x: x[0]):
            self.__frequency += [f]
            self.__velocity += [v]
            self.__velstd += [std]
            self.__wavelength += [v/f]
        self.__dc_weight = 1
        self.__pseu_d1 = None
        self.__pseu_v1 = None
        self.__ell_def = False
        self.__ell_mean = 0
        self.__ell_std = 0
        self.__ell_weight = 1

    @classmethod
    def from_file(cls, fname, headerlines=1):
        # TODO (jpv): Move constructor to from_file and clean up constructor.
        pass

    def setcov(self, cov):
        """Set coefficient of variation (COV) to a constant value for
        targets.

        This method may be used if no velocity standard deviation was
        measured or provided. A COV between 0.05 and 0.15 should provide
        reasonable estimates of the uncertainty in most test cases.

        If velocity standard deviations have already been provided this
        method will overwrite them. If this is not desired see the
        setmincov method.

        Args:
          cov: Coefficient of variation to apply to the experimental
            data.

        Returns:
          This method returns no value.

        Raises:
          This method raises no errors.
        """
        rid = 0
        for vel in self.__velocity:
            self.__velstd[rid] = vel*cov
            rid += 1

    def setmincov(self, cov):
        """Set minimum coefficient of variation (COV) for targets.

        If uncertainty in the experimental data has been provided, this
        method allows the setting of a minimum COV, where all data
        points with uncertainty below this threshold will be modified
        and those above this threshold will be left alone.

        If no measure of uncertainty has been provided, use the setcov
        method.

        Args:
          cov: Minimum threshold cov for which all covs currently below
            which will be updated to.

        Returns:
          This methods returns no value.

        Raises:
          This method raises no exceptions.
        """
        rid = 0
        for vel in self.__velocity:
            if self.__velstd[rid] < vel*cov:
                self.__velstd[rid] = vel*cov
            rid += 1

    @property
    def freq(self):
        """Returns the frequency of each data point as a list."""
        return self.__frequency

    @property
    def vel(self):
        """Returns the velocity of each data point as a list."""
        return self.__velocity

    @property
    def velstd(self):
        """Returns the velocity standard deviation of each data point as
         a list."""
        return self.__velstd

    @property
    def wavelength(self):
        """Returns the wavelength of each data point as a list."""
        return self.__wavelength

    def is_no_velstd(self):
        """Returns a boolean, indicating whether every data point has a
        non-zero velocity standard deviation."""
        return any(std == 0 for std in self.__velstd)

    def pseudo(self, depth_factor=2.5, velocity_factor=1.1):
        """Returns an estimate of shear wave velocity (Vs) and depth
        based on the provided experimental dispersion data.

        The estimate of Vs (i.e., pseudo-Vs) and depth (i.e.,
        pseudo-depth) are based on the experimental data and the two
        method arguements.The plot of pseudo-Vs vs pseudo-depth is
        beneficial for selecting approprate boundaries for parameter
        limits in the inverison stage.

        Args:
            depth_factor: Factor by which the wavelegnth is divided to
                produce an estimate of depth. Typical between 2 and 3.

            velocity_factor: Factor by which the rayleigh wave velocity
                is multiplied to produce an estimate of the shear-wave
                velocity. Typically between 1 and 1.2, depends on
                expected Poisson"s ratio.

        Returns:
            This methods returns the tuple (pseudo-velocity,
                pseudo-depth) where both quantities are lists of their
                values, one per data point.

        Raises:
            This method raises no exceptions.
        """
        tmp_v1 = []
        tmp_d1 = []
        for wave, vel in zip(self.__wavelength, self.__velocity):
            tmp_d1.append(wave/depth_factor)
            tmp_v1.append(vel*velocity_factor)
        return (tmp_v1, tmp_d1)

    def cut(self, cut_range, domain="frequency"):
        """Remove data points outside of the specified frequency or
        wavelength range.

        Args:
            cut_range: Tuple of the form (min, max) where min and max
                are the desired minimum and maximum value.

            domain: String to denote the desired domain, either
                frequency or wavelength.

        Returns:
            Returns None, instead updates the objects state.

        Raises:
            This method raises no exceptions.
        """
        min_cut = min(cut_range)
        max_cut = max(cut_range)

        frq = np.array(self.__frequency)
        wav = np.array(self.__wavelength)

        if domain == "wavelength":
            ids = np.where((wav >= min_cut) & (wav <= max_cut))
        else:
            ids = np.where((frq >= min_cut) & (frq <= max_cut))

        self.__frequency = frq[ids].tolist()
        self.__velocity = np.array(self.__velocity)[ids].tolist()
        self.__velstd = np.array(self.__velstd)[ids].tolist()
        self.__wavelength = wav[ids].tolist()

    def resample(self, res_range, res_type="log", res_by="wavelength", inplace=False):
        """Resample dispersion curve over a specific range using various
        methods.

        Resample dispersion curve over a specified range (res_range) and
        using various methods includeing log or linear sampling in the 
        frequency or wavelength space.

        Args:
            res_range: Tuple which specify mininum value, maximum value,
                and number of samples. (min, max, nsamples).

            res_type: String specifying either logarithmic ("log") or 
                linear ("linear") sampling.

            res_by: String specifying sampling in either the wavelength
                ("wavelength") or frequency ("frequency") domain.

            inplace: Boolean indicating whether or not the resampling 
                should be done in place or if a copy should be returned.
                    If True: edits internal variable.

                    If False: leaves the internal variables unchanged 
                        and returns a tuple, see Returns for details.

        Returns:
            If inplace=True, no value is returned.

            If inplace=False, a tuple of the form (frequency, velocity,
                vel_std, wavelength) where each parameter is a list.

        Raises:
            TypeError: If res_range is not of the format specified
                above.

            NotImplementedError: If res_type and/or res_by is not 
                amoung those options mentioned previously.
        """
        if type(res_range) not in (tuple, list):
            raise TypeError("range must be a list or tuple of length 3.")
        if len(res_range) != 3:
            raise TypeError("range must be a list or tuple of length 3.")
        if res_range[1] < res_range[0]:
            res_range = (res_range[1], res_range[0], res_range[2])
        if type(res_range[2]) not in (int,):
            raise TypeError("nsamples must be postive integer")
        if res_range[2] <= 0:
            raise TypeError("nsamples must be postive integer")
        types = {"log": "log", "linear": "linear"}
        options = {"wavelength": "wavelength", "frequency": "frequency"}

        if types[res_type] == types["log"]:
            xx = np.logspace(np.log10(res_range[0]),
                             np.log10(res_range[1]),
                             res_range[2])
        elif types[res_type] == types["linear"]:
            xx = np.linspace(res_range[0], res_range[1], res_range[2])
        else:
            raise NotImplementedError(
                "This type of resampling has not been implemented.")

        if options[res_by] == options["frequency"]:
            x = np.array(self.__frequency)
        elif options[res_by] == options["wavelength"]:
            x = np.array(self.__wavelength)
        else:
            raise NotImplementedError(
                "Resampling by {} has not been implemented."
                .format(res_by))

        y = np.array(self.__velocity)
        z = np.array(self.__velstd)/y   # COV
        interp_vel = sp.interp1d(x, y, kind="cubic")
        interp_cov = sp.interp1d(x, z, kind="cubic")

        vel_np = interp_vel(xx)
        velstd_np = interp_vel(xx)*interp_cov(xx)

        if options[res_by] == options["frequency"]:
            freq_np = xx
            wave_np = vel_np/xx
        elif options[res_by] == options["wavelength"]:
            wave_np = xx
            freq_np = vel_np/xx
        else:
            raise NotImplementedError(
                "Resampling by {} has not been implemented."
                .format(res_by))

        if inplace:
            self.__velocity = vel_np.tolist()
            self.__frequency = freq_np.tolist()
            self.__wavelength = wave_np.tolist()
            self.__velstd = velstd_np.tolist()
        else:
            return (freq_np.tolist(), vel_np.tolist(),
                    velstd_np.tolist(), wave_np.tolist())

    def vr40(self):
        """ Return the rayleigh wave velocity at a wavelength of 40m.

        Returns a tuple of the information for a rayleigh wave at a 
        wavelength of 40m, dispersion data encompasses a 40m wavelength
        otherwise, returns none.

        Args:
            This method requires no arguments.

        Returns:
            This method returns a tuple of the form (frequency, 
            wavelength, velstd, wavelength) at a wavelength of 40m.

        Raises:
            This method raises no exceptions.
        """
        if (max(self.__wavelength) > 40) & (min(self.__wavelength) < 40):
            freq, vel, velstd, wave = self.resample((39, 41, 3),
                                                    res_type="linear",
                                                    res_by="wavelength",
                                                    inplace=False)
            return (freq[1], vel[1], velstd[1], wave[1])
        else:
            print("Minimum wavelength is larger than 40m and/or maximum")
            print("wavelength is less than 40m. Will not extrapolate.")
            return None

    def write_to_txt(self, fname):
        """Write target to .txt file so that it can be loaded into
        DINVER for further editing if necessary.

        Args:
            fname: Name of output text file without the .txt extensions.
                A relative path or full path may also be provided.

        Returns:
            This method returns no value. But instead writes a file to 
            disk.

        Raises:
            This method raises no exceptions.
        """
        if fname.endswith(".txt"):
            fname = fname[-4:]
        with open(fname+".txt", "w") as f:
            for frq, vel, std in zip(self.freq, self.vel, self.velstd):
                cov = std/vel
                slo = 1/vel
                f.write(f"{frq}\t{slo}\t{slo*cov}\n")

    def write_to_file(self, fname="Tar1"):
        """Write target information to .target file that can be read by
        Dinver.

        Args:
            fname: Name of target file without the .target suffix. If
                desired a relative path or full path may also be
                provided.

        Returns:
            This method returns no value. But instead writes a file to 
            disk.

        Raises:
            This method raises no exceptions.
        """
        slow, slowstd = [], []
        for vel, velstd in zip(self.__velocity, self.__velstd):
            slow.append(1/vel)
            slowstd.append(slow[-1]*velstd/vel)

        contents = ["<Dinver>",
                    "  <pluginTag>DispersionCurve</pluginTag>",
                    "  <pluginTitle>Surface Wave Inversion</pluginTitle>"]

        contents += ["  <TargetList>",
                     "    <ModalCurveTarget type=\"dispersion\">",
                     "      <selected>true</selected>",
                     "      <misfitWeight>" +
                     str(self.__dc_weight)+"</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_Normalized</misfitType>",
                     "      <ModalCurve>",
                     "        <name>UTinvert</name>",
                     "        <log>UTinvert written by J. Vantassel</log>",
                     "        <Mode>",
                     "          <slowness>Phase</slowness>",
                     "          <polarisation>Rayleigh</polarisation>",
                     "          <ringIndex>0</ringIndex>",
                     "          <index>0</index>",
                     "        </Mode>"]

        for freq, mean, stdev in zip(self.__frequency, slow, slowstd):
            contents += ["        <StatPoint>",
                         "          <x>"+str(freq)+"</x>",
                         "          <mean>"+str(mean)+"</mean>",
                         "          <stddev>"+str(stdev)+"</stddev>",
                         "          <weight>1</weight>",
                         "          <valid>true</valid>",
                         "        </StatPoint>"]

        contents += ["      </ModalCurve>",
                     "    </ModalCurveTarget>",
                     "    <AutocorrTarget>",
                     "      <selected>false</selected>",
                     "      <misfitWeight>1</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_NormalizedBySigmaOnly</misfitType>",
                     "      <AutocorrCurves>",
                     "      </AutocorrCurves>",
                     "    </AutocorrTarget>",
                     "    <ModalCurveTarget type=\"ellipticity\">",
                     "      <selected>false</selected>",
                     "      <misfitWeight>1</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_LogNormalized</misfitType>",
                     "    </ModalCurveTarget>"]

        selected = "true" if self.__ell_def else "false"
        contents += ["    <ValueTarget type=\"ellipticity peak\">",
                     "      <selected>"+selected+"</selected>",
                     "      <misfitWeight>" +
                     str(self.__ell_weight)+"</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_Normalized</misfitType>",
                     "      <StatValue>",
                     "        <mean>"+str(self.__ell_mean)+"</mean>",
                     "        <stddev>"+str(self.__ell_std)+"</stddev>",
                     "        <weight>1</weight>",
                     "        <valid>"+selected+"</valid>",
                     "      </StatValue>",
                     "    </ValueTarget>"]

        contents += ["    <RefractionTarget type=\"Vp\">",
                     "      <selected>false</selected>",
                     "      <misfitWeight>1</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_Normalized</misfitType>",
                     "    </RefractionTarget>",
                     "    <RefractionTarget type=\"Vs\">",
                     "      <selected>false</selected>",
                     "      <misfitWeight>1</misfitWeight>",
                     "      <minimumMisfit>0</minimumMisfit>",
                     "      <misfitType>L2_Normalized</misfitType>",
                     "    </RefractionTarget>",
                     "  </TargetList>",
                     "</Dinver>"]

        with open("contents.xml", "w") as f:
            for row in contents:
                f.write(row+"\n")
        with tar.open(fname+".target", "w:gz") as f:
            f.add("contents.xml")
        os.remove("contents.xml")
