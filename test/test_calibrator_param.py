from unittest import TestCase

from simcal.parameters.base import *


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

    def test_OrdinalParam(self):
        basic = OrdinalParam(("a", "b", "c", "d", "e"))
        b = basic.from_normalized(0.5)
        self.assertEqual(b, "c")
        b = basic.to_normalized(b)
        self.assertAlmostEqual(b, 0.4, delta=0.01)

        formatted = OrdinalParam((1, 2, 3, 4, 5, 6, 7, 8)).format("%.1f formatted")
        f = formatted.from_normalized(0.5)
        self.assertEqual(str(f), "5.0 formatted")
        f = formatted.to_normalized(f)
        self.assertAlmostEqual(f, 0.5, delta=0.01)

        advanced = OrdinalParam(("a", "b", "c", "d", "e"))
        advanced.range_start = 5
        advanced.range_end = 10
        a = advanced.from_normalized(8)

        self.assertEqual(a, "d")
        a = advanced.to_normalized(a)

        self.assertAlmostEqual(a, 8, delta=0.01)

        lambda_param = OrdinalParam(("a", "b", "c", "d", "e"))
        lambda_param.from_normalize_override = lambda this, x: this.options[0] if x < 0.5 \
            else this.options[math.ceil((x - .5) * 5)]

        lambda_param.to_normalize_override = lambda this, x: 0 if x == "a" \
            else this.options.index(x) / 5 + .4

        lam = lambda_param.from_normalized(0.2)
        self.assertEqual(lam, "a")
        lam = lambda_param.to_normalized(lam)
        self.assertEqual(lam, 0)
        lam = lambda_param.from_normalized(0.8)
        self.assertEqual(lam, "c")
        lam = lambda_param.to_normalized(lam)
        self.assertAlmostEqual(lam, 0.8, delta=.01)
