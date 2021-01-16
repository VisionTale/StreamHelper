"""
Plugin loader and management.
"""
from typing import Tuple, List, Dict
from types import ModuleType

from shutil import rmtree
from os.path import isdir, join

from flask import Blueprint, request, flash

from libs.config import Config
from libs.log import Logger
from libs.basics.api.response import redirect_or_response
from libs.basics.api.parsing import param, is_set

Plugins = Dict[str, ModuleType]  # {plugin_name: module}
PluginPage = Tuple[str, str, int, str]  # [Page Display Name, Internal Page Route, Sort Nonce, Plugin Name]
PluginPages = List[PluginPage]

plugins: Plugins = dict()
active_plugins: List[str] = list()
plugin_pages: PluginPages = list()
c: Config = None
log: Logger = None


def get_plugin_pages() -> PluginPages:
    """
    Returns all pages from plugins that are currently active as sorted list.

    :return: list of pages
    """
    plugin_pages.sort(key=sort_pages)
    active_plugin_pages = [e for e in plugin_pages if e[3] in get_active_plugins()]
    return active_plugin_pages


def get_active_plugins() -> List[str]:
    """
    Returns a list of names of active plugins.

    :return: list of names
    """
    return active_plugins


def sort_pages(page: PluginPage) -> Tuple[int, str]:
    """
    Sort key. First the numeric priority value is used to sort, afterwards the name.

    :param page: a single page
    :return: the two values by order
    """
    return page[2], page[0]


def get_plugins_jinja() -> List[Tuple[str, str]]:
    """
    Returns a list containing of tuples, every tuple contains the lowercase name and the description

    :return: the list of plugins
    """
    return [
        (
            key,
            plugins[key].description if hasattr(plugins[key], 'description') else ""
        )
        for key in list(plugins.keys())
    ]


def get_plugins() -> Plugins:
    """
    Returns all plugins. The key is the plugin name and the value is the module.

    :return: plugin dictionary
    """
    return plugins


def _load_activated_plugins():
    """
    Loads all activated plugins from the config.
    """
    for plugin in c.get('webapi', 'active_plugins').split(', '):
        if plugin != '':
            active_plugins.append(plugin)


def _save_activated_plugins():
    """
    Saves all activated plugins to the config.
    """
    c.set('webapi', 'active_plugins', ', '.join(active_plugins))


def _activate_plugin(*names: str):
    """
    Activates all given plugins by their name if the name exists.

    :param names: plugin names
    """
    for name in names:
        if name not in active_plugins:
            active_plugins.append(name)
    _save_activated_plugins()


def _deactivate_plugin(*names: str):
    """
    Deactivates all given plugins by their name if the plugin is loaded.

    :param names: plugin names
    """
    for name in names:
        while name in active_plugins:
            active_plugins.remove(name)
    _save_activated_plugins()


def _remove_plugin(*names: str):
    """
    Removes plugins by deactivating them if they are activated, removing their objects and removing the corresponding
    folders.

    :param names: plugin names
    """
    for name in names:
        if name in active_plugins:
            active_plugins.remove(name)
        if name in plugins:
            del plugins[name]
        blueprint_path = c.get('webapi', 'plugin_path')
        if isdir(join(blueprint_path, name)):
            log.warning(f"Removing plugin {name}")
            rmtree(join(blueprint_path, name))
    # TODO Does not work if streamhelper- is cut
    # TODO needs to be added for macros as well


# noinspection PyUnresolvedReferences
def load_plugins(webapi, config: Config, logger: Logger):
    """
    Loads all plugins.

    Any folder located in config.get('webapi', 'plugin_path') is tried to import as module except of __pycache__.

    If a plugin's folder starts with 'streamhelper-' (case insensitive), this part will be removed in the plugin name.

    All plugins need to have a set_blueprint(blueprint: flask.Blueprint) function, which should be responsible for
    setting the blueprint. Routes and other things shall not be defined before the blueprint is set.

    Within the process, multiple attributes will be set: name, config, logger.

    The given blueprint will have the static and templates folder set at the root of the module, the name is the folder
    name in lowercase (the prefix 'streamhelper-' will be stripped, see above) and the url_prefix will be the name, so
    a plugin called 'test' will have it routes below '/test'.

    After execution, plugin.exec_post_actions() may be called, which invokes the function post_loading_actions() on all
    plugins if available. No order implied.

    :param webapi: the applications flask object
    :param config: the global config object
    :param logger:the global logging object
    """
    global c, log
    c = config
    log = logger

    from os import listdir
    from os.path import isdir, join, basename, dirname
    from importlib import import_module
    from sys import path

    blueprint_path = config.get('webapi', 'plugin_path')
    path.append(dirname(blueprint_path.rstrip('/')))
    blueprints = import_module(basename(blueprint_path.rstrip('/')))
    logger.info(f'Searching plugins in {blueprint_path}')
    for d in listdir(blueprint_path):
        if not isdir(join(blueprint_path, d)) or d == '__pycache__':
            continue

        name = d.lower()
        if name.startswith('streamhelper-'):
            name = name[13:]
        logger.debug(f'Loading plugin {name}')
        try:
            plugin = import_module(f'.{d}', package=blueprints.__package__)

            attr = 'set_blueprint'
            if not hasattr(plugin, attr):
                raise AttributeError(f'Plugin {name} misses the attribute {attr}.')
            from inspect import isfunction
            if not isfunction(getattr(plugin, attr)):
                raise AttributeError(f'Plugin {name} has the attribute {attr}, but it\'s not a function.')

            plugin.name = name
            plugin.config = config
            plugin.logger = logger
            blueprint = Blueprint(
                name,
                name,
                template_folder=join(blueprint_path, d, 'templates'),
                static_folder=join(blueprint_path, d, 'static'),
                url_prefix=f'/{name}'
            )
            plugin.set_blueprint(blueprint)
            plugins[name] = plugin

            webapi.register_blueprint(blueprint)
            if hasattr(plugin, 'provides_pages'):
                for page in plugin.provides_pages:
                    plugin_pages.append(
                        (
                            page[0],
                            f'{plugin.name}.{page[1]}',
                            page[2] if len(page) > 2 else 1000,
                            name
                        )
                    )

            logger.debug(' -> Finished')
        except Exception as e:
            logger.warning(f' -> Loading plugin {name} has failed: {e}')

    # Load active plugin list and remove unavailable plugins
    _load_activated_plugins()
    for plugin in active_plugins.copy():
        if plugin not in list(plugins.keys()):
            _deactivate_plugin(plugin)

    @webapi.route('/activate_plugin')
    def activate_plugin():
        """
        Activates a plugin. At the time, activation and deactivation of plugins only affects the active_plugin() method
        used by the frontend, and does not unload the plugin. TODO Real load/unload

        Arguments:
            - name

        :return: redirect if redirect_url was passed, otherwise response
        """
        plugin_name = param('name')
        if not is_set(plugin_name):
            return redirect_or_response(400, 'Missing parameter name')

        _activate_plugin(plugin_name)
        return redirect_or_response(200, 'Success')

    @webapi.route('/deactivate_plugin', methods=['GET', 'POST'])
    def deactivate_plugin():
        """
        Deactivates a plugin. At the time, activation and deactivation of plugins only affects the active_plugin()
        method used by the frontend, and does not unload the plugin. TODO Real load/unload

        Takes name as an argument. 400 response if missing.

        :return: redirect or response
        """
        plugin_name = param('name')
        if not is_set(plugin_name):
            return redirect_or_response(400, 'Missing parameter name')

        _deactivate_plugin(plugin_name)
        return redirect_or_response(200, 'Success')

    @webapi.route('/remove_plugin')
    def remove_plugin():
        """
        Removes a plugin completely. If flask does not auto reload, the application may need to be restarted for the
        changes to take effect.

        Arguments:
            - name

        :return: redirect if redirect_url was passed, otherwise response
        """
        plugin_name = param('name')
        if not is_set(plugin_name):
            return redirect_or_response(400, 'Missing parameter name')

        _remove_plugin(plugin_name)
        return redirect_or_response(200, 'Success')


# noinspection PyUnresolvedReferences
def exec_post_actions():
    """
    Execute post_loading_actions() on all plugins that implement the function. No order implied.
    """
    from inspect import isfunction
    for plugin in plugins.values():
        if hasattr(plugin, 'post_loading_actions') and isfunction(plugin.post_loading_actions):
            log.debug(f'Running post loading actions for {plugin.name}')
            plugin.post_loading_actions()
