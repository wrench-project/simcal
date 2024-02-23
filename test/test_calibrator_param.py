from unittest import TestCase

from simcal.calibrator_param import *


class TestCalibratorParam(TestCase):
    def test_LinearParam(self):
        basic = LinearParam(10, 100)
        b = basic.from_normalized(0.5)
        self.assertAlmostEqual(b, 55, delta=0.01)
        b = basic.to_normalized(b)
        self.assertAlmostEqual(b, 0.5, delta=0.01)

        formatted = LinearParam(0, 100).format("%.1f formatted")
        f = formatted.from_normalized(0.5)
        self.assertEqual(str(f), "50.0 formatted")
        f = formatted.to_normalized(f)
        self.assertAlmostEqual(f, 0.5, delta=0.01)

        advanced = LinearParam(9, 99)
        advanced.range_start = 1
        advanced.range_end = 10
        a = advanced.from_normalized(5)

        self.assertAlmostEqual(a, 49.0, delta=0.01)
        a = advanced.to_normalized(a)

        self.assertAlmostEqual(a, 5, delta=0.01)

    def test_ExponentialParam(self):
        basic = ExponentialParam(29, 32)
        b = basic.from_normalized(0.5)
        self.assertAlmostEqual(b, 1518500249.988025, delta=0.01)
        b = basic.to_normalized(b)
        self.assertAlmostEqual(b, 0.5, delta=0.01)

        formatted = ExponentialParam(0, 32).format("%.1f formatted")
        f = formatted.from_normalized(0.5)
        self.assertEqual(str(f), "65536.0 formatted")
        f = formatted.to_normalized(f)
        self.assertAlmostEqual(f, 0.5, delta=0.01)

        advanced = ExponentialParam(9, 99)
        advanced.range_start = 1
        advanced.range_end = 10
        a = advanced.from_normalized(5)

        self.assertAlmostEqual(a, 562949953421312.0, delta=0.01)
        a = advanced.to_normalized(a)

        self.assertAlmostEqual(a, 5, delta=0.01)
