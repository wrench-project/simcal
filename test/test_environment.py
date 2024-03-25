import unittest
from simcal import Environment

class MyTestCase(unittest.TestCase):
    def test_tempdir(self):
        self.assertEqual(True, False)  # add assertion here

    def test_tempfile(self):
        pass
    def test_2tmpdir(self):
        pass
    def test_2tmpfile(self):
        pass
    def test_2tmpdirWith2tmpfile(self):
        pass
if __name__ == '__main__':
    unittest.main()
