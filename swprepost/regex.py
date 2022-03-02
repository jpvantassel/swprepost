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

"""Regular expressions for text parsing."""

import re

NUMBER = r"\d+\.?\d*[eE]?[+-]?\d*"
NEWLINE = r"\W+"

# DC
pair = f"{NUMBER} {NUMBER}\n"
model_txt = r"# Layered model (\d+): value=(\d+\.?\d*)"
wave_txt = r"# \d+ (Rayleigh|Love) dispersion mode\(s\)"
mode_txt = r"# Mode \d+\n"
dcset_txt = f"{model_txt}\n{wave_txt}\n.*\n((?:{mode_txt}(?:{pair})+)+)"

model = re.compile(model_txt)
mode = re.compile(mode_txt)
dcset = re.compile(dcset_txt)
dc_data = re.compile(f"({NUMBER}) ({NUMBER})")

# GroundModel
# -----------
# Identify the text associated with a single layer of a `GroundModel`.
gm_layer = f"{NUMBER} {NUMBER} {NUMBER} {NUMBER}"
gm_layer_exec = re.compile(f"({NUMBER}) ({NUMBER}) ({NUMBER}) ({NUMBER})")

# Identify the text associated with a single `GroundModel`.
gm_meta = r"# Layered model (\d+): value=(\d+\.?\d*)"
gm_expr = f"{gm_meta}\n\d+\n((?:{gm_layer}\n)+)"
gm_exec = re.compile(gm_expr)

# TargetSet
# ---------
# Identify the text associated with a single `ModalCurve`.
modalcurve_expr = r"<ModalCurve>(.*?)</ModalCurve>"
modalcurve_exec = re.compile(modalcurve_expr, re.DOTALL)

# ModalTarget
# -----------
# Given the text associated with a single `ModalCurve` ->
# Find the associated polarization (str).
# Geopsy v2.10.1 uses polarisation, but v3.4.2 uses polarization.
polarization_expr = r"<polari[sz]ation>(Rayleigh|Love)</polari[sz]ation>"
polarization_exec = re.compile(polarization_expr)

# Find the associated Mode (number).
modenumber_expr = r"<index>(\d+)</index>"
modenumber_exec = re.compile(modenumber_expr)

# Find the associated StatPoints (tuple).
statpoint_expr = f"<x>({NUMBER})</x>{NEWLINE}<mean>({NUMBER})</mean>{NEWLINE}<stddev>({NUMBER})</stddev>"
statpoint_exec = re.compile(statpoint_expr)

# Given the text from a swprepost .csv ->
# Find the associated header information.
description_expr = "^#(rayleigh|love) (\d+)"
description_exec = re.compile(description_expr)

# Find the associated data
# the first two values (frequency and velocity) are required.
# the third value (velocity standard deviation) is optional.
# TODO(jpv): Deprecate after v2.0.0; remove optionals; require all values.
mtargetpoint_expr = f"({NUMBER}),({NUMBER}),?({NUMBER})?(.*)?{NEWLINE}"
mtargetpoint_exec = re.compile(mtargetpoint_expr)
