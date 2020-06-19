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

"""Performance test for reading a file containing dispersion curves."""

import swprepost
from testtools import get_full_path
import cProfile
import pstats

full_path = get_full_path(__file__)

def main():
    fname = full_path+"data/test_dc_mod100_ray2_lov2_full.txt"
    swprepost.DispersionSuite.from_geopsy(fname=fname, nsets="all")

fname = full_path+"data/.tmp_profiler_run"
data = cProfile.run('main()', filename=fname)
stat = pstats.Stats(fname)
stat.sort_stats('tottime')
stat.print_stats(0.1)

# YEAR - MO - DY : TIME UNIT
# -------------------------
# 2020 - 01 - 22 :  0.141s -> Baseline
# 2020 - 01 - 23 :  0.250s -> Refactor with delegation
# 2020 - 01 - 23 :  0.137s -> Compile regular expressions
# 2020 - 01 - 23 :  0.128s -> Factor out compilation
# 2020 - 01 - 24 :  0.086s -> Remove line-by-line
# 2020 - 04 - 06 :  0.065s -> After major refactor
