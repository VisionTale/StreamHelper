from typing import Tuple, List, Dict, Type
from types import ModuleType

from webapi.libs.config import Config
from webapi.libs.log import Logger

Macros = Dict[str, ModuleType]

macros: Macros = dict()
c: Config = None


# noinspection PyUnresolvedReferences
def get_macros_jinja() -> List[Tuple[str, str]]:
    """
    Returns a list containing of tuples, every tuple contains the lowercase name and the description
    :return: the list of macros
    """
    return [
        (
            key,
            macros[key].description if hasattr(macros[key], 'description') else ""
        )
        for key in list(macros.keys())
    ]


def get_macros() -> Macros:
    """
    Returns all macros. The key is the macro name and the value is the object.
    :return: macro dictionary
    """
    return macros


# noinspection PyUnresolvedReferences
def load_macros(config: Config, logger: Logger):
    """
    Loads all macros.

    It loads all moules from the macro path. All macros need to have the attribute use_module. If it is true, the
    module itself will be loaded as the macro. Otherwise, it needs to have the attribute provides_macros, which is a
    list. If an element in the list is a string, it is assumed to be the name of a class inside the module, and
    module.class is tried to initialize. If it is a class, it will be initialized directly both times without arguments.
    Otherwise, the object will be assumed to be the macro and will be set.

    Within the process, multiple attributes will be set: name (always for modules, only if missing otherwise), config,
    logger.

    After execution, post_load() will be executed if it is a function.

    :param config: the global config object
    :param logger: the global logging object
    """
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
        name = d.lower()
        if name.startswith('streamhelper-'):
            name = name[13:]
        logger.debug(f'Loading macros {name}')
        try:
            macro = import_module(f'{d}')

            _check_attributes(macro, [('use_module', bool)], name)
            if macro.use_module:
                macro.name = name
                macro.config = config
                macro.logger = logger
                macros[name] = macro
                if hasattr(macro, 'post_actions'):
                    macro.post_actions()
            else:
                from inspect import isclass
                _check_attributes(macro, [('provides_macros', list)], name)
                for cl in macro.provides_classes:
                    if type(cl) == str:
                        logger.debug(' -> Loading macro by initializing a object from given class name')
                        if not isclass(getattr(macro, cl)):
                            raise AttributeError(f' -> Passed class name {cl} for macro {name} but class was not found.')
                        macro_object = getattr(macro, cl)()
                    elif isclass(cl):
                        logger.debug(' -> Loading macro by initializing a object from given class')
                        macro_object = cl()
                    else:
                        logger.debug(' -> Loading macro by setting object directly')
                        macro_object = cl

                    macro_object.logger = logger
                    macro_object.config = config
                    if not hasattr(macro_object, 'name'):
                        macro_object.name = cl.__name__
                        logger.debug(f' -> Name assumed to be \'{macro_object.name}\'')
                    macros[macro_object.name] = macro_object
                    if hasattr(macro_object, 'post_load'):
                        logger.debug(' -> Post actions')
                        macro_object.post_load()

            logger.debug(' -> Finished')
        except Exception as e:
            logger.warning(f' -> Loading plugin {name} has failed: {e}')


def _check_attributes(obj: ModuleType, attrs: List[Tuple[str, Type]], name: str):
    """
    Checks if attributes are available and have the right type. Raises an AttributeError if it fails.

    :param obj: object to check for attributes
    :param attrs: attributes list containing tuples where the first element is the name and the second the type
    :param name: name of the object for error message
    """
    for attr, attr_type in attrs:
        if not hasattr(obj, attr):
            raise AttributeError(f' -> Macro {name} misses the attribute {attr}.')
        check_attr_type = type(getattr(obj, attr))
        if not check_attr_type == attr_type:
            raise AttributeError(f' -> Macro {name} has attribute {attr}, but the type is {check_attr_type} and'
                                 f' not {attr_type}')
