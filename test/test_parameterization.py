"""Tests for Parameterization class."""

from testtools import unittest, TestCase, get_full_path
import warnings
import swipp
import os
import tarfile as tar
import logging
logging.basicConfig(level=logging.DEBUG)


class Test_Parameterization(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_init(self):
        # Define parameterization in terms of depths
        vp = swipp.Parameter(lay_min=[1, 5], lay_max=[3, 16],
                             par_min=[200, 400], par_max=[400, 600],
                             par_rev=[True, False],
                             lay_type="depth")
        pr = swipp.Parameter(lay_min=[0], lay_max=[100],
                             par_min=[0.2], par_max=[0.5],
                             par_rev=[False],
                             lay_type="depth")
        vs = swipp.Parameter(lay_min=[1, 2], lay_max=[2, 3],
                             par_min=[100, 200], par_max=[200, 300],
                             par_rev=[True, False],
                             lay_type="depth")
        rh = swipp.Parameter(lay_min=[0], lay_max=[100],
                             par_min=[2000], par_max=[2000],
                             par_rev=[False],
                             lay_type="depth")
        test = swipp.Parameterization(vp, pr, vs, rh)
        self.assertTrue(test)

        # Define parameters in terms of thicknesses
        vp = swipp.Parameter(lay_min=[1, 5], lay_max=[3, 16],
                             par_min=[200, 400], par_max=[400, 600],
                             par_rev=[True, False],
                             lay_type="thickness")
        pr = swipp.Parameter(lay_min=[0], lay_max=[100],
                             par_min=[0.2], par_max=[0.5],
                             par_rev=[False],
                             lay_type="thickness")
        vs = swipp.Parameter(lay_min=[1, 2], lay_max=[2, 3],
                             par_min=[100, 200], par_max=[200, 300],
                             par_rev=[True, False],
                             lay_type="thickness")
        rh = swipp.Parameter(lay_min=[0], lay_max=[100],
                             par_min=[2000], par_max=[2000],
                             par_rev=[False],
                             lay_type="thickness")
        test = swipp.Parameterization(vp, pr, vs, rh)
        self.assertTrue(test)

    def test_from_min_max(self):
        rh = ['FX', 2000]
        vs = ['FTL', 5, 2, 100, 200, True]
        pr = ['LN-thickness', 3, 0.2, 0.5, False]
        vp = ['LNI', 2, 1.2, 200, 400, True]
        wv = [1, 100]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            param = swipp.Parameterization.from_min_max(vp, pr, vs, rh, wv)
            # Fixed - FX
            self.assertEqual(rh[0], param.rh._par_type)
            self.assertEqual(rh[1], param.rh.par_value)
            self.assertListEqual([rh[1]], param.rh.par_min)

            # Fixed Thickness Layers - FTL
            self.assertEqual(vs[0], param.vs._par_type)
            self.assertEqual(vs[1], param.vs.par_value)
            self.assertEqual(vs[2], param.vs.par_add_value)
            self.assertListEqual([vs[2]]*vs[1], param.vs.lay_min)
            self.assertListEqual([vs[2]]*vs[1], param.vs.lay_max)
            self.assertListEqual([vs[3]]*vs[1], param.vs.par_min)
            self.assertListEqual([vs[4]]*vs[1], param.vs.par_max)
            self.assertListEqual([vs[5]]*vs[1], param.vs.par_rev)

            # Layering by Number - LN-thickness (deprecated)
            self.assertEqual(pr[0], param.pr._par_type)
            self.assertEqual(pr[1], param.pr.par_value)
            self.assertListEqual([wv[0]/3]*pr[1], param.pr.lay_min)
            self.assertListEqual([wv[1]/(2*pr[1])]*pr[1], param.pr.lay_max)
            self.assertListEqual([pr[2]]*pr[1], param.pr.par_min)
            self.assertListEqual([pr[3]]*pr[1], param.pr.par_max)
            self.assertListEqual([pr[4]]*pr[1], param.pr.par_rev)

            # Layering by Number Increasing - LNI (deprecated)
            self.assertEqual(vp[0], param.vp._par_type)
            self.assertEqual(vp[1], param.vp.par_value)
            self.assertEqual(vp[2], param.vp.par_add_value)
            self.assertListEqual([wv[0]/3]*vp[1], param.vp.lay_min)
            self.assertListEqual([wv[1]/2]*vp[1], param.vp.lay_max)
            self.assertListEqual([vp[3]]*vp[1], param.vp.par_min)
            self.assertListEqual([vp[4]]*vp[1], param.vp.par_max)
            self.assertListEqual([vp[5]]*vp[1], param.vp.par_rev)

            vs = ['LN', 4, 300, 500, True]
            pr = ['LR', 3, 0.2, 0.5, False]
            param = swipp.Parameterization.from_min_max(vp, pr, vs, rh, wv)

            # Layering Ratio - LR
            self.assertEqual(pr[0], param.pr._par_type)
            self.assertEqual(pr[1], param.pr.par_value)
            lay_min, lay_max = swipp.Parameter.depth_lr(*wv, pr[1])
            self.assertListEqual(lay_min, param.pr.lay_min)
            self.assertListEqual(lay_max, param.pr.lay_max)
            self.assertListEqual([pr[2]]*len(lay_min), param.pr.par_min)
            self.assertListEqual([pr[3]]*len(lay_min), param.pr.par_max)
            self.assertListEqual([pr[4]]*len(lay_min), param.pr.par_rev)

            # Layering by Number - LN-depth or LN
            self.assertEqual(vs[0], param.vs._par_type)
            self.assertEqual(vs[1], param.vs.par_value)
            self.assertListEqual([wv[0]/3]*vs[1], param.vs.lay_min)
            self.assertListEqual([wv[1]/2]*vs[1], param.vs.lay_max)
            self.assertListEqual([vs[2]]*vs[1], param.vs.par_min)
            self.assertListEqual([vs[3]]*vs[1], param.vs.par_max)
            self.assertListEqual([vs[4]]*vs[1], param.vs.par_rev)


    # # TODO (jpv): Reintroduce test once LNI additional settings have been finished.
    # # def test_to_param(self):
    # #     """Check if parameter data can be written to .param file. Need to
    # #     use DINVER to confirm file was sucessfully written.
    # #     """
    # #     vp = ['LNI', 4, 4, 200, 400, True]
    # #     pr = ['LN-depth', 3, 0.2, 0.5, False]
    # #     vs = ['FTL', 3, 3, 100, 200, True]
    # #     rh = ['FX', 2000]
    # #     wv = [1, 100]
    # #     par = swipp.Parameterization.from_min_max(vp, pr, vs, rh, wv)
    # #     fname1 = self.full_path+"data/test_par1.param"
    # #     par.to_param(fname=fname1, version='2')
    # #     self.assertTrue(os.path.isfile(fname1))

    # #     # TODO (jpv): Automate checking process
    # #     # with tar.open(fname1, "r:gz") as f:
    # #     #     f.extractall()
    # #     # with open("contents.xml", "r") as f:
    # #     #     test_lines = f.read().splitlines()
    # #     # print(test_lines[:5])

    # #     # f = tar.open(self.full_path+"data/par1.param", "r:gz")
    # #     # f.extractall()
    # #     # f.close()

    # #     # with open("contents.xml", "r", encoding="utf-16") as f:
    # #     #     true_lines = f.read().splitlines()
    # #     os.remove(fname1)
    # #     # os.remove("contents.xml")

    # #     # for true, test in zip(true_lines, test_lines):
    # #     #     self.assertEqual(true, test)

    # #     vp = ['LR', 3, 200, 400, True]
    # #     pr = ['LNI', 3, 3, 0.2, 0.5, False]
    # #     vs = ['FTL', 5, 5, 100, 200, True]
    # #     rh = ['FX', 2000]
    # #     wv = [1, 100]
    # #     fname2 = "test_par2.param"
    # #     par = swipp.Parameterization.from_min_max(vp, pr, vs, rh, wv)
    # #     par.to_file(fname=fname2, version='2')
    # #     self.assertTrue(os.path.isfile(fname2))

    # #     # with tar.open(fname2, "r:gz") as f:
    # #     #     f.extractall()
    # #     # with open("contents.xml", "r") as f:
    # #     #     test_lines = f.read().splitlines()

    # #     # with tar.open(self.full_path+"data/par2.param", "r:gz") as f:
    # #     #     f.extractall()
    # #     # with open("contents.xml", "r") as f:
    # #     #     true_lines = f.read().splitlines()
    # #     os.remove(fname2)
    # #     # # os.remove("contents.xml")

    # #     # for true, test in zip(true_lines, test_lines):
    # #     #     self.assertEqual(true, test)


if __name__ == '__main__':
    unittest.main()
