"""
Library for OS operations.
"""

from logging import Logger


def create_folder(folder_path: str, logger: Logger = None):
    """
    Create a folder. If the folder cannot be created, administrator rights are requested (only works on linux) and the
    owner of the folder will be set to the current user.

    :param folder_path: path to create
    :param logger: logger object to log to
    """

    from sys import platform, stderr
    from os.path import isdir
    from subprocess import run
    from getpass import getuser
    from pathlib import Path

    if not isdir(folder_path):
        try:
            Path(folder_path).mkdir(parents=True, exist_ok=True)
        except PermissionError:
            if platform == 'linux':
                process = run('pkexec sh -c "mkdir -p %s && chown -R %s %s"' % (folder_path, getuser(), folder_path),
                              shell=True, executable='/bin/bash', capture_output=True)
                if process.returncode != 0:
                    error_message = f"Folder {folder_path} cannot be created: {process.stderr.decode('ascii')}"
                    if logger:
                        logger.fatal(error_message)
                    else:
                        print(error_message, file=stderr)
            else:
                # TODO Help needed for administrator right request on other platforms
                error_message = f"Cannot create {folder_path}. Create the folder by hand and assign current user read" \
                                f" and write rights, start with administrator rights (not recommended) or change the" \
                                f" directory in the config (or via environment variables if supported)"
                if logger:
                    logger.fatal(error_message)
                else:
                    print(error_message, file=stderr)


def create_underlying_folder(filepath: str, logger: Logger = None):
    """
    Uses dirname on filepath, the result will be used as argument to create_folder().

    :param filepath: path to create underlying folder
    :param logger: logger object to log to
    """
    from os.path import dirname
    create_folder(dirname(filepath), logger)


def load_export_file(file_path: str):
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
