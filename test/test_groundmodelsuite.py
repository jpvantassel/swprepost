"""Tests for GroundModelSuite class."""

import unittest
import os
import numpy as np
import swipp
import logging
logging.basicConfig(level=logging.INFO)

file_name = __file__.split("/")[-1]
full_path = __file__[:-len(file_name)]

class TestGroundModelSuite(unittest.TestCase):

    def test_init(self):
        # One GroundModel
        thk = [1, 3, 5, 7]
        vss = [100, 200, 300, 400]
        vps = [200, 400, 600, 800]
        rho = [2000, 2000, 2000, 2000]
        mygm = swipp.GroundModel(thk, vps, vss, rho)
        mysuite = swipp.GroundModelSuite(mygm, "test", misfit=2)
        self.assertListEqual(mysuite.gms[0].tk, thk)
        self.assertListEqual(mysuite.gms[0].vs, vss)
        self.assertListEqual(mysuite.gms[0].vp, vps)
        self.assertListEqual(mysuite.gms[0].rh, rho)
        self.assertEqual(mysuite.ids[0], "test")
        self.assertEqual(mysuite.misfits[0], 2)

    def test_append(self):
        thk = [1, 3, 5, 7]
        vss = [100, 200, 300, 400]
        vps = [200, 400, 600, 800]
        rho = [2000, 2000, 2000, 2000]
        mygm = swipp.GroundModel(thk, vps, vss, rho)

        # Two GroundModel
        mysuite = swipp.GroundModelSuite(mygm, "test", misfit=1)
        mysuite.append(mygm, "test2", misfit=1.1)
        for mod_num in range(2):
            self.assertListEqual(mysuite.gms[mod_num].tk, thk)
            self.assertListEqual(mysuite.gms[mod_num].vs, vss)
            self.assertListEqual(mysuite.gms[mod_num].vp, vps)
            self.assertListEqual(mysuite.gms[mod_num].rh, rho)

    def test_from_geopsy(self):
        # # Single Model
        true_tk = [0.68, 9.69, 0.018, 22.8, 43.9, 576.4, 0]
        true_vp = [196.7, 295.8, 1600.2, 1600.2, 1600.2, 4232.5, 4232.5]
        true_vs = [120.3, 120.3, 120., 231.9, 840.9, 840.9, 2095.3]
        true_rh = [2000.]*7

        test_suite = swipp.GroundModelSuite.from_geopsy(
            full_path+"data/test_gm_mod1.txt")

        self.assertListEqual(test_suite.gms[0].tk, true_tk)
        self.assertListEqual(test_suite.gms[0].vs, true_vs)
        self.assertListEqual(test_suite.gms[0].vp, true_vp)
        self.assertListEqual(test_suite.gms[0].rh, true_rh)

        # Two Model
        true_tk1 = [0.7, 9.1, 0.1, 21.9, 61.0, 571.8, 0]
        true_vp1 = [196.7, 281.4, 1392.1, 1392.1, 1392.1, 4149.1, 4149.1]
        true_vs1 = [120.3, 120.3, 120.3, 225.1, 840.9, 840.9, 2202.1]
        true_rh1 = [2000.]*7

        test_suite = swipp.GroundModelSuite.from_geopsy(
            full_path+"data/test_gm_mod2.txt")
        self.assertListEqual(test_suite.gms[0].tk, true_tk)
        self.assertListEqual(test_suite.gms[0].vs, true_vs)
        self.assertListEqual(test_suite.gms[0].vp, true_vp)
        self.assertListEqual(test_suite.gms[0].rh, true_rh)
        self.assertListEqual(test_suite.gms[1].tk, true_tk1)
        self.assertListEqual(test_suite.gms[1].vs, true_vs1)
        self.assertListEqual(test_suite.gms[1].vp, true_vp1)
        self.assertListEqual(test_suite.gms[1].rh, true_rh1)
        self.assertListEqual(test_suite.misfits, [0.766485, 0.767484])
        self.assertListEqual(test_suite.ids, ["149698", "147185"])

        # Full File
        test_suite = swipp.GroundModelSuite.from_geopsy(
            full_path+"data/test_gm_mod100.txt")
        # TODO (jpv): Write test for full file.

    def test_vs30(self):
        thk = [5, 20, 0]
        vps = [300, 600, 800]
        vss = [150, 300, 400]
        rho = [2000]*3
        mygm = swipp.GroundModel(thk, vps, vss, rho)

        mysuite = swipp.GroundModelSuite(mygm, "test")
        for _x in range(5):
            mysuite.append(mygm, "test")
        self.assertListEqual(mysuite.vs30(), [266.6666666666666666666]*6)

    def test_median(self):
        tks = [[1, 5, 0], [2, 4, 0], [5, 10, 0]]
        vss = [[100, 200, 300], [150, 275, 315], [100, 300, 200]]
        vps = [[300, 500, 300], [600, 700, 800], [300, 1000, 400]]
        rhs = [[2000]*3, [2300]*3, [2200]*3]

        gm = swipp.GroundModel(tks[0], vps[0], vss[0], rhs[0])
        suite = swipp.GroundModelSuite(gm, "test")
        for tk, vs, vp, rh in zip(tks[1:], vss[1:], vps[1:], rhs[1:]):
            gm = swipp.GroundModel(tk, vp, vs, rh)
            suite.append(gm, "test")
        calc_med_gm = suite.median(nbest=3)
        med_tks = [2., 5., 0.]
        med_vss = [100., 275., 300.]
        med_vps = [300., 700., 400.]
        med_rhs = [2200.]*3
        med_gm = swipp.GroundModel(med_tks, med_vps, med_vss, med_rhs)
        self.assertTrue(med_gm == calc_med_gm)

        tks = [[1, 2, 3, 0], [2, 4, 0], [5, 10, 0]]
        vss = [[100, 200, 200, 300], [150, 275, 315], [100, 300, 200]]
        vps = [[300, 500, 500, 300], [600, 700, 800], [300, 1000, 400]]
        rhs = [[2000]*4, [2300]*3, [2200]*3]

        gm = swipp.GroundModel(tks[0], vps[0], vss[0], rhs[0])
        suite = swipp.GroundModelSuite(gm, "test")
        for tk, vs, vp, rh in zip(tks[1:], vss[1:], vps[1:], rhs[1:]):
            gm = swipp.GroundModel(tk, vp, vs, rh)
            suite.append(gm, "test")
        calc_med_gm = suite.median(nbest=3)
        med_tks = [2., 5., 0.]
        med_vss = [100., 275., 300.]
        med_vps = [300., 700., 400.]
        med_rhs = [2200.]*3
        med_gm = swipp.GroundModel(med_tks, med_vps, med_vss, med_rhs)
        self.assertTrue(med_gm == calc_med_gm)

    def test_write_to_txt(self):
        tks = [[1, 2, 0], [2, 0], [5, 0], [1, 0]]
        vps = [[300, 400, 500], [300, 600], [600, 1000], [800, 1000]]
        vss = [[100, 200, 300], [200, 300], [300, 500], [400, 600]]
        rhs = [[2000]*3, [2000]*2, [2000]*2, [2000]*2]
        ids = ["1", "2", "3"]
        misfits = [1, 0.5, 0.3]

        gm = swipp.GroundModel(tks[0], vps[0], vss[0], rhs[0])
        suite = swipp.GroundModelSuite(gm, ids[0], misfits[0])
        for tk, vs, vp, rh, cid, ms in zip(tks[1:], vss[1:], vps[1:], rhs[1:], ids[1:], misfits[1:]):
            gm = swipp.GroundModel(tk, vp, vs, rh)
            suite.append(gm, cid, ms)

        fname = "text.txt"
        suite.write_to_txt(fname)

        mysuite = swipp.GroundModelSuite.from_geopsy(fname)
        for gm_a, gm_b in zip(suite.gms, mysuite.gms):
            self.assertEqual(gm_a, gm_b)
        os.remove(fname)


if __name__ == "__main__":
    unittest.main()
