from flask import render_template, request

from . import bp

from webapi import db
from webapi.libs.api.response import response

def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']


@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return response(404, "Not found")
    return render_template('404.html'), 404


@bp.app_errorhandler(500)
def internal_system_error(error):
    db.session.rollback()
    if wants_json_response():
        return response(500, "Internal server error")
    return render_template('500.html'), 500


@bp.app_errorhandler(418)
def i_am_a_teapot(error):
    if wants_json_response():
        return response(418, "May the teapot be with you")
    return render_template('418.html'), 418


@bp.app_errorhandler(400)
def bad_request(error):
    if wants_json_response():
        return response(418, f"Bad request: {error}")
    return render_template('400.html', error_message=error), 400
