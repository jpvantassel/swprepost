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

"""Tests for DispersionSet class."""

import os
import logging

from testtools import unittest, TestCase, get_full_path
import swprepost

logging.basicConfig(level=logging.CRITICAL)


class Test_DispersionSet(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ray = {0: swprepost.DispersionCurve([0.1, 0.2], [200, 100]),
                   1: swprepost.DispersionCurve([0.1, 0.2], [400, 200])}
        cls.lov = {0: swprepost.DispersionCurve([0.15, 0.2], [200, 150]),
                   1: swprepost.DispersionCurve([0.1, 0.22], [410, 200])}
        cls.identifier = 0
        cls.misfit = 0.
        cls.dc_set = swprepost.DispersionSet(cls.identifier, cls.misfit,
                                             rayleigh=cls.ray,
                                             love=cls.lov)

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_check_type(self):
        # curveset is not dict
        for curveset in ["curveset", False, ["this"]]:
            self.assertRaises(TypeError, swprepost.DispersionSet.check_type,
                              curveset=curveset,
                              valid_type=swprepost.DispersionCurve)

        # values are not of DispersionCurve
        for bad_dc in ["this", False, ["this"]]:
            curveset = {0: bad_dc}
            self.assertRaises(TypeError, swprepost.DispersionSet.check_type,
                              curveset=curveset,
                              valid_type=swprepost.DispersionCurve)

    def test_init(self):
        # Instantiate DispersionCurve objects.
        frequency = [1, 2, 3]
        velocity = [4, 5, 6]
        ray = swprepost.DispersionCurve(frequency=frequency, velocity=velocity)
        lov = swprepost.DispersionCurve(frequency=frequency, velocity=velocity)

        # Rayleigh Alone
        ex_a = swprepost.DispersionSet(identifier=1, misfit=1.2,
                                       rayleigh={0: ray}, love=None)
        self.assertListEqual(velocity, ex_a.rayleigh[0].velocity.tolist())
        self.assertEqual(1, ex_a.identifier)
        self.assertEqual(1.2, ex_a.misfit)

        # Love Alone
        ex_b = swprepost.DispersionSet(identifier=2, misfit=3.4,
                                       rayleigh=None, love={0: lov})
        self.assertListEqual(velocity, ex_b.love[0].velocity.tolist())

        # Rayleigh and Love
        ex_c = swprepost.DispersionSet(identifier=3, misfit=5.7,
                                       rayleigh={0: ray}, love={0: lov})
        self.assertListEqual(velocity, ex_c.rayleigh[0].velocity.tolist())
        self.assertListEqual(velocity, ex_c.love[0].velocity.tolist())

        # Rayleigh and Love are None
        self.assertRaises(ValueError, swprepost.DispersionSet,
                          identifier="Test")

    def test_from_geopsy(self):
        # Quick test -> Full test in DispersionSuite
        fname = self.full_path+"data/test_dc_mod2_ray2_lov2_shrt.txt"
        rayleigh = {0: swprepost.DispersionCurve([0.15, 64],
                                                 [1/0.000334532972901842,
                                                  1/0.00917746839997367]),
                    1: swprepost.DispersionCurve([0.479030947360446, 68],
                                                 [1/0.000323646256288129,
                                                  1/0.00832719612771301])}
        love = {0: swprepost.DispersionCurve([0.11, 61],
                                             [1/0.0003055565316784,
                                              1/0.00838314255586564]),
                1: swprepost.DispersionCurve([0.920128309893243, 69],
                                             [1/0.000305221889470528,
                                              1/0.00828240730448549])}
        expected_id = 149641
        expected_misfit = 1.08851

        # Both Rayleigh and Love
        returned = swprepost.DispersionSet.from_geopsy(fname=fname)
        self.assertEqual(expected_id, returned.identifier)
        self.assertEqual(expected_misfit, returned.misfit)
        for mode, expected in rayleigh.items():
            self.assertEqual(expected, returned.rayleigh[mode])
        for mode, expected in love.items():
            self.assertEqual(expected, returned.love[mode])

        # Only Rayleigh
        returned = swprepost.DispersionSet.from_geopsy(fname=fname)
        self.assertEqual(expected_id, returned.identifier)
        self.assertEqual(expected_misfit, returned.misfit)
        for mode, expected in rayleigh.items():
            self.assertEqual(expected, returned.rayleigh[mode])

        # Only Love
        returned = swprepost.DispersionSet.from_geopsy(fname=fname)
        self.assertEqual(expected_id, returned.identifier)
        self.assertEqual(expected_misfit, returned.misfit)
        for mode, expected in love.items():
            self.assertEqual(expected, returned.love[mode])

        # Neither
        self.assertRaises(ValueError, swprepost.DispersionSet.from_geopsy,
                          fname=fname, nrayleigh=0, nlove=0)

    def test_write_to_txt(self):
        fname = "dc_set_expected.dc"
        self.dc_set.write_to_txt(fname)
        expected = self.dc_set
        returned = swprepost.DispersionSet.from_geopsy(fname)
        self.assertEqual(expected, returned)
        os.remove(fname)

    def test_str_and_repr(self):
        a_set = {0: swprepost.DispersionCurve([0.1, 0.2], [200, 100]),
                 1: swprepost.DispersionCurve([0.1, 0.2], [400, 200])}
        dc_set = swprepost.DispersionSet(0, rayleigh=a_set, love=a_set)

        # __str__
        expected = "DispersionSet with 2 Rayleigh and 2 Love modes"
        returned = dc_set.__str__()
        self.assertEqual(expected, returned)

        # __repr__
        expected = f"DispersionSet(identifier={0}, rayleigh={a_set}, love={a_set}, misfit=0.0)"
        returned = dc_set.__repr__()
        self.assertEqual(expected, returned)

    def test_eq(self):
        dc = swprepost.DispersionCurve([1, 2], [3, 4])
        dc_set = swprepost.DispersionSet(0, rayleigh={0: dc})

        # Not Equal
        self.assertFalse(self.dc_set == dc_set)


if __name__ == "__main__":
    unittest.main()
