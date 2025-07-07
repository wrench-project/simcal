import math
from unittest import TestCase

from simcal.parameters import *


class TestCalibratorParam(TestCase):
    def test_LinearParam(self):
        basic = Linear(10, 100)
        b = basic.from_normalized(0.5)
        self.assertAlmostEqual(b, 55, delta=0.01)
        b = basic.to_normalized(b)
        self.assertAlmostEqual(b, 0.5, delta=0.01)

        formatted = Linear(0, 100).format("%.1f formatted")
        f = formatted.from_normalized(0.5)
        self.assertEqual(str(f), "50.0 formatted")
        f = formatted.to_normalized(f)
        self.assertAlmostEqual(f, 0.5, delta=0.01)

        advanced = Linear(9, 99)
        advanced.range_start = 1
        advanced.range_end = 10
        a = advanced.from_normalized(5)

        self.assertAlmostEqual(a, 49.0, delta=0.01)
        a = advanced.to_normalized(a)

        self.assertAlmostEqual(a, 5, delta=0.01)

    def test_ExponentialParam(self):
        basic = Exponential(29, 32)
        b = basic.from_normalized(0.5)
        self.assertAlmostEqual(b, 1518500249.988025, delta=0.01)
        b = basic.to_normalized(b)
        self.assertAlmostEqual(b, 0.5, delta=0.01)

        formatted = Exponential(0, 32).format("%.1f formatted")
        f = formatted.from_normalized(0.5)
        self.assertEqual(str(f), "65536.0 formatted")
        f = formatted.to_normalized(f)
        self.assertAlmostEqual(f, 0.5, delta=0.01)

        advanced = Exponential(9, 99)
        advanced.range_start = 1
        advanced.range_end = 10
        a = advanced.from_normalized(5)

        self.assertAlmostEqual(a, 562949953421312.0, delta=0.01)
        a = advanced.to_normalized(a)

        self.assertAlmostEqual(a, 5, delta=0.01)

    def test_OrdinalParam(self):
        basic = Ordinal(("a", "b", "c", "d", "e"))
        b = basic.from_normalized(0.5)
        self.assertEqual(b, "c")
        b = basic.to_normalized(b)
        self.assertAlmostEqual(b, 0.4, delta=0.01)

        formatted = Ordinal((1, 2, 3, 4, 5, 6, 7, 8)).format("%.1f formatted")
        f = formatted.from_normalized(0.5)
        self.assertEqual(str(f), "5.0 formatted")
        f = formatted.to_normalized(f)
        self.assertAlmostEqual(f, 0.5, delta=0.01)

        advanced = Ordinal(("a", "b", "c", "d", "e"))
        advanced.range_start = 5
        advanced.range_end = 10
        a = advanced.from_normalized(8)

        self.assertEqual(a, "d")
        a = advanced.to_normalized(a)

        self.assertAlmostEqual(a, 8, delta=0.01)

        lambda_param = Ordinal(("a", "b", "c", "d", "e"))
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

    def test_ExponentialParam(self):
        basic = Exponential(29, 32)
        new_start = basic.from_normalized(0.4)
        new_end = basic.from_normalized(0.6)
        constrained = basic.constrain(new_start, new_end)
        self.assertAlmostEqual(constrained.from_normalized(0), new_start, delta=.01)
        self.assertAlmostEqual(constrained.from_normalized(1), new_end, delta=.01)
        self.assertAlmostEqual(constrained.from_normalized(0.5), basic.from_normalized(0.5), delta=.01)

        advanced = Exponential(9, 99)
        advanced.range_start = 5
        advanced.range_end = 10
        new_start = advanced.from_normalized(6)
        new_end = advanced.from_normalized(7)
        constrained = advanced.constrain(new_start, new_end)
        self.assertAlmostEqual(constrained.from_normalized(5), new_start, delta=.01)
        self.assertAlmostEqual(constrained.from_normalized(10), new_end, delta=.01)
        self.assertAlmostEqual(constrained.from_normalized(7.5), advanced.from_normalized(6.5), delta=.01)

        basic = Linear(10, 100)
        new_start = basic.from_normalized(0.4)
        new_end = basic.from_normalized(0.6)
        constrained = basic.constrain(new_start, new_end)
        self.assertAlmostEqual(constrained.from_normalized(0), new_start, delta=.01)
        self.assertAlmostEqual(constrained.from_normalized(1), new_end, delta=.01)
        self.assertAlmostEqual(constrained.from_normalized(0.5), basic.from_normalized(0.5), delta=.01)

        advanced = Linear(9, 99)
        advanced.range_start = 1
        advanced.range_end = 10
        new_start = advanced.from_normalized(5)
        new_end = advanced.from_normalized(6)
        constrained = advanced.constrain(new_start, new_end)
        self.assertAlmostEqual(constrained.from_normalized(1), new_start, delta=.01)
        self.assertAlmostEqual(constrained.from_normalized(10), new_end, delta=.01)
        self.assertAlmostEqual(constrained.from_normalized(5.5), advanced.from_normalized(5.5), delta=.01)

