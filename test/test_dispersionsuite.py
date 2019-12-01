"""Tests for DispersionSuite Class."""

import unittest
import swipp
import logging
logging.basicConfig(level=logging.DEBUG)

file_name = __file__.split("/")[-1]
full_path = __file__[:-len(file_name)]


class TestDispersionSuite(unittest.TestCase):
    def test_check_input(self):
        # DispersionSuite to be instantiated with DispersionSet object only.
        for test in [[1, 2, 3], (1, 2, 3), True, "DC"]:
            self.assertRaises(
                TypeError, swipp.DispersionSuite, test, "Test")

    def test_init(self):
        # Manual instantiation
        frequency = [1, 2, 3]
        velocity = [4, 5, 6]
        dc = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        dc_set = swipp.DispersionSet(identifier="Test", misfit=None,
                                     rayleigh={0: dc}, love=None)
        mysuite = swipp.DispersionSuite(dispersionset=dc_set)
        self.assertListEqual(frequency,
                             mysuite.sets[0].rayleigh[0].frq.tolist())
        self.assertListEqual(velocity,
                             mysuite.sets[0].rayleigh[0].vel.tolist())

    def test_append(self):
        frequency = [1, 2, 3]
        velocity = [4, 5, 6]
        dc = swipp.DispersionCurve(frequency=frequency, velocity=velocity)
        dc_set = swipp.DispersionSet(identifier="Test", misfit=None,
                                     rayleigh={0: dc}, love=None)
        mysuite = swipp.DispersionSuite(dispersionset=dc_set)
        dc_set = swipp.DispersionSet(identifier="Test1", misfit=None,
                                     rayleigh={0: dc}, love=None)
        mysuite.append(dispersionset=dc_set)
        for c_set in mysuite.sets:
            self.assertListEqual(frequency, c_set.rayleigh[0].frq.tolist())
            self.assertListEqual(velocity, c_set.rayleigh[0].vel.tolist())
        self.assertListEqual(["Test", "Test1"], mysuite.ids)
        self.assertListEqual([None, None], mysuite.misfits)

    def test_from_geopsy(self):
        # Two Sets with Two Rayleigh Modes Each
        mysuite = swipp.DispersionSuite.from_geopsy(
            fname=full_path+"data/test_dc_mod2_ray2_lov0_shrt.txt")

        true_rays_frq = [[[0.15, 64], [0.479030947360446, 68]],
                         [[0.1, 61.5], [0.479030947360446, 62.2]]]
        true_rays_vel = [[[1/0.000334532972901842, 1/0.00917746839997367],
                          [1/0.000323646256288129, 1/0.00832719612771301]],
                         [[1/0.000324619882942684, 1/0.00917940142886033],
                          [1/0.000313021699121662, 1/0.00832708237075126]]]

        true_msfts = [1.08851, 1.0948]
        true_ids = ["149641", "143539"]

        for set_num, c_set in enumerate(mysuite.sets):
            for mode_num, (ray_frq, ray_vel) in enumerate(zip(true_rays_frq[set_num],
                                                              true_rays_vel[set_num])):
                self.assertListEqual(ray_frq, c_set.rayleigh[mode_num].frq.tolist())
                self.assertListEqual(ray_vel, c_set.rayleigh[mode_num].vel.tolist())
        self.assertListEqual(mysuite.misfits, true_msfts)
        self.assertListEqual(mysuite.ids, true_ids)

        # Two Sets with Two Love Modes Each
        mysuite = swipp.DispersionSuite.from_geopsy(
            fname=full_path+"data/test_dc_mod2_ray0_lov2_shrt.txt")

        true_lovs_frq = [[[0.11, 61], [0.920128309893243, 69]],
                         [[0.15, 64], [0.920128309893243, 61.1]]]
        true_lovs_vel = [[[1/0.0003055565316784, 1/0.00838314255586564],
                          [1/0.000305221889470528, 1/0.00828240730448549]],
                         [[1/0.000293577212739142, 1/0.00838312381838565],
                          [1/0.000293302878104174, 1/0.0082822320807379]]]

        true_msfts = [1.08851, 1.0948]
        true_ids = ["149641", "143539"]

        for set_num, c_set in enumerate(mysuite.sets):
            for mode_num, (lov_frq, lov_vel) in enumerate(zip(true_lovs_frq[set_num],
                                                              true_lovs_vel[set_num])):
                self.assertListEqual(lov_frq, c_set.love[mode_num].frq.tolist())
                self.assertListEqual(lov_vel, c_set.love[mode_num].vel.tolist())
        self.assertListEqual(mysuite.misfits, true_msfts)
        self.assertListEqual(mysuite.ids, true_ids)

        # One Set with Two Rayleigh and Two Love Modes
        mysuite = swipp.DispersionSuite.from_geopsy(
            fname=full_path+"data/test_dc_mod1_ray1_lov1_shrt.txt")

        true_rays_frq = [[[0.15, 64],
                          [0.479030947360446, 68]]]
        true_rays_vel = [[[1/0.000334532972901842, 1/0.00917746839997367],
                          [1/0.000323646256288129, 1/0.00832719612771301]]]

        true_lovs_frq = [[[0.11, 61],
                          [0.920128309893243, 69]]]
        true_lovs_vel = [[[1/0.0003055565316784, 1/0.00838314255586564],
                          [1/0.000305221889470528, 1/0.00828240730448549]]]

        true_msfts = [1.08851]
        true_ids = ["149641"]

        for set_num, c_set in enumerate(mysuite.sets):
            for mode_num, (ray_frq, ray_vel) in enumerate(zip(true_rays_frq[set_num],
                                                              true_rays_vel[set_num])):
                self.assertListEqual(ray_frq, c_set.rayleigh[mode_num].frq.tolist())
                self.assertListEqual(ray_vel, c_set.rayleigh[mode_num].vel.tolist())
            for mode_num, (lov_frq, lov_vel) in enumerate(zip(true_lovs_frq[set_num],
                                                              true_lovs_vel[set_num])):
                self.assertListEqual(lov_frq, c_set.love[mode_num].frq.tolist())
                self.assertListEqual(lov_vel, c_set.love[mode_num].vel.tolist())
        self.assertListEqual(mysuite.misfits, true_msfts)
        self.assertListEqual(mysuite.ids, true_ids)

        # Two Sets with Two Rayleigh and Love Modes Each
        mysuite = swipp.DispersionSuite.from_geopsy(
            fname=full_path+"data/test_dc_mod2_ray2_lov2_shrt.txt")

        true_rays_frq = [[[0.15, 64], [0.479030947360446, 68]],
                         [[0.1, 61.5], [0.479030947360446, 62.2]]]
        true_rays_vel = [[[1/0.000334532972901842, 1/0.00917746839997367],
                          [1/0.000323646256288129, 1/0.00832719612771301]],
                         [[1/0.000324619882942684, 1/0.00917940142886033],
                          [1/0.000313021699121662, 1/0.00832708237075126]]]

        true_lovs_frq = [[[0.11, 61], [0.920128309893243, 69]],
                         [[0.15, 64], [0.920128309893243, 61.1]]]
        true_lovs_vel = [[[1/0.0003055565316784, 1/0.00838314255586564],
                          [1/0.000305221889470528, 1/0.00828240730448549]],
                         [[1/0.000293577212739142, 1/0.00838312381838565],
                          [1/0.000293302878104174, 1/0.0082822320807379]]]

        true_msfts = [1.08851, 1.0948]
        true_ids = ["149641", "143539"]

        for set_num, c_set in enumerate(mysuite.sets):
            for mode_num, (ray_frq, ray_vel) in enumerate(zip(true_rays_frq[set_num],
                                                              true_rays_vel[set_num])):
                self.assertListEqual(ray_frq, c_set.rayleigh[mode_num].frq.tolist())
                self.assertListEqual(ray_vel, c_set.rayleigh[mode_num].vel.tolist())
            for mode_num, (lov_frq, lov_vel) in enumerate(zip(true_lovs_frq[set_num],
                                                              true_lovs_vel[set_num])):
                self.assertListEqual(lov_frq, c_set.love[mode_num].frq.tolist())
                self.assertListEqual(lov_vel, c_set.love[mode_num].vel.tolist())
        self.assertListEqual(mysuite.misfits, true_msfts)
        self.assertListEqual(mysuite.ids, true_ids)

        # Large File
        mysuite = swipp.DispersionSuite.from_geopsy(
            fname=full_path+"data/test_dc_mod100_ray2_lov2_full.txt")

        picked_model = "146980"
        known_misfit = 1.12243
        known_freq_r1 = [0.368951808039113,
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
                         ]
        known_slow_r1 = [0.000352894753134505,
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
                         0.00134585235039413]

        pick_id = mysuite.ids.index(picked_model)
        myset = mysuite.sets[pick_id]
        self.assertListEqual(known_freq_r1, myset.rayleigh[1].frq[:16].tolist())
        known_vel_r1 = [1/p for p in known_slow_r1]
        self.assertListEqual(known_vel_r1, myset.rayleigh[1].vel[:16].tolist())
        self.assertEqual(known_misfit, mysuite.misfits[pick_id])


if __name__ == "__main__":
    unittest.main()
