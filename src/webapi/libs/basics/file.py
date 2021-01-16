"""
Library for filesystem operations.
"""


def create_folder(folder_path: str) -> str:
    """
    Create a folder. If the folder cannot be created, administrator rights are requested (only works on linux) and the
    owner of the folder will be set to the current user.

    :param folder_path: path to create
    :raises OSError: if creation fails
    :return:
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
                    raise OSError(error_message)
            else:
                # TODO Help needed for administrator right request on other platforms
                error_message = f"Cannot create {folder_path}. Create the folder by hand and assign current user read" \
                                f" and write rights, start with administrator rights (not recommended) or change the" \
                                f" directory in the config (or via environment variables if supported)"
                raise OSError(error_message)


def create_underlying_folder(filepath: str):
    """
    Uses dirname on filepath, the result will be used as argument to create_folder().

    :param filepath: path to create underlying folder
    :raises OSError: if creation fails
    """
    from os.path import dirname, isdir
    if not isdir(dirname(filepath)):
        create_folder(dirname(filepath))
