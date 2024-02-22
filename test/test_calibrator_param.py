from simcal.calibrator_param import *


def test_LinearParam():
    basic = LinearParam(10, 100)
    advanced = LinearParam(9, 99)
    advanced.range_start = 1
    advanced.range_end = 10
    formatted = LinearParam(0, 100).format("%f formatted")
    basic.from_normalized(0.5)
    advanced.from_normalized(0.5)
    formatted.from_normalized(0.5)


def test_all():
    test_LinearParam()


if __name__ == "__main__":
    test_all()
