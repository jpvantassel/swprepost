"""Tests for `DispersionSet` class."""

from testtools import unittest, TestCase, get_full_path
import swipp
import logging
logging.basicConfig(level=logging.DEBUG)


class Test_DispersionSet(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_check_type(self):
        # curveset is not dict
        for curveset in ["curveset", False, ["this"]]:
            self.assertRaises(TypeError, swipp.DispersionSet.check_type,
                              curveset=curveset,
                              valid_type=swipp.DispersionCurve)

        # values are not of DispersionCurve
        for bad_dc in ["this", False, ["this"]]:
            curveset = {0: bad_dc}
            self.assertRaises(TypeError, swipp.DispersionSet.check_type,
                              curveset=curveset,
                              valid_type=swipp.DispersionCurve)

    def test_init(self):
        # Instantiate DispersionCurve objects.
        frequency = [1, 2, 3]
        velocity = [4, 5, 6]
        ray = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        lov = swipp.DispersionCurve(frequency=frequency, velocity=velocity)

        # Rayleigh Alone
        ex_a = swipp.DispersionSet(identifier="Test", misfit=None,
                                   rayleigh={0: ray}, love=None)
        self.assertListEqual(velocity, ex_a.rayleigh[0].velocity.tolist())
        self.assertEqual("Test", ex_a.identifier)
        self.assertEqual(None, ex_a.misfit)

        # Love Alone
        ex_b = swipp.DispersionSet(identifier="Test", misfit=None,
                                   rayleigh=None, love={0: lov})
        self.assertListEqual(velocity, ex_b.love[0].velocity.tolist())

        # Rayleigh and Love
        ex_c = swipp.DispersionSet(identifier="Test", misfit=None,
                                   rayleigh={0: ray}, love={0: lov})
        self.assertListEqual(velocity, ex_c.rayleigh[0].velocity.tolist())
        self.assertListEqual(velocity, ex_c.love[0].velocity.tolist())

        # Rayleigh and Love are None
        self.assertRaises(ValueError, swipp.DispersionSet, identifier="Test")

    def test_from_geopsy(self):
        # Quick test -> Full test in DispersionSuite
        fname = self.full_path+"data/test_dc_mod2_ray2_lov2_shrt.txt"
        rayleigh = {0: swipp.DispersionCurve([0.15, 64],
                                             [1/0.000334532972901842,
                                              1/0.00917746839997367]),
                    1: swipp.DispersionCurve([0.479030947360446, 68],
                                             [1/0.000323646256288129,
                                              1/0.00832719612771301])}
        love = {0: swipp.DispersionCurve([0.11, 61],
                                         [1/0.0003055565316784,
                                          1/0.00838314255586564]),
                1: swipp.DispersionCurve([0.920128309893243, 69],
                                         [1/0.000305221889470528,
                                          1/0.00828240730448549])}
        expected_id = "149641"
        expected_misfit = 1.08851

        # Both Rayleigh and Love
        returned = swipp.DispersionSet.from_geopsy(fname=fname)
        self.assertEqual(expected_id, returned.identifier)
        self.assertEqual(expected_misfit, returned.misfit)
        for mode, expected in rayleigh.items():
            self.assertEqual(expected, returned.rayleigh[mode])
        for mode, expected in love.items():
            self.assertEqual(expected, returned.love[mode])

        # Only Rayleigh
        returned = swipp.DispersionSet.from_geopsy(fname=fname)
        self.assertEqual(expected_id, returned.identifier)
        self.assertEqual(expected_misfit, returned.misfit)
        for mode, expected in rayleigh.items():
            self.assertEqual(expected, returned.rayleigh[mode])

        # Only Love
        returned = swipp.DispersionSet.from_geopsy(fname=fname)
        self.assertEqual(expected_id, returned.identifier)
        self.assertEqual(expected_misfit, returned.misfit)
        for mode, expected in love.items():
            self.assertEqual(expected, returned.love[mode])

        # Neither
        self.assertRaises(ValueError, swipp.DispersionSet.from_geopsy,
                          fname=fname, nrayleigh=0, nlove=0)


if __name__ == "__main__":
    unittest.main()
