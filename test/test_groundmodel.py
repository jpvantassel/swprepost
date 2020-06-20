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

"""Tests for GroundModel class."""

import os
import logging

from scipy.io import loadmat
from hypothesis import given, settings
import hypothesis.strategies as st
import numpy as np

import swprepost
from testtools import unittest, TestCase, get_full_path

logging.basicConfig(level=logging.WARN)


class Test_GroundModel(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_init(self):
        # List
        thk = [1, 5, 3.3, 10]
        vps = [300, 450, 1500.1, 2000.1]
        vss = [100, 150, 201., 300]
        rho = [2000, 3000, 2250., 2300.]
        mygm = swprepost.GroundModel(thickness=thk, vp=vps, vs=vss, density=rho)

        self.assertListEqual(mygm.tk, thk)
        self.assertListEqual(mygm.vp, vps)
        self.assertListEqual(mygm.vs, vss)
        self.assertListEqual(mygm.rh, rho)

        # ndarray
        thk = np.array([1, 5, 3.3, 10])
        vps = np.array([300, 450, 1500.1, 2000.1])
        vss = np.array([100, 150, 201., 300])
        rho = np.array([2000, 3000, 2250., 2300.])
        mygm = swprepost.GroundModel(thickness=thk, vp=vps, vs=vss, density=rho)

        self.assertListEqual(thk.tolist(), mygm.tk)
        self.assertListEqual(vps.tolist(), mygm.vp)
        self.assertListEqual(vss.tolist(), mygm.vs)
        self.assertListEqual(rho.tolist(), mygm.rh)

        # Bad Type
        x = ["this", "that", "these", "those"]
        self.assertRaises(TypeError, swprepost.GroundModel, x, x, x, x)

        # Bad Value - Less than zero
        x = [-1]*3
        self.assertRaises(ValueError, swprepost.GroundModel, x, x, x, x)

        # Bad Value - Length
        x = [1]*3
        y = [1]*4
        self.assertRaises(ValueError, swprepost.GroundModel, x, x, x, y)

        # Bad Value - Vp < Vs
        tk = [1]*2
        vp = [100, 200]
        vs = [200, 300]
        rh = [2000]*2
        self.assertRaises(ValueError, swprepost.GroundModel, tk, vp, vs, rh)

    def test_gm2(self):
        # Simple Test
        tk1 = [5, 0]
        vp1 = [200, 250]
        vs1 = [100, 125]
        rh1 = [2000]*2
        mygm = swprepost.GroundModel(thickness=tk1, vp=vp1, vs=vs1, density=rh1)
        self.assertListEqual([0, 5, 5, 9999.0], mygm.depth)
        self.assertListEqual([200, 200, 250, 250], mygm.vp2)
        self.assertListEqual([100, 100, 125, 125], mygm.vs2)
        self.assertListEqual([2000]*4, mygm.rh2)

        # Setup
        thks = [1, 3, 5, 7, 0]
        vss = [100, 300, 500, 700, 900]
        vps = [200, 600, 1000, 1400, 1800]
        rho = [2000]*5
        mygm = swprepost.GroundModel(thks, vps, vss, rho)
        depth2 = mygm.gm2(parameter="depth")
        vp2 = mygm.gm2(parameter="vp")
        vs2 = mygm.gm2(parameter="vs")
        rho2 = mygm.gm2(parameter="rh")

        # True
        depth2_true = [0, 1, 1, 4, 4, 9, 9, 16, 16, 9999.]
        vs2_true = [100, 100, 300, 300, 500, 500, 700, 700, 900, 900]
        vp2_true = [200, 200, 600, 600, 1000, 1000, 1400, 1400, 1800, 1800]
        rho2_true = rho+rho

        # Different way to get to the same value
        deptha = mygm.depth
        vp2a = mygm.vp2
        vs2a = mygm.vs2
        rho2a = mygm.rh2

        # Check two lists are indeed the same
        self.assertListEqual(depth2, deptha)
        self.assertListEqual(vp2, vp2a)
        self.assertListEqual(vs2, vs2a)
        self.assertListEqual(rho2, rho2a)

        # Go value by value
        returned_vals = [depth2, vp2, vs2, rho2]
        expected_vals = [depth2_true, vp2_true, vs2_true, rho2_true]
        for expected, returned in zip(expected_vals, returned_vals):
            self.assertListAlmostEqual(expected, returned)

        # Check Poisson's Ratio
        returned = mygm.pr2
        expected = swprepost.GroundModel.calc_pr(vp2, vs2)
        self.assertListEqual(expected, returned)

    def test_calcpr(self):
        # "Good" inputs.
        vp = [6000, 5000, 4000, 3000, 2000, 1000, 500, 400, 300, 200]
        vs = [100, 200, 300, 500, 750, 500, 300, 120, 210, 110]
        trials = swprepost.GroundModel.calc_pr(vp=vp, vs=vs)

        trues = [0.499861072520145, 0.499198717948718,
                 0.49717159, 0.485714285714286, 0.418181818181818,
                 0.333333333333333, 0.21875, 0.450549450549451,
                 0.0196078431372549, 0.283154121863799]
        for trial, true in zip(trials, trues):
            self.assertAlmostEqual(trial, true)

        # Single Value
        vp = 300
        vs = 150
        self.assertEqual(1/3, swprepost.GroundModel.calc_pr(vp, vs))

        # "Bad" inputs.
        vps = [150, 150, 150]
        vss = [151, 150, 149]
        for vp, vs in zip(vps, vss):
            self.assertRaises(ValueError, swprepost.GroundModel.calc_pr, vp, vs)

    def test_properties(self):
        tk = [1,2,0]
        vp = [100,200,300]
        vs = [50,100,150]
        rh = [2000]*3
        gm = swprepost.GroundModel(tk, vp, vs, rh)

        self.assertListEqual(tk, gm.thickness)
        self.assertListEqual(vp, gm.vp)
        self.assertListEqual(vs, gm.vs)
        self.assertListEqual(rh, gm.density)

    def test_vs30(self):
        # One thick layer
        thick = [50, 0]
        vp = [600]*len(thick)
        vs = [100, 100]
        density = [0]*len(thick)
        test_val = swprepost.GroundModel(thick, vp, vs, density).vs30
        know_val = 100
        self.assertEqual(test_val, know_val)

        # Two layers, same velocity
        thick = [15, 15, 0]
        vp = [600]*len(thick)
        vs = [100, 100, 0]
        density = [0]*len(thick)
        test_val = swprepost.GroundModel(thick, vp, vs, density).vs30
        know_val = 100
        self.assertEqual(test_val, know_val)

        # One layer, exactly 30m
        thick = [30, 0]
        vp = [600]*len(thick)
        vs = [100, 200]
        density = [0]*len(thick)
        test_val = swprepost.GroundModel(thick, vp, vs, density).vs30
        know_val = 100
        self.assertEqual(test_val, know_val)

        # Two layers, exactly 30m
        thick = [15, 15, 0]
        vp = [600]*len(thick)
        vs = [100, 200, 300]
        density = [0]*len(thick)
        test_val = swprepost.GroundModel(thick, vp, vs, density).vs30
        know_val = 133.33
        self.assertAlmostEqual(test_val, know_val, places=2)

        # Two layers, less than 30m
        thick = [5, 10, 0]
        vp = [600]*len(thick)
        vs = [100, 200, 300]
        density = [0]*len(thick)
        test_val = swprepost.GroundModel(thick, vp, vs, density).vs30
        know_val = 200.
        self.assertAlmostEqual(test_val, know_val, places=2)

        # Two layers, less than 30m, with velocity reversal
        thick = [10, 10, 0]
        vp = [600]*len(thick)
        vs = [200, 50, 300]
        density = [0]*len(thick)
        test_val = swprepost.GroundModel(thick, vp, vs, density).vs30
        know_val = 105.88
        self.assertAlmostEqual(test_val, know_val, places=2)

    def test_write_to_mat(self):
        thick = [5., 5., 10., 10., 50., 0.]
        vp = [1500.]*len(thick)
        vs = [100., 200., 300., 400., 500., 600.]
        density = [2000.]*len(thick)
        mygm = swprepost.GroundModel(thick, vp, vs, density)
        fname = "test"
        mygm.write_to_mat(fname)
        data = loadmat(fname)
        self.assertListEqual(data["thickness"].tolist()[0], thick)
        self.assertListEqual(data["vp1"].tolist()[0], vp)
        self.assertListEqual(data["vs1"].tolist()[0], vs)
        self.assertListEqual(data["rho1"].tolist()[0], density)
        os.remove(f"{fname}.mat")

    def test_discretize(self):
        thick = [2., 2., 0.]
        vp = [1500.]*len(thick)
        vs = [100., 200., 300.]
        density = [2000.]*len(thick)
        mygm = swprepost.GroundModel(thick, vp, vs, density)
        disc_depth, disc_par = mygm.discretize(5, dy=1.25)
        self.assertListEqual([0., 1.25, 2.5, 3.75, 5.], disc_depth)
        self.assertListEqual([100., 100., 200., 200., 300.], disc_par)

        thick = [2., 2., 0.]
        vp = [1500.]*len(thick)
        vs = [100., 200., 300.]
        density = [2000.]*len(thick)
        mygm = swprepost.GroundModel(thick, vp, vs, density)
        disc_depth, disc_par = mygm.discretize(5, dy=1)
        self.assertListEqual([0., 1., 2., 3., 4., 5.], disc_depth)
        self.assertListEqual([100., 100., 100., 200., 200., 300.], disc_par)

        thick = [1.5, 1.5, 0]
        vp = [1500.]*len(thick)
        vs = [100., 200., 300.]
        density = [2000.]*len(thick)
        mygm = swprepost.GroundModel(thick, vp, vs, density)
        disc_depth, disc_par = mygm.discretize(5, dy=1)
        self.assertListEqual([0., 1., 2., 3., 4., 5.], disc_depth)
        self.assertListEqual([100., 100., 200., 200., 300., 300.], disc_par)

        thick = [1, 1, 0]
        vp = [1500.]*len(thick)
        vs = [100., 200., 300.]
        density = [2000.]*len(thick)
        mygm = swprepost.GroundModel(thick, vp, vs, density)
        disc_depth, disc_par = mygm.discretize(3, dy=0.5)
        self.assertListEqual([0., 0.5, 1., 1.5, 2., 2.5, 3.], disc_depth)
        self.assertListEqual([100., 100., 100., 200., 200., 300., 300.],
                             disc_par)

        thick = [1, 1, 0]
        vp = [1500.]*len(thick)
        vs = [100., 200., 300.]
        density = [2000.]*len(thick)
        mygm = swprepost.GroundModel(thick, vp, vs, density)
        disc_depth, disc_par = mygm.discretize(3, dy=0.25)
        expected = [0., 0.25, 0.5, 0.75, 1., 1.25,
                    1.5, 1.75, 2., 2.25, 2.5, 2.75, 3.]
        self.assertListEqual(expected, disc_depth)
        expected = [100., 100., 100., 100., 100, 200.,
                    200., 200., 200., 300., 300., 300., 300.]
        self.assertListEqual(expected, disc_par)

        # Check pr
        thick = [0.75, 0]
        vp = [200, 400]
        vs = [100, 200]
        density = [2000]*2
        mygm = swprepost.GroundModel(thick, vp, vs, density)
        disc_depth, disc_par = mygm.discretize(1.5, dy=0.5, parameter="pr")
        self.assertListEqual([0., 0.5, 1., 1.5], disc_depth)
        self.assertListEqual([0.3333333333333333]*4, disc_par)

        # Half-space
        tk = [0]
        vp = [1500]
        vs = [100]
        rh = [2000]
        gm = swprepost.GroundModel(tk, vp, vs, rh)
        disc_depth, disc_vs = gm.discretize(dmax=5, dy=1)
        expected = [0,1,2,3,4,5]
        self.assertListEqual(expected, disc_depth)
        expected = [100]*6
        self.assertListEqual(expected, disc_vs)

        # Fine discretization
        tk = [5.3, 12.5, 0]
        vp = [100, 200, 300]
        vs = [50, 100, 150]
        rh = [2000]*3
        gm = swprepost.GroundModel(tk, vp, vs, rh)
        disc_depth, disc_vs = gm.discretize(dmax=50, dy=0.01)
        expected = np.arange(0, int(50/0.01)+1, 1)*0.01
        self.assertListEqual(expected.tolist(), disc_depth)
        self.assertEqual(len(disc_depth), len(disc_vs))

    def test_validate_parameter(self):
        # Bad Values
        valid_parameters = ["vs", "vp", "density", "pr"]
        self.assertRaises(ValueError, swprepost.GroundModel._validate_parameter,
                          "hopscotch", valid_parameters)

    def test_depth_to_thick(self):
        depth = [0, 1, 3, 5, 8]
        thk = swprepost.GroundModel.depth_to_thick(depth)
        self.assertListEqual(thk, [1, 2, 2, 3, 0])

        depth = [0, 0.5, 1.1, 3.5, 5.5]
        thk = swprepost.GroundModel.depth_to_thick(depth)
        for test, known in zip(thk, [0.5, 0.6, 2.4, 2., 0]):
            self.assertAlmostEqual(test, known)

        # Bad Value
        depth = [1,2,3]
        self.assertRaises(ValueError, swprepost.GroundModel.depth_to_thick, depth)

    def test_from_geopsy(self):
        fname = self.full_path+"data/test_gm_mod1_self.txt"
        gm = swprepost.GroundModel.from_geopsy(fname)
        self.assertListEqual([2., 4., 0.], gm.tk)
        self.assertListEqual([300., 700., 400.], gm.vp)
        self.assertListEqual([100., 275., 300.], gm.vs)
        self.assertListEqual([2200.]*3, gm.rh)
        self.assertEqual(1, gm.identifier)
        self.assertEqual(0.0, gm.misfit)

    def test_write_to_txt(self):
        tk = [2, 4, 0]
        vp = [100, 200, 300]
        vs = [50, 100, 200]
        rh = [2000]*3
        expected = swprepost.GroundModel(tk, vp, vs, rh)
        fname = "test_write_to_txt"
        expected.write_to_txt(fname)
        returned = swprepost.GroundModel.from_geopsy(fname)
        self.assertEqual(expected, returned)
        os.remove(fname)

    def test_write_model(self):
        tk = [2, 4, 0]
        vp = [100, 200, 300]
        vs = [50, 100, 200]
        rh = [2000]*3
        expected = swprepost.GroundModel(tk, vp, vs, rh)
        fname = "test_write_model"
        with open(fname, "w") as f:
            expected.write_model(f)
        returned = swprepost.GroundModel.from_geopsy(fname)
        self.assertEqual(expected, returned)
        os.remove(fname)

    def test_simplify(self):
        tk = [1, 3, 1, 5, 0]
        vp = [200, 200, 500, 500, 600]
        vs = [100, 100, 100, 300, 300]
        rh = [2000]*5

        mygm = swprepost.GroundModel(tk, vp, vs, rh)
        simp_tk, simp_vp = mygm.simplify(parameter='vp')
        self.assertListEqual(simp_tk, [4, 6, 0])
        self.assertListEqual(simp_vp, [200, 500, 600])

        simp_tk, simp_vs = mygm.simplify(parameter='vs')
        self.assertListEqual(simp_tk, [5, 0])
        self.assertListEqual(simp_vs, [100, 300])

        simp_tk, simp_rh = mygm.simplify(parameter='rh')
        self.assertListEqual(simp_tk, [0])
        self.assertListEqual(simp_rh, [2000])

    def test_from_simple_profiles(self):
        vp_tk = [0]
        vp = [500]
        vs_tk = [0]
        vs = [200]
        rh_tk = [0]
        rh = [2000]
        mygm = swprepost.GroundModel.from_simple_profiles(vp_tk, vp,
                                                      vs_tk, vs,
                                                      rh_tk, rh)
        self.assertListEqual(mygm.tk, [0])
        self.assertListEqual(mygm.vp, [500])
        self.assertListEqual(mygm.vs, [200])
        self.assertListEqual(mygm.rh, [2000])

        vp_tk = [4, 6, 0]
        vp = [200, 500, 600]
        vs_tk = [5, 0]
        vs = [100, 200]
        rh_tk = [0]
        rh = [2000]
        mygm = swprepost.GroundModel.from_simple_profiles(vp_tk, vp,
                                                      vs_tk, vs,
                                                      rh_tk, rh)
        self.assertListEqual(mygm.tk, [4, 1, 5, 0])
        self.assertListEqual(mygm.vp, [200, 500, 500, 600])
        self.assertListEqual(mygm.vs, [100, 100, 200, 200])
        self.assertListEqual(mygm.rh, [2000]*4)

        vp_tk = [4, 6, 0]
        vp = [250, 500, 600]
        vs_tk = [3, 2, 0]
        vs = [100, 200, 300]
        rh_tk = [0]
        rh = [2000]
        mygm = swprepost.GroundModel.from_simple_profiles(
            vp_tk, vp, vs_tk, vs, rh_tk, rh)
        self.assertListEqual(mygm.tk, [3, 1, 1, 5, 0])
        self.assertListEqual(mygm.vp, [250, 250, 500, 500, 600])
        self.assertListEqual(mygm.vs, [100, 200, 200, 300, 300])
        self.assertListEqual(mygm.rh, [2000]*5)

        vp_tk = [2, 4, 7, 1, 2, 0]
        vp = [100, 200, 300, 400, 500, 600]
        vs_tk = [1, 3, 5, 7, 2, 4, 6, 0]
        vs = [50, 75, 85, 100, 200, 300, 100, 200]
        rh_tk = [0]
        rh = [2000]
        mygm = swprepost.GroundModel.from_simple_profiles(vp_tk, vp,
                                                      vs_tk, vs,
                                                      rh_tk, rh)
        self.assertListEqual(mygm.tk, [1, 1, 2, 2, 3, 4, 1, 2, 2, 4, 6, 0])
        self.assertListEqual(mygm.vp,
                             [100, 100, 200, 200, 300, 300, 400, 500, 600, 600, 600, 600])
        self.assertListEqual(mygm.vs,
                             [50, 75, 75, 85, 85, 100, 100, 100, 200, 300, 100, 200])
        self.assertListEqual(mygm.rh, [2000]*12)

        vp_tk = [1, 1, 1, 1, 2, 0]
        vp = [1500, 1501, 1502, 1503, 1504, 1505]
        vs_tk = [1, 1, 1, 1, 1, 0]
        vs = [100, 101, 102, 103, 104, 105]
        rh_tk = [0]
        rh = [2000]
        mygm = swprepost.GroundModel.from_simple_profiles(vp_tk, vp,
                                                      vs_tk, vs,
                                                      rh_tk, rh)
        self.assertListEqual(mygm.tk, [1, 1, 1, 1, 1, 1, 0])
        self.assertListEqual(mygm.vp,
                             [1500, 1501, 1502, 1503, 1504, 1504, 1505])
        self.assertListEqual(mygm.vs, [100, 101, 102, 103, 104, 105, 105])
        self.assertListEqual(mygm.rh, [2000]*7)

        vp_tk = [1, 1, 1, 1, 1, 0]
        vp = [1500, 1501, 1502, 1503, 1504, 1505]
        vs_tk = [1, 1, 1, 1, 2, 0]
        vs = [100, 101, 102, 103, 104, 105]
        rh_tk = [0]
        rh = [2000]
        mygm = swprepost.GroundModel.from_simple_profiles(vp_tk, vp,
                                                      vs_tk, vs,
                                                      rh_tk, rh)
        self.assertListEqual(mygm.tk, [1, 1, 1, 1, 1, 1, 0])
        self.assertListEqual(mygm.vp,
                             [1500, 1501, 1502, 1503, 1504, 1505, 1505])
        self.assertListEqual(mygm.vs, [100, 101, 102, 103, 104, 104, 105])
        self.assertListEqual(mygm.rh, [2000]*7)

    def test_str_and_repr(self):
        tk = [1,2,0]
        vp = [100,200,300]
        vs = [50,100,150]
        rh = [2000]*3
        gm = swprepost.GroundModel(tk, vp, vs, rh)
        # str
        self.assertEqual(gm.txt_repr, gm.__str__())
        # repr
        expected = f"GroundModel(thickness={gm.tk}, vp={gm.vp}, vs={gm.vs}, density={gm.rh})"
        self.assertEqual(expected, gm.__repr__())

    def test_equal(self):
        tk = [1,2,0]
        vp = [100,200,300]
        vs = [50,100,150]
        rh = [2000]*3
        gm_a = swprepost.GroundModel(tk, vp, vs, rh)

        # Equal
        gm_b = swprepost.GroundModel(tk, vp, vs, rh)
        self.assertEqual(gm_a, gm_b)

        # Not Equal - Wrong Length
        x = [1,2]
        y = [2,4]
        gm_b = swprepost.GroundModel(x,y,x,x)
        self.assertNotEqual(gm_a, gm_b)

        # Not Equal - Wrong Value
        x = [1,2,3]
        y = [2,4,6]
        gm_b = swprepost.GroundModel(x,y,x,x)
        self.assertNotEqual(gm_a, gm_b)

class Test_FromSimple(unittest.TestCase):
    @settings(deadline=None)
    @given(st.lists(st.integers(min_value=1, max_value=999), min_size=1,),
           st.lists(st.integers(min_value=1500, max_value=6000),
                    min_size=1, unique=True),
           st.lists(st.integers(min_value=1, max_value=999), min_size=1),
           st.lists(st.integers(min_value=100, max_value=700),
                    min_size=1, unique=True),
           st.lists(st.integers(min_value=1, max_value=999), min_size=1),
           st.lists(st.integers(min_value=2000, max_value=3000), min_size=1, unique=True))
    def test_from_simple(self, vp_tk, vp, vs_tk, vs, rh_tk, rh):
        vp_len = min(len(vp_tk), len(vp))
        vp_tk = vp_tk[:vp_len][:-1]
        vp = vp[:vp_len]

        vs_len = min(len(vs_tk), len(vs))
        vs_tk = vs_tk[:vs_len][:-1]
        vs = vs[:vs_len]

        rh_len = min(len(rh_tk), len(rh))
        rh_tk = rh_tk[:rh_len][:-1]
        rh = rh[:rh_len]

        mygm = swprepost.GroundModel.from_simple_profiles(
            vp_tk+[0], vp, vs_tk+[0], vs, rh_tk+[0], rh)
        self.assertEqual(mygm.simplify(parameter='vp'), (vp_tk+[0], vp))
        self.assertEqual(mygm.simplify(parameter='vs'), (vs_tk+[0], vs))
        self.assertEqual(mygm.simplify(parameter='rh'), (rh_tk+[0], rh))


if __name__ == '__main__':
    unittest.main()
