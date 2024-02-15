#!/usr/bin/env python3
"""
simple_simulator is a 4 dimensional space to fit to the 4 dimensional function in groundtruth
The correct calibration should be 10,4,5,3
good ranges are a(0,20), b (0,8) ,c(0,10) and d(0,6)
there is an optional 9th parameter if you want to add an artificial delay to the simulation
"""

from math import sin, log
from sys import argv
from time import sleep
import json
with open(argv[1]) as json_data:
    jdata = json.loads(json_data)
    json_data.close()
x = float(argv[2])
y = float(argv[3])
z = float(argv[4])
w = float(argv[5])

a = jdata["a"]
b = jdata["b"]
c = jdata["c"]
d = jdata["d"]
print(f"""f(x,y,z,w)=
    {a / 100} * (x - {(b / 4)}) * (x - {c / 5 * 2}) * (x - {d}) * (x - {a / 10 * 6})
    - {(b / 400)} * (y + {c / 5}) * (y - {d}) * (y - {b}) * (y - {(a / 2)}) * (y - {(a / 2)}) * (y - {(b * 2)})  * (-log(y))
    + {c * 2} * sin({d * 2 / 3} * z) / (z + 1)
    + {d * 5 / 3} * sin({c / 5 * 3} * w+1) / (w + 1)
    + {a * 2}
    """
      )
if len(argv) > 5:
    sleep(float(argv[9]))
with open("results.txt", "w") as file:
    file.write(str(
        a / 100 * (x - (b / 4)) * (x - c / 5 * 2) * (x - d) * (x - a / 10 * 6)
        - (b / 400) * (y + c / 5) * (y - d) * (y - b) * (y - (a / 2)) * (y - (a / 2)) * (y - (b * 2)) * (-log(y))
        + c * 2 * sin(d * 2 / 3 * z) / (z + 1)
        + d * 5 / 3 * sin(c / 5 * 3 * w + 1) / (w + 1)
        + a * 2
    ))
