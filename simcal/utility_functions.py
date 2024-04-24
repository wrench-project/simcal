import math
import subprocess
from typing import Dict

from simcal.exceptions import Timeout


def bash(command, args=None, std_in=None, cwd=None, env: Dict[str, str] | None = None, timeout=None):
    cmd_list = [command]
    for arg in args:
        cmd_list.append(str(arg))
    # print(cmd_list)
    process = subprocess.Popen(cmd_list,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True,
                               cwd=cwd,
                               env=env)
    try:
        if std_in is not None:
            stdout, stderr = process.communicate(input=std_in, timeout=timeout)
        else:
            stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        process.kill()
        raise Timeout()

    return_code = process.returncode
    return stdout, stderr, return_code


def safe_exp2(x):
    if x > 1023:
        x = 1023
    return math.pow(2, x)
