from webapi import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def exists_username(username):
        user = User.query.filter_by(username=username).first()
        return user is not None

    @staticmethod
    def exists_email(email):
        user = User.query.filter_by(email=email).first()
        return user is not None

    def __repr__(self):
        return '<User {} : {}>'.format(self.username, self.email)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
