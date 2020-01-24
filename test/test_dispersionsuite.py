"""Tests for `DispersionSuite` class."""

from testtools import unittest, TestCase, get_full_path
import swipp
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)


class Test_DispersionSuite(TestCase):

    def setUp(self):
        self.full_path = get_full_path(__file__)

    def test_check_input(self):
        # DispersionSuite to be instantiated with only a DispersionSet object.
        for test in [[1, 2, 3], (1, 2, 3), True, "DC"]:
            self.assertRaises(TypeError, swipp.DispersionSuite, test, "Test")

    def test_init(self):
        # Manual instantiation
        frequency = np.array([1, 2, 3])
        velocity = np.array([4, 5, 6])
        dc = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        dc_set = swipp.DispersionSet(identifier="Test", misfit=None,
                                     rayleigh={0: dc}, love=None)
        dc_suite = swipp.DispersionSuite(dispersionset=dc_set)
        
        # Compare the Result
        expected = frequency
        returned = dc_suite[0].rayleigh[0].frequency
        self.assertArrayEqual(expected, returned)
        
        expected = velocity
        returned = dc_suite[0].rayleigh[0].velocity
        self.assertArrayEqual(expected, returned)
        
    def test_append(self):
        # Manual instantiation
        frequency = np.array([1, 2, 3])
        velocity = np.array([4, 5, 6])
        dc = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        dc_set_0 = swipp.DispersionSet(identifier="Test_0", misfit=None,
                                     rayleigh={0: dc}, love=None)
        dc_suite = swipp.DispersionSuite(dispersionset=dc_set_0)

        # Manual Append
        dc_set_1 = swipp.DispersionSet(identifier="Test_1", misfit=None,
                                     rayleigh={0: dc}, love=None)
        dc_suite.append(dispersionset=dc_set_1)

        # Compare the Result
        for dc_set in dc_suite:
            self.assertArrayEqual(frequency, dc_set.rayleigh[0].frequency)
            self.assertArrayEqual(velocity, dc_set.rayleigh[0].velocity)
        self.assertListEqual(["Test_0", "Test_1"], dc_suite.ids)
        self.assertListEqual([None, None], dc_suite.misfits)

    def test_from_geopsy(self):

        def compare(fname, models, **kwargs):
            dc_suite = swipp.DispersionSuite.from_geopsy(fname=fname, **kwargs)

            for model in models:
                # Use identifier to select the appropriate DispersionSet
                set_id = dc_suite.ids.index(model["identifier"])
                dc_set = dc_suite[set_id]

                # Single-valued Attributes
                for attr in ["misfit", "identifier"]:
                    self.assertEqual(model[attr], getattr(dc_set, attr))

                # Multi-valued Attributes
                for wave in ["rayleigh", "love"]:
                    if model[wave] is None:
                        continue
                    for mode_number in model[wave]:
                        for attr in model[wave][mode_number]:
                            expected = np.array(model[wave][mode_number][attr])
                            returned = getattr(getattr(dc_set, wave)[
                                               mode_number], attr)
                            self.assertArrayAlmostEqual(expected, returned, places=10)

        # One Set with Two Rayleigh and Two Love Modes
        fname = self.full_path+"data/test_dc_mod1_ray2_lov2_shrt.txt"
        e1 = {"identifier": "149641",
              "misfit": 1.08851,
              "love": {0: {"frequency": [0.11, 61],
                           "velocity": [1/0.0003055565316784,
                                        1/0.00838314255586564]},
                       1: {"frequency": [0.920128309893243, 69],
                           "velocity":  [1/0.000305221889470528,
                                         1/0.00828240730448549]}},
              "rayleigh": {0: {"frequency": [0.15, 64],
                               "velocity": [1/0.000334532972901842,
                                            1/0.00917746839997367]},
                           1: {"frequency": [0.479030947360446, 68],
                               "velocity":  [1/0.000323646256288129,
                                             1/0.00832719612771301]}}}
        models = [e1]
        compare(fname, models)

        # Two Sets with Two Rayleigh Modes Each
        fname = self.full_path+"data/test_dc_mod2_ray2_lov0_shrt.txt"
        e1 = {"identifier": "149641",
              "misfit": 1.08851,
              "rayleigh": {0: {"frequency": [0.15, 64],
                               "velocity": [1/0.000334532972901842,
                                            1/0.00917746839997367]},
                           1: {"frequency": [0.479030947360446, 68],
                               "velocity":  [1/0.000323646256288129,
                                             1/0.00832719612771301]}},
              "love": None}
        e2 = {"identifier": "143539",
              "misfit": 1.0948,
              "rayleigh": {0: {"frequency": [0.1, 61.5],
                               "velocity": [1/0.000324619882942684,
                                            1/0.00917940142886033]},
                           1: {"frequency": [0.479030947360446, 62.2],
                               "velocity": [1/0.000313021699121662,
                                            1/0.00832708237075126]}},
              "love": None}
        models = [e1, e2]
        compare(fname, models)

        # Two Sets with Two Love Modes Each
        fname = self.full_path+"data/test_dc_mod2_ray0_lov2_shrt.txt"
        e1 = {"identifier": "149641",
              "misfit": 1.08851,
              "love": {0: {"frequency": [0.11, 61],
                           "velocity": [1/0.0003055565316784,
                                        1/0.00838314255586564]},
                       1: {"frequency": [0.920128309893243, 69],
                           "velocity":  [1/0.000305221889470528,
                                         1/0.00828240730448549]}},
              "rayleigh": None}
        e2 = {"identifier": "143539",
              "misfit": 1.0948,
              "love": {0: {"frequency": [0.15, 64],
                           "velocity": [1/0.000293577212739142,
                                        1/0.00838312381838565]},
                       1: {"frequency": [0.920128309893243, 61.1],
                           "velocity": [1/0.000293302878104174,
                                        1/0.0082822320807379]}},
              "rayleigh": None}
        models = [e1, e2]
        compare(fname, models)

        # Two Sets with Two Rayleigh and Love Modes Each
        fname = self.full_path+"data/test_dc_mod2_ray2_lov2_shrt.txt"
        e1 = {"identifier": "149641",
              "misfit": 1.08851,
              "love": {0: {"frequency": [0.11, 61],
                           "velocity": [1/0.0003055565316784,
                                        1/0.00838314255586564]},
                       1: {"frequency": [0.920128309893243, 69],
                           "velocity":  [1/0.000305221889470528,
                                         1/0.00828240730448549]}},
              "rayleigh": {0: {"frequency": [0.15, 64],
                               "velocity": [1/0.000334532972901842,
                                            1/0.00917746839997367]},
                           1: {"frequency": [0.479030947360446, 68],
                               "velocity":  [1/0.000323646256288129,
                                             1/0.00832719612771301]}}}
        e2 = {"identifier": "143539",
              "misfit": 1.0948,
              "love": {0: {"frequency": [0.15, 64],
                           "velocity": [1/0.000293577212739142,
                                        1/0.00838312381838565]},
                       1: {"frequency": [0.920128309893243, 61.1],
                           "velocity": [1/0.000293302878104174,
                                        1/0.0082822320807379]}},
              "rayleigh": {0: {"frequency": [0.1, 61.5],
                               "velocity": [1/0.000324619882942684,
                                            1/0.00917940142886033]},
                           1: {"frequency": [0.479030947360446, 62.2],
                               "velocity": [1/0.000313021699121662,
                                            1/0.00832708237075126]}}}
        models = [e1, e2]
        compare(fname, models)

        # Two Sets with Two Rayleigh and Love Modes Each -> Only Rayleigh
        e1_tmp = {key:e1[key] if key!="love" else None for key in e1}
        e2_tmp = {key:e2[key] if key!="love" else None for key in e2}
        models = [e1_tmp, e2_tmp]
        compare(fname, models, nrayleigh="all", nlove=0)

        # Two Sets with Two Rayleigh and Love Modes Each -> Only Love
        e1_tmp = {key:e1[key] if key!="rayleigh" else None for key in e1}
        e2_tmp = {key:e2[key] if key!="rayleigh" else None for key in e2}
        models = [e1_tmp, e2_tmp]
        compare(fname, models, nrayleigh=0, nlove="all")

        # Two Sets with Two Rayleigh and Love Modes Each -> 1 Rayleigh, 1 Love
        del e1["rayleigh"][1]
        del e1["love"][1]
        del e2["rayleigh"][1]
        del e2["love"][1]
        models = [e1, e2]
        compare(fname, models, nrayleigh=1, nlove=1)

        # Large File
        fname = self.full_path+"data/test_dc_mod100_ray2_lov2_full.txt"
        e1 = {"identifier": "146980",
              "misfit": 1.12243,
              "love": None,
              "rayleigh": {1: {"frequency": [0.368951808039113,
                                             0.420403775120212,
                                             0.479030947360446,
                                             0.545833938963633,
                                             0.621952904225151,
                                             0.708686997017004,
                                             0.80751654398444,
                                             0.920128309893243,
                                             1.04844428634184,
                                             1.19465449518708,
                                             1.3612543665533,
                                             1.55108732937071,
                                             1.76739334135326,
                                             2.01386418669743,
                                             2.29470648529046,
                                             2.61471348883233,
                                             2.97934688924555,
                                             3.39483003563085,
                                             3.86825415074099,
                                             4.40769935981326,
                                             5.02237259740979,
                                             5.72276474597882,
                                             6.52082968808573,
                                             7.43018832827235,
                                             8.46636106666995,
                                             9.64703269208945,
                                             10.9923542156285,
                                             12.5252867963149,
                                             14.2719936287069,
                                             16.2622864809594,
                                             18.5301345046044,
                                             21.1142440001138,
                                             24.0587190333435,
                                             27.4138141778719,
                                             31.2367922305983,
                                             35.5929015395883,
                                             40.556489624625,
                                             46.212272097088,
                                             52.6567785363412,
                                             60],
                               "slowness": [0.000352894753134505,
                                            0.000382583527133217,
                                            0.000399569739415364,
                                            0.000413059335406626,
                                            0.000428797264847807,
                                            0.000456928251602023,
                                            0.000515061314793316,
                                            0.000580981200873254,
                                            0.000643989528210298,
                                            0.00071396121507491,
                                            0.00080722797879219,
                                            0.00104454865107915,
                                            0.00121950228373324,
                                            0.00127028667752782,
                                            0.00130403179500955,
                                            0.00134585235039413,
                                            0.00147824081169916,
                                            0.00294416069804082,
                                            0.00363599334177799,
                                            0.00396011214013388,
                                            0.00417806038983369,
                                            0.00432666019698977,
                                            0.00443460924282423,
                                            0.00453217507309934,
                                            0.00466297023760077,
                                            0.00491730298090653,
                                            0.00543643875965759,
                                            0.00618999838283195,
                                            0.00686627463122456,
                                            0.00734630143840603,
                                            0.00767117445623039,
                                            0.00789084327612486,
                                            0.00804045566522677,
                                            0.00814325582260482,
                                            0.00821457440912399,
                                            0.00826456218386406,
                                            0.00829996560412771,
                                            0.00832529512576377,
                                            0.00834358889522566,
                                            0.00835691356059072]}}}
        models = [e1]
        compare(fname, models)


if __name__ == "__main__":
    unittest.main()
