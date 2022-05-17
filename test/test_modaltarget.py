# This file is part of swprepost, a Python package for surface wave
# inversion pre- and post-processing.
# Copyright (C) 2019-2022 Joseph P. Vantassel (jvantassel@utexas.edu)
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

"""Tests for the ModalTarget class."""

import os
import logging
import warnings

import numpy as np

from testtools import unittest, TestCase, get_path
import swprepost

logging.basicConfig(level=logging.ERROR)


class Test_ModalTarget(TestCase):

    def setUp(self):
        self.path = get_path(__file__)

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
        # TODO (jpv): Remove after v2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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

        # With malformed description (tuple instead of tuple of tuple).
        a = [1, 2, 3]
        d = ("rayleigh", 0)
        self.assertRaises(TypeError, swprepost.ModalTarget, a, a, a, d)

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
        # TODO(jpv): Remove entire test and replace with below in version >2.0.0.
        # TODO(jpv): Remove file "data/test_tar_wstd.csv"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar = swprepost.Target.from_csv(
                self.path / "data/tar/test_from_csv_wstd.csv")
        self.assertArrayEqual(tar.frequency, np.array([1.55, 2.00]))
        self.assertArrayEqual(tar.velocity, np.array([200, 500.01]))
        self.assertArrayEqual(tar.velstd, np.array([60.0, 100.0]))
        self.assertEqual(tar.description, (("rayleigh", 0),))

        # TODO(jpv): Add metadata to csv for version >2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar = swprepost.Target.from_csv(
                self.path / "data/tar/test_from_csv_wstd.csv")
        self.assertArrayEqual(tar.frequency, np.array([1.55, 2.00]))
        self.assertArrayEqual(tar.velocity, np.array([200, 500.01]))
        self.assertArrayEqual(tar.velstd, np.array([60.0, 100.0]))
        self.assertEqual(tar.description, (("rayleigh", 0),))

        # Without standard deviation provided.
        # TODO(jpv): Remove entire test and replace with below in version >2.0.0.
        # TODO(jpv): Remove file "data/test_tar_wostd.csv"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar = swprepost.Target.from_csv(
                self.path / "data/tar/test_from_csv_wostd.csv")
        self.assertArrayEqual(tar.frequency, np.array([1.55, 2.00]))
        self.assertArrayEqual(tar.velocity, np.array([200, 500.01]))
        self.assertArrayEqual(tar.velstd, np.array([0, 0]))
        self.assertEqual(tar.description, (("rayleigh", 0),))

        # TODO(jpv): Add metadata to csv for version >2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar = swprepost.Target.from_csv(
                self.path / "data/tar/test_from_csv_wostd.csv")
        self.assertArrayEqual(tar.frequency, np.array([1.55, 2.00]))
        self.assertArrayEqual(tar.velocity, np.array([200, 500.01]))
        self.assertArrayEqual(tar.velstd, np.array([0, 0]))
        self.assertEqual(tar.description, (("rayleigh", 0),))

        # With incorrect formatting
        # TODO(jpv): Add metadata to csv for version >2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fname = self.path / "data/tar/test_from_csv_bad.csv"
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

        # TODO (jpv): Remove after v2.0.0.
        velstd = 0.1
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
        fname = self.path / "data/tar/test_easy_resample_linear_wstd.csv"
        tar = swprepost.Target.from_csv(fname)
        returned = tar.easy_resample(pmin=0.5, pmax=4.5, pn=5,
                                     res_type='linear', domain="frequency",
                                     inplace=False).frequency
        expected = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
        self.assertArrayAlmostEqual(expected, returned, places=1)

        # Linear w/ VelStd
        fname = self.path / "data/tar/test_easy_resample_linear_wstd.csv"
        tar = swprepost.Target.from_csv(fname)
        expected = np.array([2., 2.8, 4.0])
        returned = tar.easy_resample(pmin=2, pmax=4, pn=3,
                                     res_type='log', domain="frequency",
                                     inplace=False).frequency
        self.assertArrayAlmostEqual(expected, returned, places=1)

        # Non-linear w/ VelStd
        fname = self.path / "data/tar/test_tar_wstd_nonlin_0.csv"
        # TODO(jpv): Add metadata to csv for version >2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
        self.assertRaises(ValueError, tar.easy_resample,
                          pmin=0.1, pmax=0.5, pn=-1)

        # Bad res_type
        self.assertRaises(NotImplementedError, tar.easy_resample, pmin=0.1,
                          pmax=0.5, pn=5, res_type="log-spiral")

    def test_vr40(self):
        fname = self.path / "data/tar/test_tar_wstd_nonlin_0.csv"
        # TODO(jpv): Add metadata to csv for version >2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar = swprepost.Target.from_csv(fname)
        self.assertAlmostEqual(tar.vr40, 180, places=1)

        fname = self.path / "data/tar/test_tar_wstd_nonlin_1.csv"
        # TODO(jpv): Add metadata to csv for version >2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar = swprepost.Target.from_csv(fname)
        self.assertAlmostEqual(tar.vr40, 267.2, places=1)

        # Vr40 out of range
        x = [1, 2, 3]
        tar = swprepost.Target(x, x, x)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertTrue(tar.vr40 is None)

    def test_to_and_from_target(self):
        # TODO(jpv): Add metadata to csv for version >2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar = swprepost.Target.from_csv(
                self.path / "data/tar/swinvert_tar1.csv")

        prefix = str(self.path / "data/tar/from_tar1_")
        # TODO(jpv): Put specific versions and remove filter after v2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar.to_target(prefix+"3.4.2_swprepost", version="3")
            tar.to_target(prefix+"2.10.1_swprepost", version="2")

        # TODO(jpv): Remove text and replace with test below after v2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar_swprepost = swprepost.Target.from_target(
                prefix+"3.4.2_swprepost", version="3")
            tar_geopsy = swprepost.Target.from_target(
                prefix+"3.4.2_dinver", version="3")
        self.assertEqual(tar_geopsy, tar_swprepost)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar_swprepost = swprepost.Target.from_target(
                prefix+"3.4.2_swprepost", version="3.4.2")
            tar_geopsy = swprepost.Target.from_target(
                prefix+"3.4.2_dinver", version="3.4.2")
        self.assertEqual(tar_geopsy, tar_swprepost)

        # TODO(jpv): Remove text and replace with test below after v2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar_swprepost = swprepost.Target.from_target(
                prefix+"2.10.1_swprepost", version="2")
            tar_geopsy = swprepost.Target.from_target(
                prefix+"2.10.1_dinver", version="2")
        self.assertEqual(tar_geopsy, tar_swprepost)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tar_swprepost = swprepost.Target.from_target(
                prefix+"2.10.1_swprepost", version="2.10.1")
            tar_geopsy = swprepost.Target.from_target(
                prefix+"2.10.1_dinver", version="2.10.1")
        self.assertEqual(tar_geopsy, tar_swprepost)

        # Bad version
        # TODO(jpv): Add metadata to csv for version >2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertRaises(NotImplementedError, tar.to_target,
                              fname_prefix="blahbal", version="12000")
            self.assertRaises(NotImplementedError, tar.from_target,
                              fname_prefix=prefix+"3.4.2_dinver", version="12000")

        for version in swprepost.meta.SUPPORTED_GEOPSY_VERSIONS:
            os.remove(
                self.path / f"data/tar/from_tar1_{version}_swprepost.target")

    def test_to_and_from_dinver_txt(self):
        frq = [1, 3, 5, 7, 9, 15]
        vel = [200, 150, 112, 95, 90, 85]
        velstd = [10, 8, 6, 5, 5, 5]
        tar = swprepost.Target(frq, vel, velstd)

        fname = self.path / "test_dinver_txt.txt"
        # TODO(jpv): Put specific versions and remove filter after v2.0.0.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            for version in ["2", "3"]:
                tar.to_txt_dinver(fname, version=version)
                new = swprepost.Target.from_txt_dinver(fname, version=version)

                for attr in ["frequency", "velocity", "velstd"]:
                    expected = getattr(tar, attr)
                    returned = getattr(new, attr)
                    self.assertArrayAlmostEqual(expected, returned, places=0)

        # Bad version.
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

        fname = self.path / "test_csv.txt"
        tar.to_csv(fname)
        new = swprepost.Target.from_csv(fname)
        self.assertEqual(tar, new)

        os.remove(fname)

    def test_str_and_repr(self):
        x = np.array([1, 2.01, 3.155])
        tar = swprepost.Target(x, x, x)
        description = (("rayleigh", 0),)

        arr = "[1.   2.01 3.16]"
        expected = f"ModalTarget(frequency={arr}, velocity={arr}, velstd={arr}, description={description})"
        returned = tar.__repr__()
        self.assertEqual(expected, returned)

        expected = "ModalTarget with 3 frequency points."
        returned = tar.__str__()
        self.assertEqual(expected, returned)

    def test_eq(self):
        x = [1, 2]
        y = [1, 15]
        z = [1, 2, 3]

        i = (("rayleigh", 0),)
        j = (("love", 0),)
        k = (("rayleigh", 0), ("rayleigh", 1))

        a = swprepost.ModalTarget(x, x, x, i)

        b = swprepost.ModalTarget(y, y, y, i)
        c = swprepost.ModalTarget(x, x, x, j)
        d = swprepost.ModalTarget(x, x, x, k)
        e = swprepost.ModalTarget(y, y, y, j)
        f = swprepost.ModalTarget(z, z, z, i)

        self.assertEqual(a, a)

        self.assertNotEqual(a, x)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)
        self.assertNotEqual(a, e)
        self.assertNotEqual(a, f)


if __name__ == '__main__':
    unittest.main()
