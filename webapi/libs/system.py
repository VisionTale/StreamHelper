from logging import Logger


def create_folder(folder_path, logger: Logger):
    """
    Create a folder. If the folder cannot be created, administrator rights are requested (only works on linux) and the
    owner of the folder will be set to the current user.
    :param logger: logger object to log to
    :param folder_path: path to create
    :return:
    """

    from sys import platform
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
                    logger.fatal(f"Folder {folder_path} cannot be created: {process.stderr.decode('ascii')}")
            else:
                # TODO Help needed for administrator right request on other platforms
                logger.fatal(f"Cannot create {folder_path}. Create the folder by hand and assign current user read and "
                             f"write rights, start with administrator rights (not recommended) or change the directory"
                             f"in the config (or via environment variables if supported)")


def load_export_file(file_path):
    """
    Load exports from a shell file. Every line starting with export will be included into environment.
    :param file_path: file to check for export statements
    :return:
    """

    from os import environ

    with open(file_path, 'r') as f:
        for line in f.readlines():
            if line.startswith('export '):
                var, value = line.rstrip().split(' ')[-1].split('=')[0:2]
                environ[var] = str(value)
