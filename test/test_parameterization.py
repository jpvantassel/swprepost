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

"""Tests for Parameterization class."""

import os
import logging

import swprepost
from testtools import unittest, TestCase, get_path

logging.basicConfig(level=logging.DEBUG)


class Test_Parameterization(TestCase):

    def setUp(self):
        self.path = get_path(__file__)

    def test_init(self):
        for lay_type in ["depth", "thickness"]:
            vp = swprepost.Parameter(lay_min=[1, 5], lay_max=[3, 16],
                                     par_min=[200, 400], par_max=[400, 600],
                                     par_rev=[True, False],
                                     lay_type=lay_type)
            pr = swprepost.Parameter(lay_min=[0], lay_max=[100],
                                     par_min=[0.2], par_max=[0.5],
                                     par_rev=[False],
                                     lay_type=lay_type)
            vs = swprepost.Parameter(lay_min=[1, 2], lay_max=[2, 3],
                                     par_min=[100, 200], par_max=[200, 300],
                                     par_rev=[True, False],
                                     lay_type=lay_type)
            rh = swprepost.Parameter(lay_min=[0], lay_max=[100],
                                     par_min=[2000], par_max=[2000],
                                     par_rev=[False],
                                     lay_type=lay_type)
            test = swprepost.Parameterization(vp, pr, vs, rh)
            self.assertTrue(test)

        # Attempt to init with bad parameters
        self.assertRaises(TypeError,
                          swprepost.Parameterization, "vp", "pr", "vs", "rh")

    def test_to_and_from_param(self):
        for version in swprepost.meta.SUPPORTED_GEOPSY_VERSIONS:
            vp = swprepost.Parameter.from_lr(1, 100, 4, 200, 400, True)
            pr = swprepost.Parameter.from_ln(1, 100, 3, 0.2, 0.5, False)
            vs = swprepost.Parameter.from_ftl(3, 3, 100, 200, True)
            rh = swprepost.Parameter.from_fx(2000)
            par = swprepost.Parameterization(vp, pr, vs, rh)
            fname_prefix = self.path / "data/par/test_to_and_from_param"
            try:
                par.to_param(fname_prefix=fname_prefix, version=version)
                new_par = swprepost.Parameterization.from_param(
                    fname_prefix=fname_prefix, version=version)
                self.assertEqual(par, new_par)
            finally:
                os.remove(f"{fname_prefix}.param")

    def test_eq(self):
        vp = swprepost.Parameter(lay_min=[1, 5], lay_max=[3, 16],
                                 par_min=[200, 400], par_max=[400, 600],
                                 par_rev=[True, False],
                                 lay_type="depth")
        pr = swprepost.Parameter(lay_min=[0], lay_max=[100],
                                 par_min=[0.2], par_max=[0.5],
                                 par_rev=[False],
                                 lay_type="depth")
        vs = swprepost.Parameter(lay_min=[1, 2], lay_max=[2, 3],
                                 par_min=[100, 200], par_max=[200, 300],
                                 par_rev=[True, False],
                                 lay_type="depth")
        rh = swprepost.Parameter(lay_min=[0], lay_max=[100],
                                 par_min=[2000], par_max=[2000],
                                 par_rev=[False],
                                 lay_type="depth")
        a = swprepost.Parameterization(vp, pr, vs, rh)

        vpb = swprepost.Parameter(lay_min=[1, 5], lay_max=[3, 16],
                                 par_min=[200, 400], par_max=[400, 600],
                                 par_rev=[True, False],
                                 lay_type="depth")
        vpb.lay_min = [1.5, 5]
        b = swprepost.Parameterization(vpb, pr, vs, rh)

        # TODO (jpv): Add a proper eq test.
        self.assertNotEqual(a, b)


if __name__ == '__main__':
    unittest.main()
