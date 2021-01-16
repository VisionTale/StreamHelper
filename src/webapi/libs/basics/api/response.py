"""
Library for sending complex and flexible responses.
"""
from flask import request, redirect, jsonify, render_template, flash
from jinja2.exceptions import TemplateNotFound

from .parsing import param


def redirect_or_response(http_status: int = 200, response_text: str = '', redirect_url: str = '',
                         graphical: bool = False):
    """
    Creates a flask return object. If redirect_url is passed, a redirect object will be passed, (only) if not, depending
    on the accepted mime types either an json or a plain html response will be created. If neither redirect_url nor
    response_text is set, the result will be empty.

    :param http_status: status code to pass to the application, defaults to 200
    :param response_text: text to show in the response (ignored if redirect_url is set)
    :param redirect_url: url to redirect to (does not need to be set). If not set, request is checked for a passed
        redirect_url parameter. If set to None, any other redirect value will be ignored.
    :param graphical: whether the request answer shall be a website
    :return: the flask return object
    """
    if http_status - 300 >= 0 and graphical:
        try:
            return render_template(f'{http_status}.html', error_message=response_text)
        except TemplateNotFound:
            return render_template(f'generic.html', error_message=response_text, status_code=http_status)
    elif http_status - 300 >= 0:
        flash(f'Error {http_status}: {response_text}')

    redirect_url = redirect_url or param('redirect_url')
    if redirect_url and redirect_url != '':
        if redirect_url.endswith('/'):
            redirect_url = redirect_url[:-1]
        return redirect(redirect_url)
    elif request.accept_mimetypes['application/json']:
        return jsonify(response_text), http_status
    else:
        return response_text, http_status


def response(http_status: int = 200, response_text: str = '', graphical: bool = False):
    """
    Creates a flask return object. Depending on the accepted mime types either an json or a plain html response will be
    created. If response_text is not set, the result will be empty.

    Wraps around redirect_or_response, but ignores redirect_url.

    :param http_status: status code to pass to the application, defaults to 200
    :param response_text: text to show in the response
    :param graphical: whether the request answer shall be a website
    :return: the flask return object
    """
    return redirect_or_response(http_status, response_text, redirect_url=None, graphical=graphical)
