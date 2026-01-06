import datetime
import logging

from flask import current_app

from .models import User

logger = logging.getLogger(__name__)


def add_admin(email, password, verbose=False):
    user = User.query.filter_by(email=email).first()
    if user:
        if verbose:
            logger.info(f"[ ] Admin user with email {email} already exists")
        return

    user = User()
    user.email = email
    user.password = password
    user.is_admin = True
    user.is_email_confirmed = True
    user.email_confirm_date = datetime.datetime.now()
    user.save()
    logger.info(f"Uploading default admin with creds: {email} {password}")


def upload(verbose=False):
    add_admin(
        current_app.config["SEED_ADMIN_EMAIL"],
        current_app.config["SEED_ADMIN_PASSWORD"],
        verbose=verbose,
    )

    if verbose:
        logger.info("[x] Added Admin User")
