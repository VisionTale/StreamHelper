from flask import render_template
from webapi import webapi


@webapi.route('/')
@webapi.route('/index')
def index():
    user = {'username': 'Simon'}
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
    return render_template('index.html', user=user, posts=posts, app_name='StreamHelper')
