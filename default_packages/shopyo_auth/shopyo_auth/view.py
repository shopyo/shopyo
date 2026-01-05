import datetime

from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from .forms import ForgotPasswordForm
from .forms import LoginForm
from .forms import RegistrationForm
from .forms import ResetPasswordForm
from .models import User
from shopyo.api.email import send_async_email
from shopyo.api.html import notify_danger
from shopyo.api.html import notify_success
from shopyo.api.html import notify_warning
from shopyo.api.module import ModuleHelp
from shopyo.api.security import is_safe_redirect_url


mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]


@module_blueprint.route("/register", methods=["GET", "POST"])
def register():
    context = {}
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        email = reg_form.email.data
        password = reg_form.password.data
        user = User.create(email=email, password=password)
        login_user(user)

        is_disabled = False

        if "EMAIL_CONFIRMATION_DISABLED" in current_app.config:
            is_disabled = current_app.config["EMAIL_CONFIRMATION_DISABLED"]

        if is_disabled is True:
            user.is_email_confirmed = True
            user.email_confirm_date = datetime.datetime.now()
            user.update()
        else:
            token = user.generate_confirmation_token()
            template = "shopyo_auth/emails/activate_user"
            subject = "Please confirm your email"
            context.update({"token": token, "user": user})
            send_async_email(email, subject, template, **context)
            flash(notify_success("A confirmation email has been sent via email."))

        return redirect(url_for("shopyo_dashboard.index"))

    context["form"] = reg_form
    return render_template("shopyo_auth/register.html", **context)


@module_blueprint.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.is_email_confirmed:
        flash(notify_warning("Account already confirmed."))
        return redirect(url_for("shopyo_dashboard.index"))

    if current_user.confirm_token(token):
        flash(notify_success("You have confirmed your account. Thanks!"))
        return redirect(url_for("shopyo_dashboard.index"))

    flash(notify_warning("The confirmation link is invalid/expired."))
    return redirect(url_for("shopyo_auth.unconfirmed"))


@module_blueprint.route("/resend")
@login_required
def resend():
    if current_user.is_email_confirmed:
        return redirect(url_for("shopyo_dashboard.index"))

    token = current_user.generate_confirmation_token()
    template = "shopyo_auth/emails/activate_user"
    subject = "Please confirm your email"
    context = {"token": token, "user": current_user}
    send_async_email(current_user.email, subject, template, **context)
    flash(notify_success("A new confirmation email has been sent."))
    return redirect(url_for("shopyo_auth.unconfirmed"))


@module_blueprint.route("/unconfirmed")
@login_required
def unconfirmed():
    if current_user.is_email_confirmed:
        return redirect(url_for("shopyo_dashboard.index"))
    flash(notify_warning("Please confirm your account!"))
    return render_template("shopyo_auth/unconfirmed.html")


@module_blueprint.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("shopyo_dashboard.index"))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user:
            token = user.generate_reset_password_token()
            template = "shopyo_auth/emails/reset_password"
            subject = "Password Reset Requested"
            context = {"token": token, "user": user}
            send_async_email(user.email, subject, template, **context)
        flash(
            notify_success(
                "Check your email for the instructions to reset your password"
            )
        )
        return redirect(url_for("shopyo_auth.login"))
    return render_template("shopyo_auth/forgot_password.html", form=form)


@module_blueprint.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("shopyo_dashboard.index"))
    user = User.verify_reset_password_token(token)
    if not user:
        flash(notify_danger("Invalid or expired token"))
        return redirect(url_for("shopyo_dashboard.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        user.update()
        flash(notify_success("Your password has been reset."))
        return redirect(url_for("shopyo_auth.login"))
    return render_template("shopyo_auth/reset_password.html", form=form)


@module_blueprint.route("/login", methods=["GET", "POST"])
def login():
    context = {}
    login_form = LoginForm()
    context["form"] = login_form
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = User.get_by_email(email)
        if user is None or not user.check_password(password):
            flash(notify_danger("please check your user id and password"))
            return redirect(url_for("shopyo_auth.login"))
        login_user(user)
        next_url = request.form.get("next")
        if not next_url or not is_safe_redirect_url(next_url):
            next_url = url_for("shopyo_dashboard.index")
        return redirect(next_url)
    return render_template("shopyo_auth/login.html", **context)


@module_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash(notify_success("Successfully logged out"))

    next_url = request.args.get("next")
    if not next_url or not is_safe_redirect_url(next_url):
        next_url = url_for("shopyo_dashboard.index")
    return redirect(next_url)
