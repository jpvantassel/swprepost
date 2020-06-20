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

"""Tests for CurveUncertain class."""

import logging

import numpy as np

from testtools import unittest, TestCase
import swprepost

logging.basicConfig(level=logging.CRITICAL)


class Test_CurveUncertain(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.x = np.array([1, 2, 3, 5, 6, 7])
        cls.y = np.array([1, 2, 3, 5, 6, 7])
        cls.xerr = np.array([1, 1, 1, 1, 1, 1])
        cls.yerr = np.array([2, 4, 6, 10, 12, 14])

        # Define both error terms
        cls.ucurve_b = swprepost.CurveUncertain(x=cls.x, y=cls.y,
                                                yerr=cls.yerr, xerr=cls.xerr)

        # Define only yerr
        cls.ucurve_y = swprepost.CurveUncertain(x=cls.x, y=cls.y,
                                                yerr=cls.yerr)

        # Define only xerr
        cls.ucurve_x = swprepost.CurveUncertain(x=cls.x, y=cls.y,
                                                xerr=cls.xerr)

        # Define neither
        cls.ucurve_n = swprepost.CurveUncertain(x=cls.x, y=cls.y)

    def test_init(self):
        ucurve = self.ucurve_b

        for ex_attr, re_attr in zip(["x", "y", "xerr", "yerr"], ["_x", "_y", "_xerr", "_yerr"]):
            expected = getattr(self, ex_attr)
            returned = getattr(ucurve, re_attr)
            self.assertArrayEqual(expected, returned)

        ucurve = self.ucurve_y
        for eattr, rattr in zip(["x", "y", "yerr"], ["_x", "_y", "_yerr"]):
            expected = getattr(self, eattr)
            returned = getattr(ucurve, rattr)
            self.assertArrayEqual(expected, returned)

        # Define neither
        ucurve = self.ucurve_n
        for eattr, rattr in zip(["x", "y"], ["_x", "_y"]):
            expected = getattr(self, eattr)
            returned = getattr(ucurve, rattr)
            self.assertArrayEqual(expected, returned)

        # Inconsistent sizes
        yerr = [1, 2, 3]
        self.assertRaises(IndexError, swprepost.CurveUncertain,
                          self.x, self.y, yerr)

    def test_resample(self):
        # Inplace = False
        _xx = np.array([1, 2, 3, 4, 5, 6, 7])

        # Both
        xx, yy, yyerr, xxerr = self.ucurve_b.resample(_xx)
        self.assertArrayAlmostEqual(_xx, xx)
        self.assertArrayAlmostEqual(_xx, yy)
        self.assertArrayAlmostEqual(np.ones(7), xxerr)
        self.assertArrayAlmostEqual(np.array([2,4,6,8,10,12,14]), yyerr)

        # Neither
        xx, yy = self.ucurve_n.resample(_xx)
        self.assertArrayAlmostEqual(_xx, xx)
        self.assertArrayAlmostEqual(_xx, yy)

        # Inplace = True

        # Both
        xy = [1,2,3,5,6,7]
        _xx = [1,2,3,4,5,6,7]
        ucurve = swprepost.CurveUncertain(xy, xy, yerr=xy, xerr=xy)
        ucurve.resample(_xx, inplace=True)

        expected = np.array(_xx)
        for attr in ["_x", "_y", "_yerr", "_xerr"]:
            returned = getattr(ucurve, attr)
            self.assertArrayAlmostEqual(expected, returned)

        # x only
        ucurve = swprepost.CurveUncertain(xy, xy, xerr=xy)
        ucurve.resample(_xx, inplace=True)

        expected = np.array(_xx)
        for attr in ["_x", "_xerr"]:
            returned = getattr(ucurve, attr)
            self.assertArrayAlmostEqual(expected, returned)


if __name__ == "__main__":
    unittest.main()
