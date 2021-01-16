"""
Library for OS operations.
"""

from logging import Logger


def parse_export_file(file_path: str) -> None:
    """
    Load exports from a shell file. Every line starting with export will be included into environment.

    Silently fails if file is missing.

    :param file_path: file to check for export statements
    """

    from os import environ
    from os.path import isfile

    if not isfile(file_path):
        return

    with open(file_path, 'r') as f:
        for line in f.readlines():
            if line.startswith('export '):
                var, value = line[7:].replace(' ', '').rstrip().split('=')
                environ[var] = str(value)


def add_to_path(folder: str) -> None:
    """
    Add a folder to the current library path.

    :param folder: filepath to folder
    :return:
    """
    from sys import path
    from os.path import join, dirname, isabs
    if isabs(folder):
        path.append(folder)
    else:
        path.append(join(dirname(__file__), folder))


def is_pip_installed() -> bool:
    """
    Checks whether pip is installed for the current python interpreter

    :return: true if pip is available
    """
    from subprocess import run, DEVNULL, STDOUT
    from sys import executable
    process = run(f'{executable} -m pip --version', check=False, stdout=DEVNULL, stderr=STDOUT, shell=True)
    return process.returncode == 0
