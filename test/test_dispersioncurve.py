"""Tests for DispersionCurve class."""

import unittest
import swipp
import logging
logging.basicConfig(level=logging.DEBUG)


class TestDispersionCurve(unittest.TestCase):
    def test_init(self):
        frequency = [1, 2, 3, 4.5, 6.7]
        velocity = [4, 5, 6., 8.5, 2.2]
        test = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        self.assertListEqual(frequency, test.frq)
        self.assertListEqual(velocity, test.vel)

    def test_wav(self):
        frequency = [1, 1, 2, 2, 5, 5]
        velocity = [100, 200, 400, 100, 500, 1000]
        wavelength = [100, 200, 200, 50, 100, 200]
        mydc = swipp.DispersionCurve(frequency=frequency,
                                     velocity=velocity)
        self.assertListEqual(mydc.wav, wavelength)


if __name__ == "__main__":
    unittest.main()
