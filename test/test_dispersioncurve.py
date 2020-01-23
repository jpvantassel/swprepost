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
        frequency = np.array([1, 2, 3, 4.5, 6.7])
        velocity = np.array([4, 5, 6., 8.5, 2.2])
        dc = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        self.assertArrayEqual(frequency, dc.frequency)
        self.assertArrayEqual(velocity, dc.velocity)

    def test_wavelength(self):
        frequency = np.array([1, 1, 2, 2, 5, 5])
        velocity = np.array([100, 200, 400, 100, 500, 1000])
        wavelength = velocity/frequency
        dc = swipp.DispersionCurve(frequency=frequency,
                                     velocity=velocity)
        self.assertArrayEqual(wavelength, dc.wavelength)

    def test_from_geopsy(self):
        # Quick test -> Full test in DispersionSuite
        fname = self.full_path + "data/test_dc_mod2_ray2_lov0_shrt.txt"
        dc = swipp.DispersionCurve.from_geopsy(fname)
        expected_frequency = np.array([0.15, 64])
        expected_slowness = np.array([0.000334532972901842, 0.00917746839997367])
        self.assertArrayEqual(expected_frequency, dc.frequency)
        self.assertArrayEqual(expected_slowness, dc.slowness)

if __name__ == "__main__":
    unittest.main()
