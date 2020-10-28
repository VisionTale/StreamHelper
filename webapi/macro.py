from flask import Blueprint, request
from webapi.libs.config import Config
from webapi.libs.log import Logger

macros = dict()
c: Config = None


def sort_pages(page: tuple) -> tuple:
    return page[2], page[0]


def get_macros_jinja() -> list:
    return [
        (
            key,
            key.capitalize(),
            macros[key].description if hasattr(macros[key], 'description') else ""
        )
        for key in list(macros.keys())
    ]


def get_macros() -> dict:
    return macros


def load_macros(webapi, config: Config, logger: Logger) -> dict:
    global c
    c = config

    from os import listdir
    from os.path import isdir, join
    from importlib import import_module
    from sys import path

    macro_path = config.get('webapi', 'macro_path')
    path.append(macro_path)
    logger.info(f'Searching macros in {macro_path}')
    for d in listdir(macro_path):
        if not isdir(join(macro_path, d)) or d == '__pycache__':
            continue
        logger.debug(f'Loading macros {d}')
        try:
            macro = import_module(f'{d}')

            attrs = []
            for attr in attrs:
                if not hasattr(macro, attr):
                    raise AttributeError(f'Plugin {d} misses the attribute {attr}, which is expected by the framework.')

            macro.name = d
            macro.config = config
            macro.logger = logger
            macros[d] = macro

            if hasattr(macro, 'post_loading_actions'):
                logger.debug('Running post loading actions')
                macro.post_loading_actions()

            logger.debug('Finished')
        except Exception as e:
            logger.warning(f'Loading plugin {d} has failed: {e}')
