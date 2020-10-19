from flask import render_template
from flask_login import login_required

from . import bp


@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Linus'},
            'body': 'It is open!'
        }
    ]
    return render_template('dashboard.html', posts=posts, app_name='StreamHelper')


@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    return "Not yet implemented"


@bp.route('/ping')
def ping():
    return "", 200
