import math
import os
import subprocess
from typing import Dict, Any, Tuple

from simcal.exceptions import Timeout


def bash(command, args: list[Any] | None = None, std_in: str | None = None, cwd: str | os.PathLike | None = None,
         env: Dict[str, str] | None = None,
         timeout: int | float | None = None) -> Tuple[str, str, int]:
    """
    A method to invoke an executable using the Shell
    :param command: the executable name
    :param args: the command-line arguments
    :param std_in: standard input (e.g., subprocess.PIPE)
    :param cwd: a working directory
    :param env: environment variables
    :param timeout: time limit in seconds
    :return:
    """
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


def safe_exp2(x: int | float) -> float:
    if x > 1023:
        x = 1023
    return math.pow(2, x)
