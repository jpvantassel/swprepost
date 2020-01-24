"""Tests for GroundModelSuite class."""

from testtools import unittest, TestCase, get_full_path
import os
import numpy as np
import swipp
import logging
logging.basicConfig(level=logging.INFO)


class Test_GroundModelSuite(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_init(self):
        # One GroundModel
        thk = [1, 3, 5, 7]
        vss = [100, 200, 300, 400]
        vps = [200, 400, 600, 800]
        rho = [2000, 2000, 2000, 2000]
        mygm = swipp.GroundModel(thk, vps, vss, rho)
        mysuite = swipp.GroundModelSuite(mygm, "test", misfit=2)
        self.assertEqual(mygm, mysuite[0])
        self.assertEqual("test", mysuite.ids[0])
        self.assertEqual(2, mysuite.misfits[0])

    def test_append(self):
        thk = [1, 3, 5, 7]
        vss = [100, 200, 300, 400]
        vps = [200, 400, 600, 800]
        rho = [2000, 2000, 2000, 2000]
        mygm = swipp.GroundModel(thk, vps, vss, rho)

        # Two GroundModels
        mysuite = swipp.GroundModelSuite(mygm, "test1", misfit=1)
        mysuite.append(mygm, "test2", misfit=1.1)
        for gm in mysuite:
            self.assertEqual(mygm, gm)
        self.assertListEqual(["test1", "test2"], mysuite.ids)
        self.assertListEqual([1.0, 1.1], mysuite.misfits)

    def test_from_geopsy(self):
        # Single Model
        tk = [0.68, 9.69, 0.018, 22.8, 43.9, 576.4, 0]
        vp = [196.7, 295.8, 1600.2, 1600.2, 1600.2, 4232.5, 4232.5]
        vs = [120.3, 120.3, 120., 231.9, 840.9, 840.9, 2095.3]
        rh = [2000.]*7
        expected = swipp.GroundModel(thickness=tk, vp=vp, vs=vs, density=rh)

        fname = self.full_path+"data/test_gm_mod1.txt"
        returned = swipp.GroundModelSuite.from_geopsy(fname=fname)[0]
        self.assertEqual(expected, returned)

        # Two Models
        tk1 = [0.7, 9.1, 0.1, 21.9, 61.0, 571.8, 0]
        vp1 = [196.7, 281.4, 1392.1, 1392.1, 1392.1, 4149.1, 4149.1]
        vs1 = [120.3, 120.3, 120.3, 225.1, 840.9, 840.9, 2202.1]
        rh1 = [2000.]*7
        expected1 = swipp.GroundModel(thickness=tk1, vp=vp1, vs=vs1,
                                      density=rh1)

        fname = self.full_path+"data/test_gm_mod2.txt"
        returned = swipp.GroundModelSuite.from_geopsy(fname=fname)
        self.assertEqual(expected, returned[0])
        self.assertEqual(expected1, returned[1])

        self.assertListEqual([0.766485, 0.767484], returned.misfits)
        self.assertListEqual(["149698", "147185"], returned.ids)

        # Randomly check the 10th profile (index=9)
        fname = self.full_path+"data/test_gm_mod100.txt"
        suite = swipp.GroundModelSuite.from_geopsy(fname=fname)

        tk = [0.77397930357999966677,
              9.4057659375340758601,
              0.10720244308314619275,
              22.132593746915929955,
              27.312477738315664055,
              586.97428362212974662,
              0]
        vp = [196.72222021325231367,
              307.83304440876798935,
              1492.6139621303491367,
              1492.6139621303491367,
              1492.6139621303491367,
              4149.1243500998343734,
              4149.1243500998343734]
        vs = [120.30018967392834384,
              120.30018967392834384,
              120.30018967392834384,
              227.42292146971948341,
              832.63107566976702856,
              832.63107566976702856,
              2116.2608747684203081]
        rh = [2000]*7
        expected_9 = swipp.GroundModel(thickness=tk, vp=vp, vs=vs, density=rh)
        self.assertEqual(expected_9, suite[9])

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
