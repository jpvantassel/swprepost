
"""Tests for abstract class CurveSet."""

from testtools import unittest, TestCase
import swipp


class Test_CurveSet(TestCase):
    def test_check_input(self):
        # All sets are None
        bad_disp_set = {0: None}
        self.assertRaises(TypeError, swipp.CurveSet, [bad_disp_set],
                          swipp.DispersionCurve)

        # Inputs values are wrong type
        bad_disp_set = {0: {"frq": [1, 2, 3], "vel": [4, 5, 6]}}
        self.assertRaises(TypeError, swipp.CurveSet, [bad_disp_set])
        self.assertRaises(TypeError, swipp.CurveSet, [bad_disp_set, bad_disp_set])


if __name__ == "__main__":
    unittest.main()
