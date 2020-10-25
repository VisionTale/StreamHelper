from flask import Blueprint, request
from webapi.libs.config import Config
from webapi.libs.log import Logger

plugins = dict()
active_plugins = list()
plugin_pages = list()
c: Config = None


def get_plugin_pages() -> list:
    plugin_pages.sort(key=sort_pages)
    active_plugin_pages = [e for e in plugin_pages if e[3] in active_plugins]
    return active_plugin_pages


def get_active_plugins() -> list:
    return active_plugins


def sort_pages(page: tuple) -> tuple:
    return page[2], page[0]


def get_plugins() -> list:
    return [
        (
            key,
            key.capitalize(),
            plugins[key].description if hasattr(plugins[key], 'description') else ""
        )
        for key in list(plugins.keys())
    ]


def _load_activated_plugins():
    for plugin in c.get('webapi', 'active_plugins').split(', '):
        if plugin != '':
            active_plugins.append(plugin)


def _save_activated_plugins():
    c.set('webapi', 'active_plugins', ', '.join(active_plugins))


def _activate_plugin(*names: str):
    for name in names:
        if name not in active_plugins:
            active_plugins.append(name)
    _save_activated_plugins()


def _deactivate_plugin(*names: str):
    for name in names:
        while name in active_plugins:
            active_plugins.remove(name)
    _save_activated_plugins()


def load_plugins(webapi, config: Config, logger: Logger) -> dict:
    global c
    c = config

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
        logger.debug(f'Loading plugin {d}')
        try:
            plugin = import_module(f'{d}')

            attrs = ['set_blueprint']
            for attr in attrs:
                if not hasattr(plugin, attr):
                    raise AttributeError(f'Plugin {d} misses the attribute {attr}, which is expected by the framework.')

            plugin.name = d
            plugin.config = config
            plugin.logger = logger
            blueprint = Blueprint(
                d,
                d,
                template_folder=join(blueprint_path, d, 'templates'),
                static_folder=join(blueprint_path, d, 'static'),
                url_prefix=f'/{d}'
            )
            plugin.set_blueprint(blueprint)
            plugins[d] = plugin

            webapi.register_blueprint(blueprint)
            if hasattr(plugin, 'provides_pages'):
                for page in plugin.provides_pages:
                    plugin_pages.append((page[0], f'{plugin.name}.{page[1]}', page[2] if len(page) > 2 else 1000, d))

            logger.debug('Finished')
        except Exception as e:
            logger.warning(f'Loading plugin {d} has failed: {e}')

    # Load active plugin list and remove unavailable plugins
    _load_activated_plugins()
    for plugin in active_plugins.copy():
        if plugin not in list(plugins.keys()):
            _deactivate_plugin(plugin)

    @webapi.route('/activate_plugin')
    def activate_plugin():
        if 'name' not in request.args:
            return "Missing parameter name", 400
        name = request.args.get('name')
        if name == '':
            return "Missing parameter name", 400
        _activate_plugin(name)
        return "Success", 200

    @webapi.route('/deactivate_plugin')
    def deactivate_plugin():
        if 'name' not in request.args:
            return "Missing parameter name", 400
        name = request.args.get('name')
        if name == '':
            return "Missing parameter name", 400
        _deactivate_plugin(name)
        return "Success", 200
