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

"""Tests for Suite."""

import logging
import warnings

import swprepost
from testtools import unittest, TestCase

logging.basicConfig(level=logging.ERROR)


class Test_Suite(TestCase):

    @classmethod
    def setUpClass(self):
        # GroundModelSuite
        tk = [1, 2, 3]
        vs = [100, 200, 300]
        vp = [200, 400, 600]
        rh = [2000]*3
        gms = []
        for _id, _mf in enumerate([0.5, 0.8, 1, 0.3, 0.4, 0.6, 0.7, 0.1, 0.2, 0.1]):
            gms.append(swprepost.GroundModel(tk, vp, vs, rh,
                                             identifier=_id, misfit=_mf))
        self.gm_suite = swprepost.GroundModelSuite.from_list(gms)

    def test_handle_nbest(self):
        # GroundModelSuite
        for nbest, expected in zip([None, "all", 4, 12], [10, 10, 4, 10]):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                returned = self.gm_suite._handle_nbest(nbest)
            self.assertEqual(expected, returned)

        # Bad value
        self.assertRaises(ValueError, self.gm_suite._handle_nbest,
                          nbest="tada")

    def test_misfit_range(self):
        # GroundModelSuite
        for nmodels, expected in zip(["all", 1, 5], [(0.1, 1), 0.1, (0.1, 0.4)]):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                returned = self.gm_suite.misfit_range(nmodels)
            self.assertEqual(expected, returned)

    def test_misfit_repr(self):
        # GroundModelSuite
        for nmodels, expected in zip(["all", 1, 5], ["[0.10-1.00]", "[0.10]", "[0.10-0.40]"]):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                returned = self.gm_suite.misfit_repr(nmodels)
            self.assertEqual(expected, returned)

        # GroundModelSuite - with custom kwargs
        custom_kwargs = dict(unique=True)
        for nmodels, expected in zip(["all", 1, 5], ["[0.1-1.]", "[0.1]", "[0.1-0.4]"]):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                returned = self.gm_suite.misfit_repr(nmodels, **custom_kwargs)
            self.assertEqual(expected, returned)


if __name__ == "__main__":
    unittest.main()
