import csv
from collections import defaultdict


def bash(command, args=None, std_in=None):
    pass


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
