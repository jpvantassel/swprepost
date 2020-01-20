"""This file contains tests for the `Target` class."""

from testtools import unittest, TestCase, get_full_path
import swipp
import numpy as np
import os


class Test_Target(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)
        
    def test_init(self):
        # With standard deviation provided.
        frequency = np.array([1, 2, 3])
        velocity = np.array([100, 50, 25])
        velstd = np.array([5, 2.5, 1.25])
        tar = swipp.Target(frequency, velocity, velstd)
        self.assertArrayEqual(tar.frequency, frequency)
        self.assertArrayEqual(tar.velocity, velocity)
        self.assertArrayEqual(tar.velstd, velstd)

        # Without standard deviation.
        frequency = np.array([1, 2, 3])
        velocity = np.array([100, 50, 25])
        velstd = None
        tar = swipp.Target(frequency, velocity, velstd)
        self.assertArrayEqual(tar.frequency, frequency)
        self.assertArrayEqual(tar.velocity, velocity)
        self.assertArrayEqual(tar.velstd, np.zeros(velocity.shape))

        # With COV.
        frequency = np.array([1, 2, 3])
        velocity = np.array([100, 50, 25])
        velstd = 0.01
        tar = swipp.Target(frequency, velocity, velstd)
        self.assertArrayEqual(tar.frequency, frequency)
        self.assertArrayEqual(tar.velocity, velocity)
        self.assertArrayEqual(tar.velstd, velocity*velstd)

        # With list.
        a = [1, 2, 3]
        tar = swipp.Target(a, a, a)
        self.assertListEqual(tar.frequency.tolist(), a)

        # With unequal lists.
        a = [1, 2, 3]
        b = [1, 2]
        self.assertRaises(IndexError, swipp.Target, a, b, a)

    def test_from_csv(self):
        # With standard deviation provided.
        tar = swipp.Target.from_csv(self.full_path+"data/test_tar_wstd.csv")
        self.assertListEqual(tar.frequency.tolist(), [1.55, 2.00])
        self.assertListEqual(tar.velocity.tolist(), [200, 500.01245])
        self.assertListEqual(tar.velstd.tolist(), [60.012111, 100.00001])
        self.assertListEqual(tar.wavelength.tolist(),
                             [200/1.55, 500.01245/2.00])

        # Without standard deviation provided.
        tar = swipp.Target.from_csv(self.full_path+"data/test_tar_wostd.csv")
        self.assertListEqual(tar.frequency.tolist(), [1.55, 2.00])
        self.assertListEqual(tar.velocity.tolist(), [200, 500.01245])
        self.assertListEqual(tar.velstd.tolist(), [0, 0])
        self.assertListEqual(tar.wavelength.tolist(),
                             [200/1.55, 500.01245/2.00])

    def test_setcov(self):
        frequency = [1, 2, 3]
        velocity = np.array([10, 100, 1000])
        tar = swipp.Target(frequency, velocity, None)

        cov = 0.01
        tar.setmincov(cov)
        self.assertArrayEqual(tar.velstd, velocity*cov)

        cov = 0.05
        tar.setcov(cov)
        self.assertArrayEqual(tar.velstd, velocity*cov)

        cov = 0.01
        tar.setmincov(cov)
        self.assertArrayEqual(tar.velstd, velocity*0.05)

    def test_is_vel_std(self):
        frequency = [0.1, 0.2, 0.3]
        velocity = [10., 20., 30.]
        velstd = None
        tar = swipp.Target(frequency, velocity, velstd)
        self.assertTrue(tar.is_no_velstd())

        velstd = 0.1
        tar = swipp.Target(frequency, velocity, velstd)
        self.assertFalse(tar.is_no_velstd())

    def test_pseudo_vs(self):
        frequency = [0.1, 0.2, 0.3]
        velocity = np.array([10., 20., 30.])
        velstd = None
        tar = swipp.Target(frequency, velocity, velstd)
        velocity_factor = 1.1
        self.assertArrayEqual(tar.pseudo_vs(velocity_factor),
                              velocity*velocity_factor)

    def test_pseudo_depth(self):
        frequency = np.array([0.1, 0.2, 0.3])
        velocity = np.array([10., 20., 30.])
        velstd = None
        wavelength = velocity/frequency
        tar = swipp.Target(frequency, velocity, velstd)
        depth_factor = 2.5
        self.assertArrayEqual(tar.pseudo_depth(depth_factor),
                              wavelength/depth_factor)

    def test_cut(self):
        frequency = np.array([1, 2, 3, 4, 5])
        velocity = np.array([1, 2, 3, 4, 5])
        velstd = np.array([1, 2, 3, 4, 5])

        tar = swipp.Target(frequency, velocity, velstd)
        tar.cut(pmin=1.5, pmax=4.5, domain="frequency")

        self.assertListEqual(tar.frequency.tolist(), [2, 3, 4])
        self.assertListEqual(tar.velocity.tolist(), [2, 3, 4])
        self.assertListEqual(tar.velstd.tolist(), [2, 3, 4])

    def test_resample(self):
        fname = self.full_path+"data/test_tar_wstd_linear.csv"
        tar = swipp.Target.from_csv(fname)
        returned = tar.resample(pmin=0.5, pmax=4.5, pn=5,
                                res_type='linear', domain="frequency",
                                inplace=False).frequency
        expected = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
        self.assertArrayAlmostEqual(expected, returned, places=1)

        fname = self.full_path+"data/test_tar_wstd_linear.csv"
        tar = swipp.Target.from_csv(fname)
        expected = np.array([2., 2.8, 4.0])
        returned = tar.resample(pmin=2, pmax=4, pn=3,
                               res_type='log', domain="frequency",
                               inplace=False).frequency
        self.assertArrayAlmostEqual(expected, returned, places=1)

        fname = self.full_path+"data/test_tar_wstd_nonlin_0.csv"
        tar = swipp.Target.from_csv(fname)
        new_tar = tar.resample(pmin=50, pmax=100, pn=5,
                               res_type='log', domain="wavelength",
                               inplace=False)
        expected = np.array([112.5, 118.1, 125.5, 135.6, 150])
        returned = new_tar.velocity
        self.assertArrayAlmostEqual(expected, returned, places=1)

        expected = np.array([100, 84.09, 70.7, 59.5, 50])
        returned = new_tar.wavelength
        self.assertArrayAlmostEqual(expected, returned, places=1)

    def test_vr40(self):
        fname = self.full_path+"data/test_tar_wstd_nonlin_0.csv"
        tar = swipp.Target.from_csv(fname)
        self.assertAlmostEqual(tar.vr40, 180, places=1)

        fname = self.full_path+"data/test_tar_wstd_nonlin_1.csv"
        tar = swipp.Target.from_csv(fname)
        self.assertAlmostEqual(tar.vr40, 267.2, places=1)

    def test_to_target(self):
        prefix = self.full_path+"data/test_tar_wstd_nonlin_1" 
        tar = swipp.Target.from_csv(prefix + ".csv")
        tar.to_target(fname_prefix=prefix+"_swipp_v3", version="3")
        tar.to_target(fname_prefix=prefix+"_swipp_v2", version="2")

        tar_swipp = swipp.Target.from_target(prefix+"_swipp_v3", version="3")
        tar_geopsy = swipp.Target.from_target(prefix+"_geopsy_v3", version="3")
        self.assertEqual(tar_geopsy, tar_swipp)

        tar_swipp = swipp.Target.from_target(prefix+"_swipp_v2", version="2")
        tar_geopsy = swipp.Target.from_target(prefix+"_geopsy_v2", version="2")
        self.assertEqual(tar_geopsy, tar_swipp)

if __name__ == '__main__':
    unittest.main()
