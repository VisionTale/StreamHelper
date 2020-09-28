from flask import render_template

from webapi import webapi


@webapi.errorhandler(404)
def not_found_error(error):
    return render_template('../../blueprints/errors/templates/404.html'), 404


@webapi.errorhandler(500)
def internal_system_error(error):
    return render_template('../../blueprints/errors/templates/500.html'), 500


@webapi.errorhandler(418)
def i_am_a_teapot(error):
    return render_template('../../blueprints/errors/templates/418.html'), 418
