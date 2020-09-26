#!/usr/bin/python3

from os import environ


def load_export_file(file_path):
    with open(file_path, 'r') as f:
        for line in f.readlines():
            if line.startswith('export '):
                var, value = line.rstrip().split(' ')[-1].split('=')[0:2]
                environ[var] = str(value)
