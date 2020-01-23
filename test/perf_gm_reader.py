"""This file contains a performance test for reading a file containing
a dispersion curve."""

import swipp
from testtools import get_full_path
import cProfile
import pstats

full_path = get_full_path(__file__)

def main():
    suite = swipp.GroundModelSuite.from_geopsy(full_path+"data/test_gm_mod100.txt")

fname = full_path+"data/.tmp_profiler_run"
data = cProfile.run('main()', filename=fname)
stat = pstats.Stats(fname)
stat.sort_stats('tottime')
stat.print_stats(0.1)

# YEAR - MO - DY : TIME UNIT
# -------------------------
# 2020 - 01 - 22 :  0.019s -> Basline
# 2020 - 01 - 23 :  0.016s -> Refactor for delegation

