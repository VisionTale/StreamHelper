#!/usr/bin/python3
"""
Application loader.

Handles:
    - flaskenv loading
    - requirement updates for all plugins/macros and main application (if network is available)
    - database upgrade
    - loading WSGI server in production mode
"""

if __name__ == "__main__":
    from sys import path
    path.append('webapi')

    # Load .flaskenv
    from os.path import isfile
    if isfile('.flaskenv'):
        from libs.basics.system import load_export_file
        load_export_file('.flaskenv')

    # Pre-load config
    from libs.config import Config
    config = Config()

    # Install python packages
    from libs.basics.network import is_up
    if is_up("8.8.8.8") or is_up("1.1.1.1"):
        from sys import executable
        from subprocess import check_call
        from os import listdir
        from os.path import isfile, join
        check_call([executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'wheel'])
        check_call([executable, '-m', 'pip', 'install', '--upgrade', '-r', 'requirements.txt'])
        blueprint_path = config.get('webapi', 'plugin_path')
        for blueprint in listdir(blueprint_path):
            requirements_path = join(blueprint_path, blueprint, 'requirements.txt')
            if isfile(requirements_path):
                check_call([executable, '-m', 'pip', 'install', '--upgrade', '-r', requirements_path])
        macro_path = config.get('webapi', 'macro_path')
        for macro in listdir(macro_path):
            requirements_path = join(macro_path, macro, 'requirements.txt')
            if isfile(requirements_path):
                check_call([executable, '-m', 'pip', 'install', '--upgrade', '-r', requirements_path])
    else:
        print("Internet not reachable")

    # Create application
    from webapi import create_app
    webapi = create_app()

    # Start application
    from os import getenv
    if getenv('FLASK_ENV') == 'development':
        webapi.run(
            host=getenv('FLASK_RUN_HOST', '0.0.0.0'),
            port=int(getenv('FLASK_RUN_PORT', '5000')),
            debug=bool(getenv('FLASK_DEBUG', True))
        )
    else:
        from waitress import serve
        serve(
            webapi,
            host=getenv('FLASK_RUN_HOST', '0.0.0.0'),
            port=int(getenv('FLASK_RUN_PORT', '5000'))
        )
