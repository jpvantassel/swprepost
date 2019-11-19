"""Tests for Curve object class."""

import unittest
import swipp

class Test(unittest.TestCase):
    def test_check_input(self):
        bad_frequency_types = ["1", True, (1, 2, 3)]
        bad_frequency_lengths = [[2, 3], [4, 5, 6, 7]]
        bad_frequency_values = [["1"], [True]]
        velocity = [100, 200, 300.5]

        bad_velocity_types = bad_frequency_types
        bad_velocity_lengths = [[1, 2, 3, 4], [5, 6]]
        bad_velocity_values = [["1"], [True]]
        frequency = [50, 25, 1.5]

        # Check types
        for bf, gv in zip(bad_frequency_types, velocity):
            self.assertRaises(
                TypeError, swipp.Curve.check_input, bf, gv)
        for gf, bv in zip(frequency, bad_velocity_types):
            self.assertRaises(
                TypeError, swipp.Curve.check_input, gf, bv)
        # Check lengths
        for bf in bad_frequency_lengths:
            gv = velocity
            self.assertRaises(
                IndexError, swipp.Curve.check_input, bf, gv)
        for bv in bad_velocity_lengths:
            gf = frequency
            self.assertRaises(
                IndexError, swipp.Curve.check_input, gf, bv)
        # Check values
        for bf, gv in zip(bad_frequency_values, velocity):
            self.assertRaises(
                TypeError, swipp.Curve.check_input, bf, gv)
        for gf, bv in zip(frequency, bad_velocity_values):
            self.assertRaises(
                TypeError, swipp.Curve.check_input, gf, bv)


if __name__ == "__main__":
    unittest.main()
