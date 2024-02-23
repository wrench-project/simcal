import csv
import math
from collections import defaultdict


def bash(command, args=None, std_in=None):
    pass


# return stdout, stderr, exit code, throw if needed
# maybe momve to env

def parse_csv(file):
    stats = defaultdict(list)
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [field.strip() for field in reader.fieldnames]
        for row in reader:
            machine = row['machine.name']
            runtime = float(row['job.end']) - float(row['job.start'])
            stats[machine].append(runtime)
    return stats


def safe_exp2(x):
    if x > 1023:
        x = 1023
    return math.pow(2, x)
