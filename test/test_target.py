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

"""Tests for the Target class."""

import os
import logging
import warnings

import numpy as np
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

from testtools import unittest, TestCase, get_full_path
import swprepost

logging.basicConfig(level=logging.ERROR)


class Test_Target(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_init(self):
        # With standard deviation provided.
        frequency = np.array([1, 2, 3])
        velocity = np.array([100, 50, 25])
        velstd = np.array([5, 2.5, 1.25])
        tar = swprepost.Target(frequency, velocity, velstd)
        self.assertArrayEqual(tar.frequency, frequency)
        self.assertArrayEqual(tar.velocity, velocity)
        self.assertArrayEqual(tar.velstd, velstd)

        # Without standard deviation.
        frequency = np.array([1, 2, 3])
        velocity = np.array([100, 50, 25])
        velstd = None
        tar = swprepost.Target(frequency, velocity, velstd)
        self.assertArrayEqual(tar.frequency, frequency)
        self.assertArrayEqual(tar.velocity, velocity)
        self.assertArrayEqual(tar.velstd, np.zeros(velocity.shape))

        # With COV.
        frequency = np.array([1, 2, 3])
        velocity = np.array([100, 50, 25])
        velstd = 0.01
        tar = swprepost.Target(frequency, velocity, velstd)
        self.assertArrayEqual(tar.frequency, frequency)
        self.assertArrayEqual(tar.velocity, velocity)
        self.assertArrayEqual(tar.velstd, velocity*velstd)

        # With list.
        a = [1, 2, 3]
        tar = swprepost.Target(a, a, a)
        self.assertListEqual(tar.frequency.tolist(), a)

        # With unequal lists.
        a = [1, 2, 3]
        b = [1, 2]
        self.assertRaises(IndexError, swprepost.Target, a, b, a)

    def test_setters(self):
        x = [1, 3, 2]
        tar = swprepost.Target(x, x, velstd=x)

        # Check _check_new_value
        self.assertRaises(ValueError, tar._check_new_value, [1, 2])

        new = [1, 4, 5]
        expected = np.array(new)
        # Frequency
        tar.frequency = new
        self.assertArrayEqual(expected, tar.frequency)

        # Velocity
        tar.velocity = new
        self.assertArrayEqual(expected, tar.velocity)

        # VelStd
        tar.velstd = new
        self.assertArrayEqual(expected, tar.velstd)

    def test_sort(self):
        x = [1, 3, 2]
        tar = swprepost.Target(x, x, velstd=x)

        # Check sort
        expected = np.array([1, 2, 3])
        for attr in ["frequency", "velocity", "velstd"]:
            returned = getattr(tar, attr)
            self.assertArrayEqual(expected, returned)

    def test_from_csv(self):
        # With standard deviation provided.
        tar = swprepost.Target.from_csv(self.full_path+"data/test_tar_wstd.csv")
        self.assertListEqual(tar.frequency.tolist(), [1.55, 2.00])
        self.assertListEqual(tar.velocity.tolist(), [200, 500.01245])
        self.assertListEqual(tar.velstd.tolist(), [60.012111, 100.00001])
        self.assertListEqual(tar.wavelength.tolist(),
                             [200/1.55, 500.01245/2.00])

        # Without standard deviation provided.
        tar = swprepost.Target.from_csv(self.full_path+"data/test_tar_wostd.csv")
        self.assertListEqual(tar.frequency.tolist(), [1.55, 2.00])
        self.assertListEqual(tar.velocity.tolist(), [200, 500.01245])
        self.assertListEqual(tar.velstd.tolist(), [0, 0])
        self.assertListEqual(tar.wavelength.tolist(),
                             [200/1.55, 500.01245/2.00])

        # With incorrect formatting
        fname = self.full_path+"data/test_tar_bad.csv"
        self.assertRaises(ValueError, swprepost.Target.from_csv, fname)

    def test_setcov(self):
        frequency = [1, 2, 3]
        velocity = np.array([10, 100, 1000])
        tar = swprepost.Target(frequency, velocity, None)

        cov = 0.01
        tar.setmincov(cov)
        self.assertArrayEqual(tar.velstd, velocity*cov)

        cov = 0.05
        tar.setcov(cov)
        self.assertArrayEqual(tar.velstd, velocity*cov)

        cov = 0.01
        tar.setmincov(cov)
        self.assertArrayEqual(tar.velstd, velocity*0.05)

        # Bad cov
        cov = -0.1
        self.assertRaises(ValueError, tar.setmincov, cov)

    def test_is_vel_std(self):
        frequency = [0.1, 0.2, 0.3]
        velocity = [10., 20., 30.]
        velstd = None
        tar = swprepost.Target(frequency, velocity, velstd)
        self.assertTrue(tar.is_no_velstd)

        velstd = 0.1
        tar = swprepost.Target(frequency, velocity, velstd)
        self.assertFalse(tar.is_no_velstd)

    def test_pseudo_vs(self):
        frequency = [0.1, 0.2, 0.3]
        velocity = np.array([10., 20., 30.])
        velstd = None
        tar = swprepost.Target(frequency, velocity, velstd)
        velocity_factor = 1.1
        self.assertArrayEqual(tar.pseudo_vs(velocity_factor),
                              velocity*velocity_factor)

        # Velocity factor outside the typical range
        velocity_factor = 0.5
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertArrayEqual(tar.pseudo_vs(velocity_factor),
                                  tar.velocity*velocity_factor)

    def test_pseudo_depth(self):
        frequency = np.array([0.1, 0.2, 0.3])
        velocity = np.array([10., 20., 30.])
        velstd = None
        wavelength = velocity/frequency
        tar = swprepost.Target(frequency, velocity, velstd)
        depth_factor = 2.5
        self.assertArrayEqual(tar.pseudo_depth(depth_factor),
                              wavelength/depth_factor)

        # Depth factor outside the typical range
        depth_factor = 0.5
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertArrayEqual(tar.pseudo_depth(depth_factor),
                                  wavelength/depth_factor)

    def test_cut(self):
        frequency = np.array([1, 2, 3, 4, 5])
        velocity = np.array([1, 2, 3, 4, 5])
        velstd = np.array([1, 2, 3, 4, 5])

        tar = swprepost.Target(frequency, velocity, velstd)
        tar.cut(pmin=1.5, pmax=4.5, domain="frequency")

        self.assertListEqual(tar.frequency.tolist(), [2, 3, 4])
        self.assertListEqual(tar.velocity.tolist(), [2, 3, 4])
        self.assertListEqual(tar.velstd.tolist(), [2, 3, 4])

        # Bad domain
        self.assertRaises(NotImplementedError, tar.cut, pmin=2, pmax=4,
                          domain="slowness")

    def test_easy_resample(self):
        # Inplace=False
        # Linear w/ VelStd
        fname = self.full_path+"data/test_tar_wstd_linear.csv"
        tar = swprepost.Target.from_csv(fname)
        returned = tar.easy_resample(pmin=0.5, pmax=4.5, pn=5,
                                res_type='linear', domain="frequency",
                                inplace=False).frequency
        expected = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
        self.assertArrayAlmostEqual(expected, returned, places=1)

        # Linear w/ VelStd
        fname = self.full_path+"data/test_tar_wstd_linear.csv"
        tar = swprepost.Target.from_csv(fname)
        expected = np.array([2., 2.8, 4.0])
        returned = tar.easy_resample(pmin=2, pmax=4, pn=3,
                                res_type='log', domain="frequency",
                                inplace=False).frequency
        self.assertArrayAlmostEqual(expected, returned, places=1)

        # Non-linear w/ VelStd
        fname = self.full_path+"data/test_tar_wstd_nonlin_0.csv"
        tar = swprepost.Target.from_csv(fname)
        new_tar = tar.easy_resample(pmin=50, pmax=100, pn=5,
                               res_type='log', domain="wavelength",
                               inplace=False)
        expected = np.array([112.5, 118.1, 125.5, 135.6, 150])
        returned = new_tar.velocity
        self.assertArrayAlmostEqual(expected, returned, places=1)

        expected = np.array([100, 84.09, 70.7, 59.5, 50])
        returned = new_tar.wavelength
        self.assertArrayAlmostEqual(expected, returned, places=1)

        # Inplace=True
        x = [0.1, 0.2, 0.4, 0.5]
        tar = swprepost.Target(x, x, x)

        for pmin, pmax in [(0.1, 0.5), (0.5, 0.1)]:
            tar.easy_resample(pmin=pmin, pmax=pmax, pn=5, domain="frequency",
                         res_type="linear", inplace=True)

            expected = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
            for attr in ["frequency", "velocity", "velstd"]:
                returned = getattr(tar, attr)
                self.assertArrayAlmostEqual(expected, returned)

        # Bad pn
        self.assertRaises(ValueError, tar.easy_resample, pmin=0.1, pmax=0.5, pn=-1)

        # Bad res_type
        self.assertRaises(NotImplementedError, tar.easy_resample, pmin=0.1,
                          pmax=0.5, pn=5, res_type="log-spiral")

    def test_vr40(self):
        fname = self.full_path+"data/test_tar_wstd_nonlin_0.csv"
        tar = swprepost.Target.from_csv(fname)
        self.assertAlmostEqual(tar.vr40, 180, places=1)

        fname = self.full_path+"data/test_tar_wstd_nonlin_1.csv"
        tar = swprepost.Target.from_csv(fname)
        self.assertAlmostEqual(tar.vr40, 267.2, places=1)

        # Vr40 out of range
        x = [1, 2, 3]
        tar = swprepost.Target(x, x, x)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertTrue(tar.vr40 is None)

    def test_to_and_from_target(self):
        prefix = self.full_path+"data/test_tar_wstd_nonlin_1"
        tar = swprepost.Target.from_csv(prefix + ".csv")
        tar.to_target(fname_prefix=prefix+"_swprepost_v3", version="3")
        tar.to_target(fname_prefix=prefix+"_swprepost_v2", version="2")

        tar_swprepost = swprepost.Target.from_target(prefix+"_swprepost_v3", version="3")
        tar_geopsy = swprepost.Target.from_target(prefix+"_geopsy_v3", version="3")
        self.assertEqual(tar_geopsy, tar_swprepost)
        os.remove(prefix+"_swprepost_v3.target")

        tar_swprepost = swprepost.Target.from_target(prefix+"_swprepost_v2", version="2")
        tar_geopsy = swprepost.Target.from_target(prefix+"_geopsy_v2", version="2")
        self.assertEqual(tar_geopsy, tar_swprepost)
        os.remove(prefix+"_swprepost_v2.target")

        # Bad version
        self.assertRaises(NotImplementedError, tar.to_target,
                          fname_prefix="blahbal", version="12000")
        self.assertRaises(NotImplementedError, tar.from_target,
                          fname_prefix=prefix+"_geopsy_v3", version="12000")

    def test_to_and_from_dinver_txt(self):
        frq = [1, 3, 5, 7, 9, 15]
        vel = [200, 150, 112, 95, 90, 85]
        velstd = [10, 8, 6, 5, 5, 5]
        tar = swprepost.Target(frq, vel, velstd)

        fname = self.full_path+"test_dinver_txt.txt"
        for version in ["2", "3"]:
            tar.to_txt_dinver(fname, version=version)
            new = swprepost.Target.from_txt_dinver(fname, version=version)

            for attr in ["frequency", "velocity", "velstd"]:
                expected = getattr(tar, attr)
                returned = getattr(new, attr)
                self.assertArrayAlmostEqual(expected, returned, places=0)

        # Bad verison
        version = "1245"
        self.assertRaises(NotImplementedError, tar.to_txt_dinver,
                          fname, version=version)
        self.assertRaises(NotImplementedError, swprepost.Target.from_txt_dinver,
                          fname, version=version)

        os.remove(fname)

    def test_to_and_from_csv(self):
        frq = [1, 3, 5, 7, 9, 15]
        vel = [200, 150, 112, 95, 90, 85]
        velstd = [10, 8, 6, 5, 5, 5]
        tar = swprepost.Target(frq, vel, velstd)

        fname = self.full_path+"test_csv.txt"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar.to_txt_swipp(fname)
        new = swprepost.Target.from_csv(fname)
        self.assertEqual(tar, new)

        os.remove(fname)

    def test_str_and_repr(self):
        x = np.array([1, 2.01, 3.155])
        tar = swprepost.Target(x, x, x)

        arr = "[1.   2.01 3.16]"
        expected = f"Target(frequency={arr}, velocity={arr}, velstd={arr})"
        returned = tar.__repr__()
        self.assertEqual(expected, returned)

        expected = "Target with 3 frequency/wavelength points"
        returned = tar.__str__()
        self.assertEqual(expected, returned)

    def test_eq(self):
        x = [1, 2]
        tar1 = swprepost.Target(x, x, x)

        # False - Wrong Values
        y = [1, 15]
        tar2 = swprepost.Target(y, y, y)
        self.assertFalse(tar1 == tar2)

        # False - Wrong Length
        y = [1, 2, 3]
        tar2 = swprepost.Target(y, y, y)
        self.assertFalse(tar1 == tar2)

    def test_notebook(self):
        fname = "../examples/basic/Targets.ipynb"
        with open(self.full_path+fname) as f:
            nb = nbformat.read(f, as_version=4)

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
                ep.preprocess(
                    nb, {'metadata': {'path': self.full_path+"../examples/basic"}})
        finally:
            with open(self.full_path+fname, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)


if __name__ == '__main__':
    unittest.main()
