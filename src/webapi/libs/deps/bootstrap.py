"""
Helper files for Bootstrap.
"""


def download(version: str, static_folder: str, verbose: bool = True):
    """
    Downloads the bootstrap dist files.

    Does not execute if folder already exists.

    :param version: bootstrap version
    :param static_folder: folder for flasks static files
    :param verbose: whether to print information, defaults to true.
    """
    from . import debug_print, download_and_unzip_archive
    from os.path import isdir, join

    bootstrap_dir = join(static_folder, f'bootstrap-{version}-dist')
    if not isdir(bootstrap_dir):
        debug_print("Downloading bootstrap files..", verbose)
        url = f'https://github.com/twbs/bootstrap/releases/download/v{version}/bootstrap-{version}-dist.zip'
        debug_print(f'Download url: {url}', verbose)

        zip_file_fp = join(static_folder, 'bootstrap.zip')
        download_and_unzip_archive(url, zip_file_fp, static_folder, verbose=verbose)

        debug_print("Done!", verbose)


def get_bootstrap_version():
    """
    Get the installed bootstrap version.

    :return: bootstrap version
    """
    from webapi import config
    return config.get('webapi', 'bootstrap_version')
