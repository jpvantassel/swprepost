"""This file contains a performance test for reading a file containing
dispersion curves."""

import swipp
from testtools import get_full_path
import cProfile
import pstats

full_path = get_full_path(__file__)

def main():
    fname = full_path+"data/test_dc_mod100_ray2_lov2_full.txt"
    suite = swipp.DispersionSuite.from_geopsy(fname=fname, ndc="all")

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
