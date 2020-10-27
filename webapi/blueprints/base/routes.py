from os import remove
from os.path import join, basename, dirname
from zipfile import ZipFile
from time import sleep

from flask import render_template, request, redirect, flash, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename

from . import bp


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['zip']


def extract_blueprint_zip(filepath, delete=False):
    with ZipFile(filepath, 'r') as zip_file:
        extract_filepath = dirname(filepath)
        filename_without_ext = '.'.join(basename(filepath).split('.')[:-1])
        files = [f.filename for f in zip_file.filelist]
        for f in files:
            # TODO Check if separator differs for Windows implementation of zipfile
            if not f.startswith(f'{filename_without_ext}/'):
                extract_filepath = join(extract_filepath, f'{filename_without_ext}')
                break
        zip_file.extractall(extract_filepath)
    if delete:
        remove(filepath)


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@bp.route('/install', methods=['POST'])
@login_required
def install():
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
        if file and allowed_file(file.filename):
            logger.debug('-> Filename accepted')
            from . import config
            filename = secure_filename(file.filename)
            filepath = join(config.get('webapi', 'plugin_path'), filename)
            logger.debug(f'-> Saving location: {filepath}')
            file.save(filepath)
            logger.debug('-> File saved')
            extract_blueprint_zip(filepath=filepath, delete=True)
            logger.debug('-> Files extracted')
            sleep(2)
            return redirect(url_for('base.dashboard'))
    return redirect(url_for('base.dashboard'))


@bp.route('/ping')
def ping():
    return "", 200
