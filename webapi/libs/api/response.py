from flask import request as r, redirect, jsonify


def redirect_or_response(request: r, http_status: int = 200, redirect_url: str = None, response_text: str = ''):
    """
    Creates a flask return object. If redirect_url is passed, a redirect object will be passed, (only) if not, depending
    on the accepted mime types either an json or a plain html response will be created. If neither redirect_url nor
    response_text is set, the result will be empty.

    :param request: the request object of the current request
    :param http_status: status code to pass to the application, defaults to 200
    :param redirect_url: url to redirect to (does not need to be set)
    :param response_text: text to show in the response (ignored if redirect_url is set)
    :return: the flask return object
    """

    if redirect_url:
        if redirect_url.endswith('/'):
            redirect_url = redirect_url[:-1]
        return redirect(redirect_url)
    elif request.accept_mimetypes['application/json']:
        return jsonify(response_text), http_status
    else:
        return response_text, http_status


def response(request: r, http_status: int = 200, response_text: str = ''):
    """
    Creates a flask return object. Depending on the accepted mime types either an json or a plain html response will be
    created. If response_text is not set, the result will be empty.

    :param request: the request object of the current request
    :param http_status: status code to pass to the application, defaults to 200
    :param response_text: text to show in the response
    :return: the flask return object
    """
    return redirect_or_response(r, http_status, None, response_text)
