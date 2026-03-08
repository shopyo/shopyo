"""
.. module:: AdminModels
   :synopsis: Contains model of a user Record

"""

import datetime
import hashlib
import logging
import secrets

from flask import current_app
from flask_login import AnonymousUserMixin
from flask_login import UserMixin

from init import db
from init import login_manager

from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from shopyo.api.models import PkModel

role_user_bridge = db.Table(
    "role_user_bridge",
    db.Column(
        "user_id",
        db.Integer(),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "role_id",
        db.Integer(),
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class AnonymousUser(AnonymousUserMixin):
    """Anonymous user class"""

    def __init__(self):
        self.username = "guest"
        self.email = "<anonymous-user-no-email>"

    @property
    def is_email_confirmed(self):
        is_disabled = False

        if "EMAIL_CONFIRMATION_DISABLED" in current_app.config:
            is_disabled = current_app.config["EMAIL_CONFIRMATION_DISABLED"]

            if is_disabled is not True:
                is_disabled = False

        return is_disabled

    @property
    def is_admin(self):
        return False

    def __repr__(self):
        return f"<AnonymousUser {self.username}>"


login_manager.anonymous_user = AnonymousUser


class User(UserMixin, PkModel):
    """The user of the app"""

    __tablename__ = "users"

    username = db.Column(db.String(100), unique=True)
    _password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_registered = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.now
    )
    is_email_confirmed = db.Column(db.Boolean(), nullable=False, default=False)
    email_confirm_date = db.Column(db.DateTime)
    last_password_change = db.Column(db.DateTime, default=datetime.datetime.now)

    # A user can have many roles and a role can have many users
    roles = db.relationship(
        "Role",
        secondary=role_user_bridge,
        backref="users",
    )

    tokens = db.relationship(
        "UserToken", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User-id: {self.id}, User-email: {self.email}>"

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        # the default hashing method is pbkdf2:sha256
        self._password = generate_password_hash(plaintext)
        self.last_password_change = datetime.datetime.now()
        # Revoke all tokens on password change for security
        self.tokens.delete()

    def check_password(self, password):
        return check_password_hash(self._password, password)

    @classmethod
    def get_by_email(cls, email):
        """Case-insensitive user lookup by email."""
        return cls.query.filter(func.lower(cls.email) == func.lower(email)).first()

    def generate_confirmation_token(self):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(self.email, salt=current_app.config["PASSWORD_SALT"])

    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = False
        try:
            email = serializer.loads(
                token,
                salt=current_app.config["PASSWORD_SALT"],
                max_age=expiration,
            )
        except Exception as e:
            logging.getLogger(__name__).error(f"Error at confirm_token: {e}")
            return False

        if email != self.email:
            return False

        self.is_email_confirmed = True
        self.email_confirm_date = datetime.datetime.now()
        self.update()
        return True

    def generate_reset_password_token(self):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(self.email, salt=current_app.config["PASSWORD_SALT"])

    @staticmethod
    def verify_reset_password_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = serializer.loads(
                token,
                salt=current_app.config["PASSWORD_SALT"],
                max_age=expiration,
            )
        except Exception:
            return None
        return User.get_by_email(email)

    def generate_api_token(self, name):
        """Generates a new API token for the user."""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        UserToken.create(user_id=self.id, name=name, token_hash=token_hash)
        return token  # Return the raw token ONLY ONCE

    @staticmethod
    def verify_api_token(token):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user_token = UserToken.query.filter_by(token_hash=token_hash).first()
        if user_token:
            user_token.last_used_at = datetime.datetime.now()
            user_token.update()
            return user_token.user
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


login_manager.login_view = "shopyo_auth.login"


class UserToken(PkModel):
    """API Tokens for users"""

    __tablename__ = "user_tokens"
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    token_hash = db.Column(db.String(64), unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    last_used_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<UserToken {self.name} for User {self.user_id}>"


class Role(PkModel):
    """A role for a user."""

    __tablename__ = "roles"
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Role-id: {self.id}, Role-name: {self.name}>"
