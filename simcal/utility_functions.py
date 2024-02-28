
import math


def bash(command, args=None, std_in=None):
    pass


def safe_exp2(x):
    if x > 1023:
        x = 1023
    return math.pow(2, x)
