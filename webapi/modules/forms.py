from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

from re import compile

from webapi.modules.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if User.exists_username(username.data):
            raise ValidationError('Username already in use')
        pattern = compile("^[A-Za-z0-9]{4,20}$")
        if not pattern.fullmatch(username.data):
            raise ValidationError('Username should contain between 4 to 20 characters and can contain english alphabet '
                                  'letters and numbers')

    def validate_email(self, email):
        if User.exists_email(email.data):
            raise ValidationError('Email already in use')

    def validate_password(self, password):
        error_message = 'Password shall contain between 8 and 32 characters, containing at least one digit, one ' \
                        'lowercase character, one uppercase character and one special character ' \
                        '*.!@#$%^&(){}:;<>,.?/~_+=|'
        if not compile('[0-9]').search(password.data) or not compile('[a-z]').search(password.data) or \
                not compile('[A-Z]').search(password.data) or \
                not compile('[!@$%^&(){}:;<>,?/~_+=|]').search(password.data) or \
                not compile('^[0-9a-zA-Z*.!@$%^&(){}:;<>,?/~_+=|]{8,32}$').search(password.data):
            raise ValidationError(error_message)
