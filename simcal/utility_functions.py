import subprocess
import math

# TODO move to env
def bash(command, args=None, std_in=None):
    cmd_list = [command]
    if args:
        cmd_list += args

    process = subprocess.Popen(cmd_list,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

    if std_in is not None:
        stdout, stderr = process.communicate(input=std_in)
    else:
        stdout, stderr = process.communicate()

    return_code = process.returncode
    return stdout, stderr, return_code


def safe_exp2(x):
    if x > 1023:
        x = 1023
    return math.pow(2, x)
