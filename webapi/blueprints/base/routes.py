from os import remove
from os.path import join, basename, dirname
from zipfile import ZipFile
from time import sleep

from flask import render_template, request, redirect, flash, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename

from . import bp


def _allowed_file(filename):
    """
    Checks if the the filename belongs to a zip file.

    :param filename: filename to check
    :return: boolean value
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['zip']


def _extract_blueprint_zip(filepath, delete=False):
    """
    Extracts a blueprint from a zip.

    If the zip contains multiple files at root level, the name of the zip determines the name of the folder.

    :param filepath: path to the zip file
    :param delete: whether to delete the zip after extraction
    :return:
    """
    # Basic error checks
    if not filepath.endswith('.zip'):
        raise FileNotFoundError('Given file seems to be no zip file. (Missing extension)')
    from os.path import isfile, isdir
    if not isfile(filepath) or isdir(filepath):
        raise FileNotFoundError('Given file seems to be no file.')

    # Extraction
    with ZipFile(filepath, 'r') as zip_file:
        extract_filepath = dirname(filepath)
        org_extract_filepath = extract_filepath
        filename_without_ext = '.'.join(basename(filepath).split('.')[:-1]).lower()
        files = [f.filename.lower() for f in zip_file.filelist]
        # Ensuring files will not be packed out without a directory name, using the zips name in case of doubt
        if '/' not in files[0]:
            extract_filepath = join(extract_filepath, filename_without_ext)
        else:
            prefix = files[0].split('/')[0]
            for f in files:
                # TODO Check if separator within zip differs for Windows implementation of zipfile
                if not f.startswith(f'{prefix}/'):
                    extract_filepath = join(extract_filepath, filename_without_ext)
                    break
        # Remove old directory if present, replacing with new one TODO Dangerous?
        if extract_filepath == org_extract_filepath:
            if isdir(join(extract_filepath, prefix)):
                from shutil import rmtree
                rmtree(join(extract_filepath, prefix), ignore_errors=True)
        else:
            if isdir(join(extract_filepath, filename_without_ext)):
                from shutil import rmtree
                rmtree(join(extract_filepath, filename_without_ext), ignore_errors=True)
        zip_file.extractall(extract_filepath)

    # Delete zip file after completion if requested
    if delete:
        remove(filepath)

    # Return the name of the directory containing the files
    if extract_filepath == org_extract_filepath:
        return prefix
    else:
        return filename_without_ext


def _install_dependencies(blueprint_name) -> bool:
    """
    Installs the dependencies from a single blueprint's requirements.txt

    :param blueprint_name: name of the blueprint
    :return: Whether an installation happened
    """
    from . import config
    from os.path import isfile
    from subprocess import check_call
    from sys import executable
    blueprint_path = config.get('webapi', 'plugin_path')
    requirements_path = join(blueprint_path, blueprint_name, 'requirements.txt')
    if isfile(requirements_path):
        check_call([executable, '-m', 'pip', 'install', '--upgrade', '-r', requirements_path])
        return True
    else:
        return False


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    Renders the dashboard.

    :return:
    """
    return render_template('dashboard.html')


@bp.route('/install', methods=['POST'])
@login_required
def install():
    """
    Install a given zip containing a blueprint.

    The files argument name for the blueprint must be 'plugin'.

    :return:
    """
    from . import logger
    if request.method == 'POST':
        if 'plugin' not in request.files:
            flash('No file part')
            return redirect(url_for('base.dashboard'))
        file = request.files['plugin']
        logger.debug(f'Uploading file {file}')
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('base.dashboard'))
        if file and _allowed_file(file.filename):
            logger.debug('-> Filename accepted')
            from . import config
            filename = secure_filename(file.filename)
            filepath = join(config.get('webapi', 'plugin_path'), filename)
            logger.debug(f'-> Saving location: {filepath}')
            file.save(filepath)
            logger.debug('-> File saved')
            name = _extract_blueprint_zip(filepath=filepath, delete=True)
            logger.debug('-> Files extracted')
            _install_dependencies(name)
            logger.debug('-> Dependencies installed')

            sleep(2)
            return redirect(url_for('base.dashboard'))
    return redirect(url_for('base.dashboard'))


@bp.route('/ping')
def ping():
    """
    Simple ping, returns an empty HTTP 200 response.

    :return:
    """
    return "", 200
