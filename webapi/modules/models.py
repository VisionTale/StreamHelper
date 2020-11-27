"""
Models for database representation.
"""

from webapi import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """
    User model.

    TODO Implement permission system, user deletion, password change
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password: str):
        """
        Set a password using a salted hash.

        :param password: password to safe
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Check if the password corresponds to the salted password.

        :param password: password to check
        :return: whether the password is correct
        """
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def exists_username(username: str):
        """
        Checks if a username is already taken.

        :param username: username to check
        :return: user object or None
        """
        return User.get_user(username) is not None

    @staticmethod
    def exists_email(email: str):
        """
        Checks if a mail is already in use.

        :param email: mail to check
        :return: user object or None
        """
        user = User.query.filter_by(email=email).first()
        return user is not None

    @staticmethod
    def get_user(username: str):
        """
        Returns a user with a given name. Assumes the user exists.

        :param username: user to query
        :return: user object
        """

        user = User.query.filter_by(username=username).first()
        assert user

        return user

    def __repr__(self):
        """
        Textual representation of a user.

        :return: "<User **username** : **email**>"
        """
        return '<User {} : {}>'.format(self.username, self.email)


@login.user_loader
def load_user(user_id: int) -> User:
    """
    Load a user based on his user id.

    :param user_id: user id of the user
    :return: user object
    """
    return User.query.get(int(user_id))
