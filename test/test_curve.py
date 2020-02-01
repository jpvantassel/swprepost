"""Tests for Curve class."""

from testtools import unittest, TestCase
import numpy as np
import swipp


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
        self.assertRaises(TypeError, swipp.Curve.check_input, bad_types, good,
                          fxn)
        self.assertRaises(TypeError, swipp.Curve.check_input, good, bad_types,
                          fxn)

        # Check values
        for bad in bad_lengths:
            self.assertRaises(IndexError, swipp.Curve.check_input, bad, good,
                              fxn)
            self.assertRaises(IndexError, swipp.Curve.check_input, good, bad,
                              fxn)

        # Check values
        self.assertRaises(ValueError, swipp.Curve.check_input, bad_values,
                          good, fxn)
        self.assertRaises(ValueError, swipp.Curve.check_input, good,
                          bad_values, fxn)


if __name__ == "__main__":
    unittest.main()
