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

"""Tests for GroundModelSuite class."""

import os
import logging

import numpy as np

import swprepost
from testtools import unittest, TestCase, get_full_path

logging.basicConfig(level=logging.ERROR)


class Test_GroundModelSuite(TestCase):

    @classmethod
    def setUpClass(cls):

        def make_gm(v, gm_dict):
            for key, value in gm_dict.items():
                setattr(cls, key+v, value)
            setattr(cls, "gm"+v, swprepost.GroundModel(*[gm_dict[attr] for attr in ["tk", "vp", "vs", "rh"]],
                                                   **{key: gm_dict[attr] for key, attr in zip(["identifier", "misfit"], ["id", "mf"])}))

        v = "_0"
        tk = [1, 3, 5, 0]
        vp = [200, 400, 600, 800]
        vs = [100, 200, 300, 400]
        rh = [1900, 2000, 2100, 2200]
        _id = 0
        mf = 1.0
        make_gm(v, dict(tk=tk, vp=vp, vs=vs, rh=rh, id=_id, mf=mf))

        v = "_1"
        tk = [2, 4, 3, 0]
        vp = [352, 500, 500, 600]
        vs = [150, 250, 250, 300]
        rh = [1900, 2000, 2150, 2200]
        _id = 5
        mf = 1.3
        make_gm(v, dict(tk=tk, vp=vp, vs=vs, rh=rh, id=_id, mf=mf))

        cls.suite = swprepost.GroundModelSuite(cls.gm_0)
        cls.suite.append(cls.gm_1)

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_init(self):
        # One GroundModel
        gm = swprepost.GroundModel(self.tk_0, self.vp_0, self.vs_0, self.rh_0,
                               identifier=self.id_0, misfit=self.mf_0)
        returned = swprepost.GroundModelSuite(gm)
        expected = swprepost.GroundModelSuite(self.gm_0)
        self.assertEqual(expected, returned)

        # Bad Value - Wrong Type
        gm = ["GroundModel"]
        self.assertRaises(TypeError, swprepost.GroundModelSuite, gm)

    def test_append(self):
        # Two GroundModels
        returned = swprepost.GroundModelSuite(self.gm_0)
        returned.append(self.gm_1)
        self.assertEqual(self.suite, returned)

    def test_from_geopsy(self):
        # Single Model
        tk = [0.68, 9.69, 0.018, 22.8, 43.9, 576.4, 0]
        vp = [196.7, 295.8, 1600.2, 1600.2, 1600.2, 4232.5, 4232.5]
        vs = [120.3, 120.3, 120., 231.9, 840.9, 840.9, 2095.3]
        rh = [2000.]*7
        _id = 149698
        mf = 0.766485
        expected_0 = swprepost.GroundModel(thickness=tk, vp=vp, vs=vs, density=rh,
                                       identifier=_id, misfit=mf)

        fname = self.full_path+"data/test_gm_mod1.txt"
        returned_0 = swprepost.GroundModelSuite.from_geopsy(fname=fname)[0]
        self.assertEqual(expected_0, returned_0)

        # Two Models
        tk1 = [0.7, 9.1, 0.1, 21.9, 61.0, 571.8, 0]
        vp1 = [196.7, 281.4, 1392.1, 1392.1, 1392.1, 4149.1, 4149.1]
        vs1 = [120.3, 120.3, 120.3, 225.1, 840.9, 840.9, 2202.1]
        rh1 = [2000.]*7
        _id = 147185
        mf = 0.767484
        expected_1 = swprepost.GroundModel(thickness=tk1, vp=vp1,
                                       vs=vs1, density=rh1, identifier=_id,
                                       misfit=mf)

        fname = self.full_path+"data/test_gm_mod2.txt"
        returned_1 = swprepost.GroundModelSuite.from_geopsy(fname=fname)
        self.assertEqual(expected_0, returned_1[0])
        self.assertEqual(expected_1, returned_1[1])

        # Randomly check the 10th profile (index=9)
        fname = self.full_path+"data/test_gm_mod100.txt"
        suite = swprepost.GroundModelSuite.from_geopsy(fname=fname, nmodels=10)

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
        _id = 149535
        mf = 0.770783
        expected_9 = swprepost.GroundModel(thickness=tk, vp=vp, vs=vs, density=rh,
                                       identifier=_id, misfit=mf)
        self.assertEqual(expected_9, suite[9])

    def test_vs30(self):
        # nbest="all"
        thk = [5, 20, 0]
        vps = [300, 600, 800]
        vss = [150, 300, 400]
        rho = [2000]*3
        gm = swprepost.GroundModel(thk, vps, vss, rho)
        suite = swprepost.GroundModelSuite(gm)
        for _ in range(5):
            suite.append(gm)
        self.assertListEqual(suite.vs30(), [266.6666666666666666666]*6)

        # nbest=3
        self.assertListEqual(suite.vs30(nbest=3), [
                             266.6666666666666666666]*3)

    def test_median(self):
        tks = [[1, 5, 0], [2, 4, 0], [5, 10, 0]]
        vss = [[100, 200, 300], [150, 275, 315], [100, 300, 200]]
        vps = [[300, 500, 350], [600, 700, 800], [300, 1000, 400]]
        rhs = [[2000]*3, [2300]*3, [2200]*3]

        gm = swprepost.GroundModel(tks[0], vps[0], vss[0], rhs[0])
        suite = swprepost.GroundModelSuite(gm)
        for tk, vs, vp, rh in zip(tks[1:], vss[1:], vps[1:], rhs[1:]):
            gm = swprepost.GroundModel(tk, vp, vs, rh)
            suite.append(gm)
        calc_med_gm = suite.median(nbest=3)
        med_tks = [2., 5., 0.]
        med_vss = [100., 275., 300.]
        med_vps = [300., 700., 400.]
        med_rhs = [2200.]*3
        med_gm = swprepost.GroundModel(med_tks, med_vps, med_vss, med_rhs)
        self.assertTrue(med_gm == calc_med_gm)

        tks = [[1, 2, 3, 0], [2, 4, 0], [5, 10, 0]]
        vss = [[100, 200, 200, 300], [150, 275, 315], [100, 300, 200]]
        vps = [[300, 500, 500, 350], [600, 700, 800], [300, 1000, 400]]
        rhs = [[2000]*4, [2300]*3, [2200]*3]

        gm = swprepost.GroundModel(tks[0], vps[0], vss[0], rhs[0])
        suite = swprepost.GroundModelSuite(gm)
        for tk, vs, vp, rh in zip(tks[1:], vss[1:], vps[1:], rhs[1:]):
            gm = swprepost.GroundModel(tk, vp, vs, rh)
            suite.append(gm)
        calc_med_gm = suite.median(nbest="all")
        med_tks = [2., 5., 0.]
        med_vss = [100., 275., 300.]
        med_vps = [300., 700., 400.]
        med_rhs = [2200.]*3
        med_gm = swprepost.GroundModel(med_tks, med_vps, med_vss, med_rhs)
        self.assertTrue(med_gm == calc_med_gm)

    def test_sigma_ln(self):
        tk = [1, 5, 0]
        vss = [[100, 200, 300], [150, 275, 315], [100, 300, 200]]
        vp = [200, 400, 600]
        rh = [2000]*3

        gm = swprepost.GroundModel(tk, vp, vss[0], rh)
        suite = swprepost.GroundModelSuite(gm)
        for vs in vss[1:]:
            gm = swprepost.GroundModel(tk, vp, vs, rh)
            suite.append(gm)
        dmax = 10
        dy = 0.5
        depth, sigln = suite.sigma_ln(nbest=3, dmax=dmax, dy=dy,
                                      parameter='vs')
        self.assertListEqual(depth, list(np.arange(0, dmax+dy, dy)))
        self.assertListEqual(sigln, ([np.std(np.log([100, 150, 100]), ddof=1)]*3 +
                                     [np.std(np.log([200, 275, 300]), ddof=1)]*10 +
                                     [np.std(np.log([300, 315, 200]), ddof=1)]*8))

    def test_from_array(self):
        tks = np.array([[1, 2, 3], [0, 0, 0]])
        vps = np.array([[100, 200, 300], [200, 400, 600]])
        vss = np.array([[50, 75, 100], [100, 200, 300]])
        rhs = np.array([[2000, 2200, 2250], [2100, 2300, 2300]])
        misfits = np.array([1., 2., 3.])
        ids = np.array([2, 7, 9])

        gms = []
        for col in range(tks.shape[1]):
            gm = swprepost.GroundModel(tks[:, col], vps[:, col],
                                   vss[:, col], rhs[:, col],
                                   identifier=ids[col],
                                   misfit=misfits[col])
            gms.append(gm)

        suite = swprepost.GroundModelSuite.from_array(tks, vps, vss, rhs,
                                                  ids, misfits)

        for expected, returned in zip(gms, suite):
            self.assertEqual(expected, returned)

        self.assertListEqual(misfits.tolist(), suite.misfits)
        self.assertListEqual(ids.tolist(), suite.identifiers)

    def test_write_to_txt(self):
        tks = [[1, 2, 0], [2, 0], [5, 0], [1, 0]]
        vps = [[300, 400, 500], [300, 600], [600, 1000], [800, 1000]]
        vss = [[100, 200, 300], [200, 300], [300, 500], [400, 600]]
        rhs = [[2000]*3, [2000]*2, [2000]*2, [2000]*2]
        ids = [1, 2, 3]
        misfits = [1, 0.5, 0.3]

        gm = swprepost.GroundModel(tks[0], vps[0], vss[0], rhs[0],
                               identifier=ids[0], misfit=misfits[0])
        suite = swprepost.GroundModelSuite(gm)
        for tk, vs, vp, rh, cid, ms in zip(tks[1:], vss[1:], vps[1:], rhs[1:], ids[1:], misfits[1:]):
            gm = swprepost.GroundModel(tk, vp, vs, rh, identifier=cid, misfit=ms)
            suite.append(gm)

        fname = "text.txt"
        suite.write_to_txt(fname)

        mysuite = swprepost.GroundModelSuite.from_geopsy(fname)
        for gm_a, gm_b in zip(suite.gms, mysuite.gms):
            self.assertEqual(gm_a, gm_b)
        os.remove(fname)

    def test_str(self):
        x = [1, 2, 3]
        y = [2, 4, 5]
        gm = swprepost.GroundModel(x, y, x, x)
        suite = swprepost.GroundModelSuite(gm)
        for _ in range(3):
            suite.append(gm)
        expected = "GroundModelSuite with 4 GroundModels."
        returned = suite.__str__()
        self.assertEqual(expected, returned)

        # TODO (jpv): Add a more serious test for slice get_item
        suite = suite[1:3]
        expected = "GroundModelSuite with 2 GroundModels."
        returned = suite.__str__()
        self.assertEqual(expected, returned)


if __name__ == "__main__":
    unittest.main()
