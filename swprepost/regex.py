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

"""Regular expressions for text parsing."""

import re

number = r"\d+.?\d*[eE]?[+-]?\d*"

# DC
pair = f"{number} {number}\n"
model_txt = r"# Layered model (\d+): value=(\d+.?\d*)"
wave_txt = r"# \d+ (Rayleigh|Love) dispersion mode\(s\)"
mode_txt = r"# Mode \d+\n"
dcset_txt = f"{model_txt}\n{wave_txt}\n.*\n((?:{mode_txt}(?:{pair})+)+)"

model = re.compile(model_txt)
mode = re.compile(mode_txt)
dcset = re.compile(dcset_txt)
dc_data = re.compile(f"({number}) ({number})")

# GM
quad = f"{number} {number} {number} {number}\n"
gm_txt = f"{model_txt}\n\d+\n((?:{quad})+)"

gm = re.compile(gm_txt)
gm_data = re.compile(f"({number}) ({number}) ({number}) ({number})")
