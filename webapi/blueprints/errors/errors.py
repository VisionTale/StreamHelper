from flask import render_template, request
from webapi import db
from . import bp


def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']


@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return
    return render_template('404.html'), 404


@bp.app_errorhandler(500)
def internal_system_error(error):
    db.session.rollback()
    if wants_json_response():
        return
    return render_template('500.html'), 500


@bp.app_errorhandler(418)
def i_am_a_teapot(error):
    return render_template('418.html'), 418

