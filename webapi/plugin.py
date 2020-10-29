from shutil import rmtree
from os.path import isdir, join

from flask import Blueprint, request, flash

from webapi.libs.config import Config
from webapi.libs.log import Logger
from webapi.libs.api.response import redirect_or_response

plugins = dict()
active_plugins = list()
plugin_pages = list()
c: Config = None
l: Logger = None


def get_plugin_pages() -> list:
    plugin_pages.sort(key=sort_pages)
    active_plugin_pages = [e for e in plugin_pages if e[3] in active_plugins]
    return active_plugin_pages


def get_active_plugins() -> list:
    return active_plugins


def sort_pages(page: tuple) -> tuple:
    return page[2], page[0]


def get_plugins_jinja() -> list:
    return [
        (
            key,
            key.capitalize(),
            plugins[key].description if hasattr(plugins[key], 'description') else ""
        )
        for key in list(plugins.keys())
    ]


def get_plugins() -> dict:
    return plugins


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


def _remove_plugin(*names: str):
    for name in names:
        if name in active_plugins:
            active_plugins.remove(name)
        if name in plugins:
            del plugins[name]
        blueprint_path = c.get('webapi', 'plugin_path')
        if isdir(join(blueprint_path, name)):
            l.warning(f"Removing plugin {name}")
            rmtree(join(blueprint_path, name))


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
        d_name = d.lower()
        if d_name.startswith('streamhelper-'):
            d_name = d_name[13:]
        logger.debug(f'Loading plugin {d_name}')
        try:
            plugin = import_module(f'{d}')

            attrs = ['set_blueprint']
            for attr in attrs:
                if not hasattr(plugin, attr):
                    raise AttributeError(f'Plugin {d_name} misses the attribute {attr}, which is expected by the '
                                         f'framework.')

            plugin.name = d_name
            plugin.config = config
            plugin.logger = logger
            blueprint = Blueprint(
                d_name,
                d_name,
                template_folder=join(blueprint_path, d, 'templates'),
                static_folder=join(blueprint_path, d, 'static'),
                url_prefix=f'/{d_name}'
            )
            plugin.set_blueprint(blueprint)
            plugins[d_name] = plugin

            webapi.register_blueprint(blueprint)
            if hasattr(plugin, 'provides_pages'):
                for page in plugin.provides_pages:
                    plugin_pages.append(
                        (
                            page[0],
                            f'{plugin.name}.{page[1]}',
                            page[2] if len(page) > 2 else 1000,
                            d_name
                        )
                    )

            if hasattr(plugin, 'post_loading_actions'):
                logger.debug('Running post loading actions')
                plugin.post_loading_actions()

            logger.debug('Finished')
        except Exception as e:
            logger.warning(f'Loading plugin {d_name} has failed: {e}')

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
