"""
Helper files for Ace.
"""


def download(version: str, static_folder: str, verbose: bool = True):
    """
    Downloads the ace files.

    Does not execute if folder already exists.

    :param version: ace version
    :param static_folder: folder for flasks static files
    :param verbose: whether to print information, defaults to true.
    :exception OSError: os.remove, requests.get, open, TextIOWrapper.write, ZipFile, ZipFile.extractall
    """
    from . import debug_print, download_and_unzip_archive
    from os.path import isdir, join

    ace_dir = join(static_folder, f'ace-builds-{version}')
    if not isdir(ace_dir):
        debug_print("Downloading ace files..", verbose)
        url = f'https://github.com/ajaxorg/ace-builds/archive/v{version}.zip'
        debug_print(f'Download url: {url}', verbose)

        zip_file_fp = join(static_folder, f'v{version}.zip')
        download_and_unzip_archive(url, zip_file_fp, static_folder, verbose=verbose)

        debug_print("Done!", verbose)


def get_ace_version():
    """
    Get the installed ace version.

    :return: ace version
    """
    from webapi import config
    return config.get('webapi', 'ace_version')
