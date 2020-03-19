# This file is part of swipp, a Python package for surface-wave
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

"""Tests for DispersionCurve class."""

from testtools import unittest, TestCase, get_full_path
import swipp
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)


class Test_DispersionCurve(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_init(self):
        # list
        frequency = [1, 2, 3, 4.5, 6.7]
        velocity = [4, 5, 6., 8.5, 2.2]
        dc = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        self.assertArrayEqual(np.array(frequency), dc.frequency)
        self.assertArrayEqual(np.array(velocity), dc.velocity)

        # ndarray
        frequency = np.array([1, 2, 3, 4.5, 6.7])
        velocity = np.array([4, 5, 6., 8.5, 2.2])
        dc = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        self.assertArrayEqual(frequency, dc.frequency)
        self.assertArrayEqual(velocity, dc.velocity)

    def test_properties(self):
        frequency = np.array([1, 1.5, 2, 2.5, 3.5, 5])
        velocity = np.array([100, 200, 400, 100, 500, 1000])
        dc = swipp.DispersionCurve(frequency=frequency,
                                   velocity=velocity)

        expecteds = [frequency, velocity, velocity/frequency, 1/velocity]
        returneds = [dc.frequency, dc.velocity, dc.wavelength, dc.slowness]

        for expected, returned in zip(expecteds, returneds):
            self.assertArrayEqual(expected, returned)

    def test_from_geopsy(self):
        # Quick test -> Full test in DispersionSuite
        fname = self.full_path + "data/test_dc_mod2_ray2_lov0_shrt.txt"
        dc = swipp.DispersionCurve.from_geopsy(fname)
        expected_frequency = np.array([0.15, 64])
        expected_slowness = np.array([0.000334532972901842,
                                      0.00917746839997367])
        self.assertArrayEqual(expected_frequency, dc.frequency)
        self.assertArrayEqual(expected_slowness, dc.slowness)

    def test_equal(self):
        dc_a = swipp.DispersionCurve([1, 2, 3], [4, 5, 6])
        dc_b = swipp.DispersionCurve([1, 2, 3], [4, 5, 6])
        dc_c = swipp.DispersionCurve([4, 5, 6], [4, 5, 6])
        dc_d = swipp.DispersionCurve([1, 2, 3], [1, 2, 3])
        dc_e = swipp.DispersionCurve([1, 2], [1, 2])

        self.assertTrue(dc_a == dc_b)
        self.assertTrue(dc_a != dc_c)
        self.assertTrue(dc_a != dc_d)
        self.assertTrue(dc_c != dc_d)
        self.assertTrue(dc_e != dc_a)


if __name__ == "__main__":
    unittest.main()
