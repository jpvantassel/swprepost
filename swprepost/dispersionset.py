# This file is part of swprepost, a Python package for surface wave
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

"""DispersionSet class definition."""

import numpy as np

from swprepost import DispersionCurve, regex

__all__ = ["DispersionSet"]


class DispersionSet():
    """Class for handling sets of
    :meth: `DispersionCurve <swprepost.DispersionCurve>` objects, which all
    belong to a common ground model.

    Attributes
    ----------
    rayleigh, love : dict
        Container for `DispersionCurve` objects, of the form:
        `{0:DispersionCurve0, ... N:DispersionCurveN}`
        where each key is the mode number and the value is the
        corresponding instantiated `DispersionCurve` object.
    identifier : int
        Model identifier of the `DispersionSet`.
    misfit : float
        Value of dispersion misfit if provided, `None` otherwise.

    """

    @classmethod
    def check_type(cls, curveset, valid_type):
        """Check that the `curveset` are are valid.

        Specifically:
        1. Assume `curveset` is instance of `dict`.
        2. If it is a `dict`, check all values are instances of the
        `valid_type` and return zero, otherwise raise `TypeError`.
        3. If it is not check if `None`, if so return one.
        4. Otherwise, raise `TypeError`.

        """
        try:
            for key, value in curveset.items():
                if not isinstance(value, valid_type):
                    msg = f"{key} must be a {valid_type}, not {type(value)}."
                    raise TypeError(msg)
        except AttributeError:
            if curveset is None:
                return 1
            else:
                msg = f"CurveSet must be a `dict` or `None`, not {type(curveset)}."
                raise TypeError(msg)
        return 0

    def __init__(self, identifier=0, misfit=0.0, rayleigh=None, love=None):
        """Create a `DispersionCurveSet` object.

        Parameters
        ----------
        identifier : str
            Unique identifier of the `DispersionSet`.
        misfit : float, optional
            `DispersionSet` misfit, default is 0.0.
        rayleigh, love : dict
            Container for `DispersionCurve` objects of the form
            `{0:disp_curve_obj0, ... N:disp_curve_objN}` where each
            key is the mode number and the value is the
            corresponding `DispersionCurve` object.

        Returns
        -------
        DispersionSet
            Instantiated `DispersionSet` object.

        """
        none_count = 0
        none_count += self.check_type(rayleigh, self._dc())
        none_count += self.check_type(love, self._dc())

        if none_count == 2:
            msg = "`rayleigh` and `love` cannot both be `None`."
            raise ValueError(msg)

        self.rayleigh = None if rayleigh is None else dict(rayleigh)
        self.love = None if love is None else dict(love)

        self.identifier = int(identifier)
        self.misfit = float(misfit)

    @classmethod
    def _parse_dcs(cls, dcs_data, nmodes="all"):
        """Parse a group of modes into a `dict` of `DispersionCurves`"""
        modes = regex.dc_mode_start_exec.split(dcs_data)

        if nmodes == "all":
            modes = modes[1:]
        elif nmodes == 0:
            return None
        else:
            modes = modes[1:nmodes+1]

        dcs = {}
        for mode, dc_data in zip(regex.dc_mode_exec.finditer(dcs_data), modes):
            mode_number = int(mode.groups()[0])
            dcs.update({mode_number: cls._dc()._parse_dc(dc_data)})
        return dcs

    @classmethod
    def _from_full_file(cls, text, nrayleigh="all", nlove="all"):
        """Parse the first `DispersionSet` from Geopsy-style contents.

        Parameters
        ----------
        text : str
            Contents of Geopsy-style text file.
        nrayleigh, nlove : {"all", int}, optional
            Number of Rayleigh and Love modes to extract into a
            `DispersionSet` object, default is "all" meaning all
            available modes will be extracted.

        Returns
        -------
        DispersionSet
            Instantiated `DispersionSet` object.

        """
        if nrayleigh == 0 and nlove == 0:
            raise ValueError(f"`nrayleigh` and `nlove` cannot both be 0.")

        rayleigh, love = None, None
        previous_id, previous_misfit = "start", "0"
        for model_info in regex.dc_set_exec.finditer(text):
            id_a, msft_a, wav_a, wav_b, id_b, msft_b, wav_c, id_c, msft_c,  data = model_info.groups()

            for _id, _msft, _wav in zip([id_a, id_b, id_c], [msft_a, msft_b, msft_c], [wav_a, wav_b, wav_c]):
                if _id is not None:
                    identifier = _id
                    misfit = _msft
                    wave_type = _wav
                    break

            if identifier == previous_id or previous_id == "start":
                if wave_type == "Rayleigh":
                    rayleigh = cls._parse_dcs(data, nmodes=nrayleigh)
                elif wave_type == "Love":
                    love = cls._parse_dcs(data, nmodes=nlove)
                else: # pragma: no cover
                    raise NotImplementedError
                previous_id = identifier
                previous_misfit = misfit
            else:
                break

        return cls(previous_id, float(previous_misfit),
                   rayleigh=rayleigh, love=love)

    @classmethod
    def _dc(cls):
        """Define `DispersionCurve` to allow subclassing."""
        return DispersionCurve

    @classmethod
    def from_geopsy(cls, fname, nrayleigh="all", nlove="all"):
        """Create from a text file following the Geopsy format.

        Parameters
        ----------
        fname : str
            Name of file to be read, may be a relative or full path.
        nrayleigh, nlove : {"all", int}, optional
            Number of Rayleigh and Love modes to extract into a
            `DispersionSet` object, default is "all" meaning all
            available modes will be extracted.

        Returns
        -------
        DispersionSet
            Instantiated `DispersionSet` object.

        """
        with open(fname, "r") as f:
            text = f.read()
        return cls._from_full_file(text, nrayleigh=nrayleigh, nlove=nlove)

    def write_set(self, fileobj, nrayleigh="all", nlove="all"):
        """Write `DispersionSet` to current file.

        Parameters
        ----------
        fname : str
            Name of file, may be a relative or the full path.

        Returns
        -------
        None
            Writes file to disk.

        """
        nrayleigh = np.inf if nrayleigh == "all" else int(nrayleigh)
        nlove = np.inf if nlove == "all" else int(nlove)

        misfit = 0.0 if self.misfit is None else self.misfit
        if (self.rayleigh is not None) and (nrayleigh > 0):
            fileobj.write(
                f"# Layered model {self.identifier}: value={misfit}\n")
            nmodes = min(len(self.rayleigh), nrayleigh)
            # TODO (jpv): Not true is mode is missing.
            fileobj.write(f"# {nmodes} Rayleigh dispersion mode(s)\n")
            fileobj.write("# CPU Time = 0 ms\n")
            for key, value in self.rayleigh.items():
                if key >= nrayleigh:
                    continue
                fileobj.write(f"# Mode {key}\n")
                value.write_curve(fileobj)
        if (self.love is not None) and (nlove > 0):
            fileobj.write(
                f"# Layered model {self.identifier}: value={misfit}\n")
            nmodes = min(len(self.love), nlove)
            # TODO (jpv): Not true is mode is missing.
            fileobj.write(f"# {nmodes} Love dispersion mode(s)\n")
            fileobj.write("# CPU Time = 0 ms\n")
            for key, value in self.love.items():
                if key >= nlove:
                    continue
                fileobj.write(f"# Mode {key}\n")
                value.write_curve(fileobj)

    def write_to_txt(self, fname):
        """Write `DispersionSet` to Geopsy formated file.

        Parameters
        ----------
        fname : str
            Name of file, may be a relative or the full path.

        Returns
        -------
        None
            Writes text representation to disk.

        """
        with open(fname, "w") as f:
            f.write("# File written by swprepost\n")
            self.write_set(f)

    def __eq__(self, other):
        """Define when two `DispersionSet` objects are equal."""
        for attr in ["misfit", "identifier", "love", "rayleigh"]:
            my_attr = getattr(self, attr)
            ur_attr = getattr(other, attr)
            if my_attr != ur_attr:
                return False
        return True

    def __repr__(self):
        """Unambiguous representation of a `DispersionSet` object."""
        return f"DispersionSet(identifier={self.identifier}, rayleigh={self.rayleigh}, love={self.love}, misfit={self.misfit})"

    def __str__(self):
        """Human-readable representation of `DispersionSet` object."""
        return f"DispersionSet with {len(self.rayleigh)} Rayleigh and {len(self.love)} Love modes"
