from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse

from datetime import datetime

from webapi import logger, db
from webapi.modules.models import User

from . import bp
from .forms import LoginForm, SignUpForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('base.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('user.login'))
        login_user(user, remember=form.remember_me.data)
        logger.info('User {} logged in at {}'.format(form.username.data, datetime.utcnow()))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('base.dashboard')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('base.dashboard'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        logger.info('User {} with mail {} signed up at {}'.format(form.username.data, form.email.data,
                                                                  datetime.utcnow()))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('base.dashboard')
        return redirect(next_page)

    return render_template('signup.html', title='Sign Up', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base.dashboard'))
