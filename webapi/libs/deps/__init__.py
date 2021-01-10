"""
Dependency management package.
"""


def debug_print(message: str, verbose: bool):
    """
    Print if verbose is set to true.

    :param message: message to print
    :param verbose: whether to print
    :return:
    """
    if verbose:
        print(message)


def download_and_unzip_archive(url: str, zip_file_fp: str, remove: bool = True, verbose: bool = True):
    """
    Downloads and unzips an archive.

    :param url: url to request
    :param zip_file_fp: filepath for zip
    :param remove: whether to remove the zip after unpacking, defaults to true.
    :param verbose: whether to print information, defaults to true.
    :exception OSError: os.remove, requests.get, open, TextIOWrapper.write, ZipFile, ZipFile.extractall
    """
    from requests import get
    r = get(url)
    debug_print("Saving archive..", verbose)
    with open(zip_file_fp, 'wb') as f:
        f.write(r.content)
    debug_print("Extracting..", verbose)
    from zipfile import ZipFile
    with ZipFile(zip_file_fp, 'r') as zip_file:
        zip_file.extractall(static_folder)
    if remove:
        debug_print("Removing archive..", verbose)
        from os import remove
        remove(zip_file_fp)
