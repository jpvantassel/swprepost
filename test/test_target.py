"""
Tests for target class.
"""

import swipp
import unittest
import os

file_name = __file__.split("/")[-1]
full_path = __file__[:-len(file_name)]


class TestTarget(unittest.TestCase):

    # Test constructor
    def test_witherror(self):
        """Test if frequency, velocity, and wavelength have been defined 
        correctly."""
        tar = swipp.Target(full_path+"data/test_tar_wstd.csv")
        self.assertListEqual(tar.freq, [1.55, 2.00])
        self.assertListEqual(tar.vel, [200, 500.01245])
        self.assertListEqual(tar.velstd, [60.012111, 100.00001])
        self.assertListEqual(tar.wavelength, [200/1.55, 500.01245/2.00])

    def test_withoerror(self):
        """Test if frequency, velocity, and wavelength have been defined
         correctly."""
        tar = swipp.Target(full_path+"data/test_tar_wostd.csv")
        self.assertListEqual(tar.freq, [1.55, 2.00])
        self.assertListEqual(tar.vel, [200, 500.01245])
        self.assertListEqual(tar.velstd, [0, 0])
        self.assertListEqual(tar.wavelength, [200/1.55, 500.01245/2.00])

    def test_setcov(self):
        """Check if setCOV works for three typical cases: no std_dev, 
        set std_dev, and no change to set std_dev.
        """
        tar = swipp.Target(full_path+"data/test_tar_wostd.csv")
        cov = 0.01
        tar.setmincov(cov)
        self.assertAlmostEqual(tar.velstd[0], tar.velstd[0])

        cov = 0.05
        tar.setcov(cov)
        self.assertAlmostEqual(tar.velstd[0], 200*cov)

        cov = 0.01
        tar.setmincov(cov)
        self.assertAlmostEqual(tar.velstd[0], tar.velstd[0])

    def test_isvelstd_true(self):
        "Check if file appropriately returns if std_dev has been defined."
        tar = swipp.Target(full_path+"data/test_tar_wostd.csv")
        self.assertTrue(tar.is_no_velstd())

        tar = swipp.Target(full_path+"data/test_tar_wstd.csv")
        self.assertFalse(tar.is_no_velstd())

    def test_dc_to_pseudovs(self):
        "Check dispersion curve to pseudo depth and Vs calcuation."
        tar = swipp.Target(full_path+"data/test_tar_wstd.csv")
        self.assertAlmostEqual(max(tar.pseudo()[0]),
                               max(tar.vel)*1.1)
        self.assertAlmostEqual(max(tar.pseudo()[1]),
                               max(tar.wavelength)/2.5)

    def test_cut(self):
        "Check cut is working correctly."
        tar = swipp.Target(full_path+"data/test_tar_wstd_linear.csv")
        tar.cut((1.5, 4.5), domain="frequecy")

        self.assertListEqual(tar.freq, [2, 3, 4])
        self.assertListEqual(tar.vel, [2, 3, 4])
        self.assertListEqual(tar.velstd, [2, 3, 4])

    def test_resample(self):
        "Check resample calculation is working correctly."
        tar = swipp.Target(full_path+"data/test_tar_wstd_linear.csv")
        known_vals = (0.5, 1.5, 2.5, 3.5, 4.5)
        test_vals = tar.resample(
            res_range=(0.5, 4.5, 5), res_by='frequency', res_type='linear', inplace=False)
        for test_val in test_vals[:-1]:
            for known, test in zip(known_vals, test_val):
                self.assertAlmostEqual(known, test, places=1)

        tar = swipp.Target(full_path+"data/test_tar_wstd_linear.csv")
        known_vals = (2., 2.8284, 4.0)
        test_vals = tar.resample(
            res_range=(2, 4, 3), res_by='frequency', res_type='log', inplace=False)
        for test_val in test_vals[:-1]:
            for known, test in zip(known_vals, test_val):
                self.assertAlmostEqual(known, test, places=1)

        tar = swipp.Target(full_path+"data/test_tar_wstd_nonlin_0.csv")
        known_vel = (150, 135.6, 125.6, 118.3, 112.8)
        known_wave = (50, 59.5, 70.7, 84.09, 100)
        test_vals = tar.resample(
            res_range=(50, 100, 5), res_by='wavelength', res_type='log', inplace=False)
        for known, test in zip(known_wave, test_vals[-1]):
            self.assertAlmostEqual(known, test, places=1)
        for known, test in zip(known_vel, test_vals[1]):
            self.assertAlmostEqual(known, test, places=0)

    def test_vr40(self):
        "Check Vr40 calculation is working correctly."
        tar = swipp.Target(full_path+"data/test_tar_wstd_nonlin_1.csv")
        known_vals = (6.7, 267.2, 13.4, 40.0)
        test_vals = tar.vr40()
        for known, test in zip(known_vals, test_vals):
            self.assertAlmostEqual(known, test, places=1)

        tar = swipp.Target(full_path+"data/test_tar_wstd_nonlin_0.csv")
        known_vals = (4.5, 180, 0.85, 40.0)
        test_vals = tar.vr40()
        for known, test in zip(known_vals, test_vals):
            self.assertAlmostEqual(known, test, places=1)

    def test_write_to_file(self):
        """
        Check if dispersion data as well as dispersion data with H/V can
        be written to .target file. Need to use DINVER to confirm file 
        was sucessfully written. 
        """
        tar = swipp.Target(full_path+"data/test_tar_wstd_nonlin_1.csv")
        tar.write_to_file(fname=full_path+"data/test")
        self.assertTrue(os.path.isfile(full_path+"data/test.target"))

        # print("Go check files test.target wrote correclty!")
        # TODO: Write code to uncompress and compare the two files to two files
        # that are known to work.

        os.remove(full_path+"data/test.target")
        # os.remove(full_path+"data/test_wHV.target")


if __name__ == '__main__':
    unittest.main()
