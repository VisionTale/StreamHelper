"""
Helper files for JQuery.
"""

from webapi import config, static_folder
from . import debug_print

jquery_version = config.get('webapi', 'jquery_version')


def download_jquery(version: str, verbose: bool = True):
    """
    Downloads the jquery javascript and map files.

    :param version: jquery version
    :param verbose: whether to print information, defaults to true.
    """
    from os.path import isdir, isfile, join

    jquery_dir = join(static_folder, 'jquery')
    if not isdir(jquery_dir) or not isfile(join(jquery_dir, f'jquery-{version}.min.js')):
        debug_print("Downloading jquery files..", verbose)

        from os import mkdir
        mkdir(jquery_dir)

        js_url = f'https://code.jquery.com/jquery-{version}.min.js'
        map_url = f'https://code.jquery.com/jquery-{version}.min.map'

        debug_print(f'Download urls: {js_url} + {map_url}', verbose)

        from requests import get
        js_request = get(js_url)
        map_request = get(map_url)

        js_fp = join(jquery_dir, f'jquery-{version}.min.js')
        map_fp = join(jquery_dir, f'jquery-{version}.min.map')

        with open(js_fp, 'wb') as f:
            f.write(js_request.content)

        with open(map_fp, 'wb') as f:
            f.write(map_request.content)

        debug_print("Done!", verbose)


def get_jquery_version():
    """
    Get the installed jquery version.

    :return: jquery version
    """
    return jquery_version
