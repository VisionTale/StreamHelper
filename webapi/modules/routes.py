from flask import render_template, flash, redirect, url_for
from webapi import webapi, logger
from webapi.modules.forms import LoginForm


@webapi.route('/')
@webapi.route('/dashboard')
def dashboard():
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
    return render_template('dashboard.html', user=user, posts=posts, app_name='StreamHelper')


@webapi.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        logger.info('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('dashboard'))
    return render_template('login.html', title='Sign In', form=form)


@webapi.route('/settings', methods=['GET', 'POST'])
def settings():
    return "Not yet implemented"
