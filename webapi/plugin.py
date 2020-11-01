from typing import Tuple, List, Dict
from types import ModuleType

from shutil import rmtree
from os.path import isdir, join

from flask import Blueprint, request, flash

from webapi.libs.config import Config
from webapi.libs.log import Logger
from webapi.libs.api.response import redirect_or_response

Plugins = Dict[str, ModuleType]
PluginPage = Tuple[str, str, int, str]
PluginPages = List[PluginPage]

plugins: Plugins = dict()
active_plugins: List[str] = list()
plugin_pages: PluginPages = list()
c: Config = None
l: Logger = None


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
            l.warning(f"Removing plugin {name}")
            rmtree(join(blueprint_path, name))
    # TODO Does not work if streamhelper- is cut
    # TODO needs to be added for macros aswell


# noinspection PyUnresolvedReferences
def load_plugins(webapi, config: Config, logger: Logger) -> dict:
    global c, l
    c = config
    l = logger

    from os import listdir
    from os.path import isdir, join
    from importlib import import_module
    from sys import path

    blueprint_path = config.get('webapi', 'plugin_path')
    path.append(blueprint_path)
    logger.info(f'Searching plugins in {blueprint_path}')
    for d in listdir(blueprint_path):
        if not isdir(join(blueprint_path, d)) or d == '__pycache__':
            continue
        name = d.lower()
        if name.startswith('streamhelper-'):
            name = name[13:]
        logger.debug(f'Loading plugin {name}')
        try:
            plugin = import_module(f'{d}')

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

            logger.debug('Finished')
        except Exception as e:
            logger.warning(f'Loading plugin {name} has failed: {e}')

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
        :return: redirect if redirect_url was passed, otherwise response
        """
        redirect_url = request.args.get('redirect_url')
        name = request.args.get('name')

        if not name or name == '':
            flash('Missing parameter name')
            return redirect_or_response(request, 400, redirect_url, 'Missing parameter name')

        _activate_plugin(name)
        return redirect_or_response(request, 200, redirect_url, 'Success')

    @webapi.route('/deactivate_plugin')
    def deactivate_plugin():
        """
        Deactivates a plugin. At the time, activation and deactivation of plugins only affects the active_plugin()
        method used by the frontend, and does not unload the plugin. TODO Real load/unload
        :return: redirect if redirect_url was passed, otherwise response
        """
        redirect_url = request.args.get('redirect_url')
        name = request.args.get('name')

        if not name or name == '':
            flash('Missing parameter name')
            return redirect_or_response(request, 400, redirect_url, 'Missing parameter name')

        _deactivate_plugin(name)
        return redirect_or_response(request, 200, redirect_url, 'Success')

    @webapi.route('/remove_plugin')
    def remove_plugin():
        """
        Removes a plugin completely. If flask does not auto reload, the application may need to be restartet for the
        changes to take effect.
        :return: redirect if redirect_url was passed, otherwise response
        """
        redirect_url = request.args.get('redirect_url')
        name = request.args.get('name')

        if not name or name == '':
            flash('Missing parameter name')
            return redirect_or_response(request, 400, redirect_url, 'Missing parameter name')

        _remove_plugin(name)
        return redirect_or_response(request, 200, redirect_url, 'Success')
