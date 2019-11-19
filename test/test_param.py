"""
Tests for paramater class.
"""
import swipp
import unittest
import os
import logging
logging.basicConfig(level=logging.DEBUG)


dex_vp = {"depth": {"min": [1, 5], "max": [3, 16]},
          "par": {"min": [200, 400], "max": [400, 600], "rev": [True, False]}}
dex_pr = {"depth": {"min": [0], "max": [100]},
          "par": {"min": [0.2], "max": [0.5], "rev": [False]}}
dex_vs = {"depth": {"min": [1, 2], "max": [2, 3]},
          "par": {"min": [100, 200], "max": [200, 300], "rev": [True, False]}}
dex_rh = {"depth": {"min": [0], "max": [100]},
          "par": {"min": [2000], "max": [2000], "rev": [False]}}
dex_wv = [1, 100]
dex_ft = 3

tex_vp = {"thickness": {"min": [1, 5], "max": [3, 16]},
          "par": {"min": [200, 400], "max": [400, 600], "rev": [True, False]}}
tex_pr = {"thickness": {"min": [0], "max": [100]},
          "par": {"min": [0.2], "max": [0.5], "rev": [False]}}
tex_vs = {"thickness": {"min": [1, 2], "max": [2, 3]},
          "par": {"min": [100, 200], "max": [200, 300], "rev": [True, False]}}
tex_rh = {"thickness": {"min": [0], "max": [100]},
          "par": {"min": [2000], "max": [2000], "rev": [False]}}
tex_wv = [1, 100]
tex_ft = 3


class TestParam(unittest.TestCase):

    def test_init(self):
        # Define parameterization in terms of depths
        test = swipp.Parameter(vp=dex_vp, pr=dex_pr, vs=dex_vs, rh=dex_rh)
        self.assertDictEqual(test.vp, dex_vp)
        self.assertDictEqual(test.pr, dex_pr)
        self.assertDictEqual(test.vs, dex_vs)
        self.assertDictEqual(test.rh, dex_rh)

        # Define parameters in terms of thicknesses
        test = swipp.Parameter(vp=tex_vp, pr=tex_pr, vs=tex_vs, rh=tex_rh)
        self.assertDictEqual(test.vp, tex_vp)
        self.assertDictEqual(test.pr, tex_pr)
        self.assertDictEqual(test.vs, tex_vs)
        self.assertDictEqual(test.rh, tex_rh)

    def test_check_parameter(self):
        pass

    def test_check_wave(self):
        pass

    def test_check_factor(self):
        pass

    # def test_wv(self):
    #     vs = ['LR', 3.0, 100, 200, True]
    #     vp = ['LN', 2, 200, 400, True]
    #     pr = ['LN', 3, 0.2, 0.5, False]
    #     rh = ['FX', 2000]
    #     wv = [1, 100]
    #     "Test wv input, should be list of integer or floats"
    #     # Wave smaller to larger
    #     self.assertAlmostEqual(
    #         max(wv)/2,
    #         max(swipp.Parameter(vs, vp, pr, rh, wv)._par_for_plot(par='depth')))
    #     # Flip wave larger to smaller
    #     wv.sort(reverse=True)
    #     self.assertAlmostEqual(
    #         max(wv)/2,
    #         max(swipp.Parameter(vs, vp, pr, rh, wv)._par_for_plot(par='depth')))
    #     for val in [1, '1', True, (1, 2)]:
    #         self.assertRaises(TypeError, swipp.Parameter,
    #                           vs, vp, pr, rh, val)
    #     for val in [0, -1, -0.01]:
    #         vals = [val, 100]
    #         self.assertRaises(ValueError, swipp.Parameter,
    #                           vs, vp, pr, rh, vals)

    # def test_factor(self):
    #     "Test factor input, should be an integer or float."
    #     for factor in ['2', True, [2.0]]:
    #         self.assertRaises(TypeError, swipp.Parameter,
    #                           vs, vp, pr, rh, wv, factor)

    def test_init_type(self):
        "Check input types, should be a list."

        vs = ['LR', 3.0, 100, 200, True]
        vp = ['LN', 2, 200, 400, True]
        pr = ['LN', 3, 0.2, 0.5, False]
        rh = ['FX', 2000]
        wv = [1, 100]

        for vals in [1.2, "1.3", True, 1]:
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)

    def test_init_vals(self):
        "Check input values, should start with FX, FTL, LN, LNI, or LR."

        vs = ['LR', 3.0, 100, 200, True]
        vp = ['LN', 2, 200, 400, True]
        pr = ['LN', 3, 0.2, 0.5, False]
        rh = ['FX', 2000]
        wv = [1, 100]

        for vals in [[1.2], ["1.3"], [True], [1]]:
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vals, vp, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vals, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, vals, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, pr, vals, wv)

    def test_init_fx(self):
        "Check FX, second values should be positive integer or float."

        vs = ['LR', 3.0, 100, 200, True]
        vp = ['LN', 2, 200, 400, True]
        pr = ['LN', 3, 0.2, 0.5, False]
        rh = ['FX', 2000]
        wv = [1, 100]

        for val in ["1", True, [1], (1,)]:
            vals = ['FX', val]
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)

        for val in [-1, 0]:
            vals = ['FX', val]
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vals, vp, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vals, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, vals, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, pr, vals, wv)

    def test_init_ftl(self):
        """Check FTL, second values should be positive integer, third value
        should be interger or float great than 1.
        """

        vs = ['LR', 3.0, 100, 200, True]
        vp = ['LN', 2, 200, 400, True]
        pr = ['LN', 3, 0.2, 0.5, False]
        rh = ['FX', 2000]
        wv = [1, 100]

        # Check integer for number of layers.
        for val in ["1", True, [1], (1,), 1.1]:
            vals = ['FTL', val, 1.1, 100, 200, True]
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
        # Check number of layers >0.
        for val in [-1, 0]:
            vals = ['FTL', val, 2, 100, 200, True]
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vals, vp, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vals, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, vals, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, pr, vals, wv)
        # Check integer or float for second value.
        for val in ["1", True, [1], (1,)]:
            vals = ['FTL', 2, val, 100, 200, True]
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
        # Check layer thickness is >0.
        for val in [-1, 0]:
            vals = ['FTL', 2, val, 100, 200, True]
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vals, vp, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vals, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, vals, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, pr, vals, wv)

    def test_init_ln(self):
        "Check LN second value should be postive integer."

        vs = ['LR', 3.0, 100, 200, True]
        vp = ['LN', 2, 200, 400, True]
        pr = ['LN', 3, 0.2, 0.5, False]
        rh = ['FX', 2000]
        wv = [1, 100]

        for val in ["5", True, 0.5, 2.2]:
            vals = ['LN', val, 50, 300, True]
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
        for val in [-1, 0]:
            vals = ['LN', val, 50, 300, True]
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vals, vp, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vals, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, vals, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, pr, vals, wv)

    def test_init_lni(self):
        "Test LNI, first number int greater than 1, second number int or float > 1"

        vs = ['LR', 3.0, 100, 200, True]
        vp = ['LN', 2, 200, 400, True]
        pr = ['LN', 3, 0.2, 0.5, False]
        rh = ['FX', 2000]
        wv = [1, 100]

        # Check number of layers is an int
        for val in ["5", True, 0.5, 2.2]:
            vals = ['LNI', val, 1.1, 50, 300, True]
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
        # Check factor is an int or float
        for val in ["5", True]:
            vals = ['LNI', 2, val, 50, 300, True]
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
        # Check number of layers is greater than 1
        for val in [-1, 0, 1]:
            vals = ['LNI', val, 1.1, 50, 300, True]
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vals, vp, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vals, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, vals, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, pr, vals, wv)
        # Check factor is greater than 1
        for val in [-1, 0, 1]:
            vals = ['LNI', 5, val, 50, 300, True]
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vals, vp, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vals, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, vals, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, pr, vals, wv)

    def test_init_lr(self):
        "Test LR, second value should be postive integer or float greater than 1"

        vs = ['LR', 3.0, 100, 200, True]
        vp = ['LN', 2, 200, 400, True]
        pr = ['LN', 3, 0.2, 0.5, False]
        rh = ['FX', 2000]
        wv = [1, 100]

        for val in ["5", True]:
            vals = ['LR', val, 50, 300, True]
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
            self.assertRaises(
                TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
        for val in [-1, 0, 0.5, 0.9, 1, 1.0]:
            vals = ['LR', val, 50, 300, True]
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vals, vp, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vals, pr, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, vals, rh, wv)
            self.assertRaises(ValueError, swipp.Parameter.from_min_max,
                              vs, vp, pr, vals, wv)

    def test_lr_calc(self):
        "Test LR calculation."
        wv = [1, 100]
        known_lr = {'1.4':
                    [[0.3, 0.5, 1.2, 2.2, 3.6, 5.5, 8.2, 11.9, 17.2, 24.6, 34.9, 50],
                     [0.5, 1.2, 2.2, 3.6, 5.5, 8.2, 11.9, 17.2, 24.6, 34.9, 50, "half-space"]],
                    '1.5':
                    [[0.3, 0.5, 1.3, 2.4, 4.1, 6.6, 10.4, 16.1, 24.6, 50],
                     [0.5, 1.3, 2.4, 4.1, 6.6, 10.4, 16.1, 24.6, 50, "half-space"]],
                    '2.0':
                    [[0.3, 0.5, 1.5, 3.5, 7.5, 15.5, 31.5, 50],
                     [0.5, 1.5, 3.5, 7.5, 15.5, 31.5, 50, "half-space"]],
                    '3.0':
                    [[0.3, 0.5, 2.0, 6.5, 20, 50],
                     [0.5, 2.0, 6.5, 20, 50, "half-space"]],
                    '5.0':
                    [[0.3, 0.5, 3.0, 15.5, 50],
                     [0.5, 3.0, 15.5, 50, "half-space"]]}
        for key in known_lr.keys():
            mindepth, maxdepth = swipp.Parameter._depth_lr(
                wv, float(key), 2)
            for known1, test1, known2, test2 in zip(mindepth, known_lr[key][0], maxdepth, known_lr[key][1]):
                self.assertAlmostEqual(known1, test1, delta=0.051)
                self.assertAlmostEqual(known2, test2, delta=0.051)

    def test_write_to_file(self):
        """Check if parameter data can be written to .param file. Need to
        use DINVER to confirm file was sucessfully written.
        """
        vp = ['LNI', 4, 4, 200, 400, True]
        pr = ['LN', 3, 0.2, 0.5, False]
        vs = ['FTL', 3, 3, 100, 200, True]
        rh = ['FX', 2000]
        wv = [1, 100]
        par = swipp.Parameter.from_min_max(vp, pr, vs, rh, wv)
        name1 = "LNI_LN_FTL_FX"
        par.write_to_file(fname=f"{name1}", version='2.10.1')
        self.assertTrue(os.path.isfile(f"{name1}.param"))

        vp = ['LR', 3, 200, 400, True]
        pr = ['LNI', 3, 3, 0.2, 0.5, False]
        vs = ['FTL', 5, 5, 100, 200, True]
        rh = ['FX', 2000]
        wv = [1, 100]
        name2 = "LR_LNI_FTL_FX"
        par = swipp.Parameter.from_min_max(vp, pr, vs, rh, wv)
        par.write_to_file(fname=f"{name2}", version='2.10.1')
        self.assertTrue(os.path.isfile(f"{name2}.param"))

        print(f"Check if {name1} and {name2} wrote correctly!")
        os.remove(f"{name1}.param")
        os.remove(f"{name2}.param")


if __name__ == '__main__':
    unittest.main()
