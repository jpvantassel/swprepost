# This file is part of swprepost, a Python package for surface wave
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

"""Tests for the TargetSet class."""

import os

from testtools import unittest, TestCase, get_full_path

import swprepost

class Test_Target(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_init(self):
        r0 = swprepost.ModalTarget(frequency=[1, 3, 10], velocity=[100, 200, 300], velstd=[10, 20, 30], type="rayleigh", mode=(0,))
        r1 = swprepost.ModalTarget(frequency=[1, 3, 10], velocity=[200, 300, 400], velstd=[20, 30, 40], type="rayleigh", mode=(1,))
        targets = [r0, r1]
        targetset = swprepost.TargetSet(targets)
        self.assertTrue(isinstance(targetset, swprepost.TargetSet))

    def test_to_target(self):
        for version in ["2", "3"]:
            # v2
            r0 = swprepost.ModalTarget(frequency=[1, 3, 10], velocity=[100, 200, 300], velstd=[10, 20, 30], type="rayleigh", mode=(0,))
            r1 = swprepost.ModalTarget(frequency=[1, 3, 10], velocity=[200, 300, 400], velstd=[20, 30, 40], type="rayleigh", mode=(1,))
            targets = [r0, r1]
            targetset = swprepost.TargetSet(targets)
            fname_prefix = "r0r1"
            fname = f"{fname_prefix}.target"
            try:
                targetset.to_target(fname_prefix, version=version)
                self.assertTrue(os.path.exists(fname))
            finally:
                # pass
                os.remove(fname)

            r0 = swprepost.ModalTarget(frequency=[1, 3, 10], velocity=[100, 200, 300], velstd=[10, 20, 30], type="rayleigh", mode=(0,))
            l0 = swprepost.ModalTarget(frequency=[1, 3, 10], velocity=[200, 300, 400], velstd=[20, 30, 40], type="love", mode=(0,))
            targets = [r0, l0]
            targetset = swprepost.TargetSet(targets)
            fname_prefix = "r0l0"
            fname = f"{fname_prefix}.target"
            try:
                targetset.to_target(fname_prefix, version=version)
                self.assertTrue(os.path.exists(fname))
            finally:
                # pass
                os.remove(fname)

if __name__ == '__main__':
    unittest.main()
