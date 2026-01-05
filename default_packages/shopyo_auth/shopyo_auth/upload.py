import datetime
import json
import logging

from .models import User

logger = logging.getLogger(__name__)


def add_admin(email, password):
    user = User()
    user.email = email
    user.password = password
    user.is_admin = True
    user.is_email_confirmed = True
    user.email_confirm_date = datetime.datetime.now()
    user.save()
    logger.info(f"Uploading default admin with creds: {email} {password}")


def upload(verbose=False):
    with open("config.json") as config:
        config = json.load(config)
        add_admin(config["admin_user"]["email"], config["admin_user"]["password"])

        if verbose:
            logger.info("[x] Added Admin User")
