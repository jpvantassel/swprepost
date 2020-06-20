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

"""Tests for Curve class."""

import numpy as np

from testtools import unittest, TestCase
import swprepost


class Test_Curve(TestCase):
    def test_check_input(self):
        bad_types = ["a", "b", "c"]
        bad_lengths = [[2, 3], [4, 5, 6, 7]]
        bad_values = [-1, 0, 0]
        good = [1, 2, 3]

        def fxn(x, y):
            options = (int, float)
            if isinstance(x, options) or isinstance(y, (options)):
                if x < 0 or y < 0:
                    raise ValueError
            else:
                raise TypeError

        # Check types
        self.assertRaises(TypeError, swprepost.Curve.check_input, bad_types,
                          good, fxn)
        self.assertRaises(TypeError, swprepost.Curve.check_input, good,
                          bad_types, fxn)

        # Check values
        for bad in bad_lengths:
            self.assertRaises(IndexError, swprepost.Curve.check_input, bad,
                              good, fxn)
            self.assertRaises(IndexError, swprepost.Curve.check_input, good,
                              bad, fxn)

        # Check values
        self.assertRaises(ValueError, swprepost.Curve.check_input, bad_values,
                          good, fxn)
        self.assertRaises(ValueError, swprepost.Curve.check_input, good,
                          bad_values, fxn)

    def test_resample(self):
        x = [1, 2, 4, 5]
        y = [0, 1, 3, 4]
        curve = swprepost.Curve(x, y)

        xx = [1, 2, 3, 4, 5]
        expected = np.array([0, 1, 2, 3, 4])

        # Inplace = False
        xx, returned = curve.resample(xx, inplace=False)
        self.assertArrayEqual(expected, returned)

        # Inplace = True
        curve.resample(xx, inplace=True)
        returned = curve._y
        self.assertArrayEqual(expected, returned)

    def test_eq(self):
        curve_a = swprepost.Curve(x=[1, 2, 3], y=[4, 5, 6])
        curve_b = "I am not a Curve object"
        curve_c = swprepost.Curve(x=[2, 4, 4], y=[4, 5, 6])
        curve_d = swprepost.Curve(x=[1, 2, 3, 4], y=[1, 2, 3, 7])
        curve_e = swprepost.Curve(x=[1, 2, 3], y=[4, 5, 6])

        self.assertTrue(curve_a != curve_b)
        self.assertTrue(curve_a != curve_c)
        self.assertTrue(curve_a != curve_b)
        self.assertTrue(curve_a != curve_d)
        self.assertTrue(curve_a == curve_e)

    def test_str_and_repr(self):
        x = [4, 5, 6]
        y = [7, 8, 9]
        curve = swprepost.Curve(x, y)

        # __repr__
        expected = f"Curve(x={curve._x}, y={curve._y})"
        returned = curve.__repr__()
        self.assertEqual(expected, returned)

        # __str__
        expected = f"Curve with 3 points."
        returned = curve.__str__()
        self.assertEqual(expected, returned)


if __name__ == "__main__":
    unittest.main()
