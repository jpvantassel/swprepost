import unittest

def get_full_path(path):
    if path.count("/") > 1:
        file_name = path.split(r"/")[-1]
        full_path = path[:-len(file_name)]
    else:
        file_name = path.split(r"\\")[-1]
        full_path = path[:-len(file_name)]
    return full_path

class TestCase(unittest.TestCase):

    def assertListAlmostEqual(self, list1, list2, **kwargs):
        for a, b in zip(list1, list2):
            self.assertAlmostEqual(a, b, **kwargs)

    def assertArrayEqual(self, array1, array2):
        self.assertListEqual(array1.tolist(), array2.tolist())

    def assertArrayAlmostEqual(self, array1, array2, **kwargs):
        assert(array1.size == array2.size)
        array1 = array1.flatten()
        array2 = array2.flatten()
        for v1, v2 in zip(array1, array2):
            self.assertAlmostEqual(v1, v2, **kwargs)
