"""
Library for parsing requests.
"""

from flask import request


def param(name: str, default: str = "") -> str:
    """
    Parses an request for GET and POST arguments.

    :param request: request to parse
    :param name: name of the argument
    :param default: default value if no param found. Defaults to an empty string.
    :return: get or post or default argument
    """
    return request.args.get(name) or request.form.get(name) or default


def is_set(parameter: str):
    """
    Checks if a given parameter exists and is not empty.

    :param parameter: param to check for
    :return: if param is not None and not empty
    """
    return parameter and parameter != ""
