"""
Helper files for Fontawesome.
"""


def download(version: str, static_folder: str, verbose: bool = True):
    """
    Downloads the fontawesome files.

    Does not execute if folder already exists.

    :param version: ace version
    :param static_folder: folder for flasks static files
    :param verbose: whether to print information, defaults to true.
    :exception OSError: os.remove, requests.get, open, TextIOWrapper.write, ZipFile, ZipFile.extractall
    """
    from . import debug_print, download_and_unzip_archive
    from os.path import isdir, join

    fontawesome_dir = join(static_folder, f'fontawesome-free-{version}-web')
    if not isdir(fontawesome_dir):
        debug_print("Downloading fontawesome files..", verbose)
        url = f'https://github.com/FortAwesome/Font-Awesome/releases/download/{version}/' \
              f'fontawesome-free-{version}-web.zip'
        debug_print(f'Download url: {url}', verbose)

        zip_file_fp = join(static_folder, f'fontawesome-free-{version}-web.zip')
        download_and_unzip_archive(url, zip_file_fp, static_folder, verbose=verbose)

        debug_print("Done!", verbose)


def get_fontawesome_version():
    """
    Get the installed fontawesome version.

    :return: fontawesome version
    """
    from webapi import config
    return config.get('webapi', 'fontawesome_version')
