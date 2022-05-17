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
import warnings

import numpy as np

from testtools import unittest, TestCase, get_path

import swprepost


class Test_TargetSet(TestCase):

    def setUp(self):
        self.path = get_path(__file__)

    def test_init(self):
        r0 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                   velocity=[100, 200, 300],
                                   velstd=[10, 20, 30],
                                   description=(("rayleigh", 0),))
        r1 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                   velocity=[200, 300, 400],
                                   velstd=[20, 30, 40],
                                   description=(("rayleigh", 1),))
        targets = [r0, r1]
        targetset = swprepost.TargetSet(targets)
        self.assertTrue(isinstance(targetset, swprepost.TargetSet))

    def test_to_and_from_target(self):
        for version in ["2.10.1", "3.4.2"]:
            # Fundamental and first-higher Rayleigh.
            r0 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                       velocity=[100, 200, 300],
                                       velstd=[10, 20, 30],
                                       description=(("rayleigh", 0),))
            r1 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                       velocity=[200, 300, 400],
                                       velstd=[20, 30, 40],
                                       description=(("rayleigh", 1),))
            targets = [r0, r1]
            expected = swprepost.TargetSet(targets)
            fname_prefix = "r0r1"
            fname = f"{fname_prefix}.target"
            try:
                # TODO (jpv): Remove catch_warnings >2.0.0
                # When replace to_target with to_file and
                # from_target with from_file.
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    expected.to_target(fname_prefix, version=version)
                    returned = swprepost.TargetSet.from_target(fname_prefix,
                                                               version=version)
                self.assertEqual(expected, returned)
            finally:
                os.remove(fname)

            # Fundamental Rayleigh and fundamental Love.
            r0 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                       velocity=[100, 200, 300],
                                       velstd=[10, 20, 30],
                                       description=(("rayleigh", 0),))
            l0 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                       velocity=[200, 300, 400],
                                       velstd=[20, 30, 40],
                                       description=(("love", 0),))
            targets = [r0, l0]
            expected = swprepost.TargetSet(targets)
            fname_prefix = "r0l0"
            fname = f"{fname_prefix}.target"
            try:
                # TODO (jpv): Remove catch_warnings >2.0.0
                # When replace to_target with to_file and
                # from_target with from_file.
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    expected.to_target(fname_prefix, version=version)
                    returned = swprepost.TargetSet.from_target(fname_prefix,
                                                               version=version)
                self.assertEqual(expected, returned)
            finally:
                os.remove(fname)

    def test_cut(self):
        r0 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                   velocity=[100, 200, 300],
                                   velstd=[10, 20, 30],
                                   description=(("rayleigh", 0),))
        r1 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                   velocity=[200, 300, 400],
                                   velstd=[20, 30, 40],
                                   description=(("rayleigh", 1),))
        targets = [r0, r1]
        targetset = swprepost.TargetSet(targets)
        targetset.cut(2, 8, domain="frequency")

        expected_r0 = swprepost.ModalTarget(frequency=[3],
                                            velocity=[200],
                                            velstd=[20],
                                            description=(("rayleigh", 0),))
        expected_r1 = swprepost.ModalTarget(frequency=[3],
                                            velocity=[300],
                                            velstd=[30],
                                            description=(("rayleigh", 1),))
        returned_r0, returned_r1 = targetset.targets
        self.assertEqual(returned_r0, expected_r0)
        self.assertEqual(returned_r1, expected_r1)

    def test_resample(self):
        r0 = swprepost.ModalTarget(frequency=np.linspace(1, 9, 10),
                                   velocity=np.linspace(100, 300, 10),
                                   velstd=np.linspace(10, 30, 10),
                                   description=(("rayleigh", 0),))
        r1 = swprepost.ModalTarget(frequency=np.linspace(1, 9, 10),
                                   velocity=np.linspace(200, 400, 10),
                                   velstd=np.linspace(20, 40, 10),
                                   description=(("rayleigh", 1),))
        targets = [r0, r1]
        targetset = swprepost.TargetSet(targets)

        for inplace in [True, False]:
            targetset = swprepost.TargetSet(targets)

            df = 2
            fs = np.arange(1, 9+df, df)
            if inplace:
                targetset._resample(fs, domain="frequency",
                                    inplace=inplace)
            else:
                targetset = targetset._resample(fs, domain="frequency",
                                                inplace=inplace)

            expected_r0 = swprepost.ModalTarget(frequency=fs,
                                                velocity=fs*25+75,
                                                velstd=fs*2.5+7.5,
                                                description=(("rayleigh", 0),))
            expected_r1 = swprepost.ModalTarget(frequency=fs,
                                                velocity=fs*25+175,
                                                velstd=fs*2.5+17.5,
                                                description=(("rayleigh", 1),))
            returned_r0, returned_r1 = targetset.targets

            self.assertEqual(returned_r0, expected_r0)
            self.assertEqual(returned_r1, expected_r1)

    def test_easy_resample(self):
        r0 = swprepost.ModalTarget(frequency=np.linspace(1, 9, 10),
                                   velocity=np.linspace(100, 300, 10),
                                   velstd=np.linspace(10, 30, 10),
                                   description=(("rayleigh", 0),))
        r1 = swprepost.ModalTarget(frequency=np.linspace(1, 9, 10),
                                   velocity=np.linspace(200, 400, 10),
                                   velstd=np.linspace(20, 40, 10),
                                   description=(("rayleigh", 1),))
        targets = [r0, r1]
        targetset = swprepost.TargetSet(targets)

        for inplace in [True, False]:
            targetset = swprepost.TargetSet(targets)

            if inplace:
                targetset.easy_resample(1, 9, 5,
                                        res_type="linear",
                                        domain="frequency",
                                        inplace=inplace)
            else:
                targetset = targetset.easy_resample(1, 9, 5,
                                                    res_type="linear",
                                                    domain="frequency",
                                                    inplace=inplace)

            df = 2
            fs = np.arange(1, 9+df, df)
            expected_r0 = swprepost.ModalTarget(frequency=fs,
                                                velocity=fs*25+75,
                                                velstd=fs*2.5+7.5,
                                                description=(("rayleigh", 0),))
            expected_r1 = swprepost.ModalTarget(frequency=fs,
                                                velocity=fs*25+175,
                                                velstd=fs*2.5+17.5,
                                                description=(("rayleigh", 1),))
            returned_r0, returned_r1 = targetset.targets

            # print(expected_r0.__repr__())
            # print(returned_r0.__repr__())
            # print(expected_r1.__repr__())
            # print(returned_r1.__repr__())

            self.assertEqual(returned_r0, expected_r0)
            self.assertEqual(returned_r1, expected_r1)

    def test_eq(self):
        r0 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                   velocity=[100, 200, 300],
                                   velstd=[10, 20, 30],
                                   description=(("rayleigh", 0),))
        r1 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                   velocity=[200, 300, 400],
                                   velstd=[20, 30, 40],
                                   description=(("rayleigh", 1),))
        l0 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                   velocity=[100, 200, 300],
                                   velstd=[10, 20, 30],
                                   description=(("love", 0),))
        l1 = swprepost.ModalTarget(frequency=[1, 3, 10],
                                   velocity=[200, 300, 400],
                                   velstd=[20, 30, 40],
                                   description=(("love", 1),))

        r0_set = swprepost.TargetSet([r0])
        r1_set = swprepost.TargetSet([r1])
        l0_set = swprepost.TargetSet([l0])
        l1_set = swprepost.TargetSet([l1])
        r0r1_set = swprepost.TargetSet([r0, r1])
        l0l1_set = swprepost.TargetSet([l0, l1])

        self.assertEqual(r0_set, r0_set)
        self.assertEqual(r0r1_set, r0r1_set)
        self.assertEqual(l0l1_set, l0l1_set)

        self.assertNotEqual(r0_set, r1_set)
        self.assertNotEqual(r0_set, l0_set)
        self.assertNotEqual(r1_set, l1_set)
        self.assertNotEqual(l0_set, l1_set)
        self.assertNotEqual(r0r1_set, r0_set)
        self.assertNotEqual(r0r1_set, l0l1_set)
        self.assertNotEqual(r0_set, "target")

    def test_str(self):
        r0 = swprepost.ModalTarget(frequency=np.linspace(1, 9, 10),
                                   velocity=np.linspace(100, 300, 10),
                                   velstd=np.linspace(10, 30, 10),
                                   description=(("rayleigh", 0),))
        r1 = swprepost.ModalTarget(frequency=np.linspace(1, 9, 10),
                                   velocity=np.linspace(200, 400, 10),
                                   velstd=np.linspace(20, 40, 10),
                                   description=(("rayleigh", 1),))
        targets = [r0, r1]
        targetset = swprepost.TargetSet(targets)

        expected = "TargetSet with 2 targets."
        returned = targetset.__str__()
        self.assertEqual(returned, expected)

    def test_repr(self):
        r0 = swprepost.ModalTarget(frequency=np.linspace(1, 9, 10),
                                   velocity=np.linspace(100, 300, 10),
                                   velstd=np.linspace(10, 30, 10),
                                   description=(("rayleigh", 0),))
        r1 = swprepost.ModalTarget(frequency=np.linspace(1, 9, 10),
                                   velocity=np.linspace(200, 400, 10),
                                   velstd=np.linspace(20, 40, 10),
                                   description=(("rayleigh", 1),))
        targets = [r0, r1]
        targetset = swprepost.TargetSet(targets)

        expected = ""
        for target in targetset.targets:
            expected += f"{target.__repr__()}\n"
        returned = targetset.__repr__()
        self.assertEqual(returned, expected)


if __name__ == '__main__':
    unittest.main()
