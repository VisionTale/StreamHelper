"""
Custom error pages.
"""
from flask import render_template, request

from . import bp

from webapi import db
from libs.basics.api.response import response


def wants_json_response() -> bool:
    """
    Check if json is accepted by comparing mimetype values of application/json vs. text/html

    :return: True if value of application/json is higher or equal to text/html, False otherwise
    """
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']


@bp.app_errorhandler(404)
def not_found_error(error):
    """
    Returns a json 404 if json requested, otherwise rendering custom 404 error page.

    :param error: error message (not handled)
    :return: json response or rendered template
    """
    if wants_json_response():
        return response(404, "Not found")
    return render_template('404.html'), 404


@bp.app_errorhandler(500)
def internal_system_error(error):
    """
    Returns a json 500 if json requested, otherwise rendering custom 500 error page.

    Also rolls back the database session.

    :param error: error message (not handled)
    :return: json response or rendered template
    """
    db.session.rollback()
    if wants_json_response():
        return response(500, "Internal server error")
    return render_template('500.html'), 500


@bp.app_errorhandler(418)
def i_am_a_teapot(error):
    """
    Returns a json 418 if json requested, otherwise rendering custom 418 "error" page.

    :param error: error message (not handled)
    :return: json response or rendered template
    """
    if wants_json_response():
        return response(418, "May the teapot be with you")
    return render_template('418.html'), 418


@bp.app_errorhandler(400)
def bad_request(error):
    """
    Returns a json 400 if json requested, otherwise rendering custom 400 error page.

    :param error: error message
    :return: json response or rendered template
    """
    if wants_json_response():
        return response(418, f"Bad request: {error}")
    return render_template('400.html', error_message=error), 400
