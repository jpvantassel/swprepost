"""Tests for Parameterization class."""

import swipp
import unittest
import os
import logging
logging.basicConfig(level=logging.DEBUG)


class TestParameterization(unittest.TestCase):

    def test_init(self):
        # Define parameterization in terms of depths
        vp = swipp.Parameter(par_type="CD", lay_min=[1, 5], lay_max=[3, 16],
                             par_min=[200, 400], par_max=[400, 600], 
                             par_rev=[True, False])
        pr = swipp.Parameter(par_type="CD", lay_min=[0], lay_max=[100],
                             par_min=[0.2], par_max=[0.5], 
                             par_rev=[False])
        vs = swipp.Parameter(par_type="CD", lay_min=[1, 2], lay_max=[2, 3],
                             par_min=[100, 200], par_max=[200, 300], 
                             par_rev=[True, False])
        rh = swipp.Parameter(par_type="CD", lay_min=[0], lay_max=[100],
                             par_min=[2000], par_max=[2000], 
                             par_rev=[False])
        test = swipp.Parameterization(vp, pr, vs, rh)
        self.assertTrue(test)

        # Define parameters in terms of thicknesses
        vp = swipp.Parameter(par_type="CT", lay_min=[1, 5], lay_max=[3, 16],
                             par_min=[200, 400], par_max=[400, 600], 
                             par_rev=[True, False])
        pr = swipp.Parameter(par_type="CT", lay_min=[0], lay_max=[100],
                             par_min=[0.2], par_max=[0.5], 
                             par_rev=[False])
        vs = swipp.Parameter(par_type="CT", lay_min=[1, 2], lay_max=[2, 3],
                             par_min=[100, 200], par_max=[200, 300], 
                             par_rev=[True, False])
        rh = swipp.Parameter(par_type="CT", lay_min=[0], lay_max=[100],
                             par_min=[2000], par_max=[2000], 
                             par_rev=[False])
        test = swipp.Parameterization(vp, pr, vs, rh)
        self.assertTrue(test)

# TODO (jpv): Finish tests.
# def test_init_type(self):
#     "Check input types, should be a list."

#     vs = ['LR', 3.0, 100, 200, True]
#     vp = ['LN', 2, 200, 400, True]
#     pr = ['LN', 3, 0.2, 0.5, False]
#     rh = ['FX', 2000]
#     wv = [1, 100]

#     for vals in [1.2, "1.3", True, 1]:
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)

# def test_init_vals(self):
#     "Check input values, should start with FX, FTL, LN, LNI, or LR."

#     vs = ['LR', 3.0, 100, 200, True]
#     vp = ['LN', 2, 200, 400, True]
#     pr = ['LN', 3, 0.2, 0.5, False]
#     rh = ['FX', 2000]
#     wv = [1, 100]

#     for vals in [[1.2], ["1.3"], [True], [1]]:
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vals, vp, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vals, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, vals, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, pr, vals, wv)

# def test_init_fx(self):
#     "Check FX, second values should be positive integer or float."

#     vs = ['LR', 3.0, 100, 200, True]
#     vp = ['LN', 2, 200, 400, True]
#     pr = ['LN', 3, 0.2, 0.5, False]
#     rh = ['FX', 2000]
#     wv = [1, 100]

#     for val in ["1", True, [1], (1,)]:
#         vals = ['FX', val]
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)

#     for val in [-1, 0]:
#         vals = ['FX', val]
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vals, vp, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vals, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, vals, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, pr, vals, wv)

# def test_init_ftl(self):
#     """Check FTL, second values should be positive integer, third value
#     should be interger or float great than 1.
#     """

#     vs = ['LR', 3.0, 100, 200, True]
#     vp = ['LN', 2, 200, 400, True]
#     pr = ['LN', 3, 0.2, 0.5, False]
#     rh = ['FX', 2000]
#     wv = [1, 100]

#     # Check integer for number of layers.
#     for val in ["1", True, [1], (1,), 1.1]:
#         vals = ['FTL', val, 1.1, 100, 200, True]
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
#     # Check number of layers >0.
#     for val in [-1, 0]:
#         vals = ['FTL', val, 2, 100, 200, True]
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vals, vp, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vals, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, vals, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, pr, vals, wv)
#     # Check integer or float for second value.
#     for val in ["1", True, [1], (1,)]:
#         vals = ['FTL', 2, val, 100, 200, True]
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
#     # Check layer thickness is >0.
#     for val in [-1, 0]:
#         vals = ['FTL', 2, val, 100, 200, True]
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vals, vp, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vals, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, vals, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, pr, vals, wv)

# def test_init_ln(self):
#     "Check LN second value should be postive integer."

#     vs = ['LR', 3.0, 100, 200, True]
#     vp = ['LN', 2, 200, 400, True]
#     pr = ['LN', 3, 0.2, 0.5, False]
#     rh = ['FX', 2000]
#     wv = [1, 100]

#     for val in ["5", True, 0.5, 2.2]:
#         vals = ['LN', val, 50, 300, True]
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
#     for val in [-1, 0]:
#         vals = ['LN', val, 50, 300, True]
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vals, vp, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vals, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, vals, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, pr, vals, wv)

# def test_init_lni(self):
#     "Test LNI, first number int greater than 1, second number int or float > 1"

#     vs = ['LR', 3.0, 100, 200, True]
#     vp = ['LN', 2, 200, 400, True]
#     pr = ['LN', 3, 0.2, 0.5, False]
#     rh = ['FX', 2000]
#     wv = [1, 100]

#     # Check number of layers is an int
#     for val in ["5", True, 0.5, 2.2]:
#         vals = ['LNI', val, 1.1, 50, 300, True]
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
#     # Check factor is an int or float
#     for val in ["5", True]:
#         vals = ['LNI', 2, val, 50, 300, True]
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
#     # Check number of layers is greater than 1
#     for val in [-1, 0, 1]:
#         vals = ['LNI', val, 1.1, 50, 300, True]
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vals, vp, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vals, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, vals, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, pr, vals, wv)
#     # Check factor is greater than 1
#     for val in [-1, 0, 1]:
#         vals = ['LNI', 5, val, 50, 300, True]
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vals, vp, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vals, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, vals, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, pr, vals, wv)

# def test_init_lr(self):
#     "Test LR, second value should be postive integer or float greater than 1"

#     vs = ['LR', 3.0, 100, 200, True]
#     vp = ['LN', 2, 200, 400, True]
#     pr = ['LN', 3, 0.2, 0.5, False]
#     rh = ['FX', 2000]
#     wv = [1, 100]

#     for val in ["5", True]:
#         vals = ['LR', val, 50, 300, True]
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vals, vp, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vals, pr, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, vals, rh, wv)
#         self.assertRaises(
#             TypeError, swipp.Parameter.from_min_max, vs, vp, pr, vals, wv)
#     for val in [-1, 0, 0.5, 0.9, 1, 1.0]:
#         vals = ['LR', val, 50, 300, True]
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vals, vp, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vals, pr, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, vals, rh, wv)
#         self.assertRaises(ValueError, swipp.Parameter.from_min_max,
#                           vs, vp, pr, vals, wv)

# def test_lr_calc(self):
#     "Test LR calculation."
#     wv = [1, 100]
#     known_lr = {'1.4':
#                 [[0.3, 0.5, 1.2, 2.2, 3.6, 5.5, 8.2, 11.9, 17.2, 24.6, 34.9, 50],
#                  [0.5, 1.2, 2.2, 3.6, 5.5, 8.2, 11.9, 17.2, 24.6, 34.9, 50, "half-space"]],
#                 '1.5':
#                 [[0.3, 0.5, 1.3, 2.4, 4.1, 6.6, 10.4, 16.1, 24.6, 50],
#                  [0.5, 1.3, 2.4, 4.1, 6.6, 10.4, 16.1, 24.6, 50, "half-space"]],
#                 '2.0':
#                 [[0.3, 0.5, 1.5, 3.5, 7.5, 15.5, 31.5, 50],
#                  [0.5, 1.5, 3.5, 7.5, 15.5, 31.5, 50, "half-space"]],
#                 '3.0':
#                 [[0.3, 0.5, 2.0, 6.5, 20, 50],
#                  [0.5, 2.0, 6.5, 20, 50, "half-space"]],
#                 '5.0':
#                 [[0.3, 0.5, 3.0, 15.5, 50],
#                  [0.5, 3.0, 15.5, 50, "half-space"]]}
#     for key in known_lr.keys():
#         mindepth, maxdepth = swipp.Parameter._depth_lr(
#             wv, float(key), 2)
#         for known1, test1, known2, test2 in zip(mindepth, known_lr[key][0], maxdepth, known_lr[key][1]):
#             self.assertAlmostEqual(known1, test1, delta=0.051)
#             self.assertAlmostEqual(known2, test2, delta=0.051)

# def test_write_to_file(self):
#     """Check if parameter data can be written to .param file. Need to
#     use DINVER to confirm file was sucessfully written.
#     """
#     vp = ['LNI', 4, 4, 200, 400, True]
#     pr = ['LN', 3, 0.2, 0.5, False]
#     vs = ['FTL', 3, 3, 100, 200, True]
#     rh = ['FX', 2000]
#     wv = [1, 100]
#     par = swipp.Parameter.from_min_max(vp, pr, vs, rh, wv)
#     name1 = "LNI_LN_FTL_FX"
#     par.write_to_file(fname=f"{name1}", version='2.10.1')
#     self.assertTrue(os.path.isfile(f"{name1}.param"))

#     vp = ['LR', 3, 200, 400, True]
#     pr = ['LNI', 3, 3, 0.2, 0.5, False]
#     vs = ['FTL', 5, 5, 100, 200, True]
#     rh = ['FX', 2000]
#     wv = [1, 100]
#     name2 = "LR_LNI_FTL_FX"
#     par = swipp.Parameter.from_min_max(vp, pr, vs, rh, wv)
#     par.write_to_file(fname=f"{name2}", version='2.10.1')
#     self.assertTrue(os.path.isfile(f"{name2}.param"))

#     print(f"Check if {name1} and {name2} wrote correctly!")
#     os.remove(f"{name1}.param")
#     os.remove(f"{name2}.param")

if __name__ == '__main__':
    unittest.main()
