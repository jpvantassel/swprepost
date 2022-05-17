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

"""Utilities for test-specific input checking."""

import warnings

from .meta import SUPPORTED_GEOPSY_VERSIONS


def check_geopsy_version(version):
    """Check if Geopsy version is supported by `swprepost`.

    Parameters
    ----------
    version : str
        Full version of Geopsy of the form `Major.Minor.Micro`.

    Returns
    -------
    str
        Version specified if valid, raise `NotImplementedError` otherwise.

    """
    # TODO (jpv): Remove in swprocess version >2.0.0.
    # Provides backwards compatability to v1.0.0 and earlier.
    if version == "2" or version == "3":
        version_map = {"2": "2.10.1", "3": "3.4.2"}
        version = version_map[version]
        msg = "Proving only Geopsy's major version is no longer permitted, "
        msg += f"setting version to {version}."
        warnings.warn(msg, DeprecationWarning)

    if version in SUPPORTED_GEOPSY_VERSIONS:
        return version
    else:
        msg = f"The version {version} is not supported, "
        msg += f"use one of the following {SUPPORTED_GEOPSY_VERSIONS}."
        raise NotImplementedError(msg)
