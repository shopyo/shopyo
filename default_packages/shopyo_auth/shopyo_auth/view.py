import datetime

from flask import current_app
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from . import limiter
from .forms import ForgotPasswordForm
from .forms import LoginForm
from .forms import RegistrationForm
from .forms import ResetPasswordForm
from .models import User
from .models import UserToken
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
@limiter.limit(lambda: current_app.config["SHOPYO_AUTH_RATE_LIMIT"])
def register():
    context = {}
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        email = reg_form.email.data
        password = reg_form.password.data
        user = User.create(email=email, password=password)

        auth_ext = current_app.extensions.get("shopyo_auth")
        if auth_ext:
            auth_ext.trigger("user_registered", user)

        login_user(user)

        is_disabled = current_app.config.get(
            "SHOPYO_AUTH_EMAIL_CONFIRMATION_DISABLED", False
        )

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

        next_url = request.args.get("next")
        if not next_url or next_url == "/" or not is_safe_redirect_url(next_url):
            if auth_ext and auth_ext.login_redirect_url:
                if callable(auth_ext.login_redirect_url):
                    next_url = auth_ext.login_redirect_url(user)
                else:
                    next_url = auth_ext.login_redirect_url

            if not next_url:
                next_url = url_for("shopyo_dashboard.index")
        return redirect(next_url)

    context["form"] = reg_form
    register_template = current_app.config.get("SHOPYO_AUTH_REGISTER_TEMPLATE", "shopyo_auth/register.html")
    return render_template(register_template, **context)


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
@limiter.limit(lambda: current_app.config["SHOPYO_AUTH_RATE_LIMIT"])
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
            auth_ext = current_app.extensions.get("shopyo_auth")
            if auth_ext:
                auth_ext.trigger("password_reset_requested", user)
        flash(
            notify_success(
                "Check your email for the instructions to reset your password"
            )
        )
        return redirect(url_for("shopyo_auth.login"))
    elif form.errors:
        from shopyo.api.forms import flash_errors

        flash_errors(form)
    return render_template("shopyo_auth/forgot_password.html", form=form)


@module_blueprint.route("/reset-password/<token>", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["SHOPYO_AUTH_RATE_LIMIT"])
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

        auth_ext = current_app.extensions.get("shopyo_auth")
        if auth_ext:
            auth_ext.trigger("password_reset_completed", user)

        flash(notify_success("Your password has been reset."))
        return redirect(url_for("shopyo_auth.login"))
    elif form.errors:
        from shopyo.api.forms import flash_errors

        flash_errors(form)
    return render_template("shopyo_auth/reset_password.html", form=form, token=token)


@module_blueprint.route("/login", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["SHOPYO_AUTH_RATE_LIMIT"])
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
        remember = (
            login_form.remember.data if hasattr(login_form, "remember") else False
        )
        login_user(user, remember=remember)

        auth_ext = current_app.extensions.get("shopyo_auth")
        if auth_ext:
            auth_ext.trigger("user_login", user)

        next_url = request.form.get("next")
        if not next_url or next_url == "/" or not is_safe_redirect_url(next_url):
            if auth_ext and auth_ext.login_redirect_url:
                if callable(auth_ext.login_redirect_url):
                    next_url = auth_ext.login_redirect_url(user)
                else:
                    next_url = auth_ext.login_redirect_url

            if not next_url:
                next_url = url_for("shopyo_dashboard.index")
        return redirect(next_url)
    login_template = current_app.config.get(
        "SHOPYO_AUTH_LOGIN_TEMPLATE", "shopyo_auth/login.html"
    )
    return render_template(login_template, **context)


@module_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user._get_current_object()
    logout_user()

    auth_ext = current_app.extensions.get("shopyo_auth")
    if auth_ext:
        auth_ext.trigger("user_logout", user)

    flash(notify_success("Successfully logged out"))

    next_url = request.args.get("next")
    if not next_url or not is_safe_redirect_url(next_url):
        if auth_ext and auth_ext.logout_redirect_url:
            if callable(auth_ext.logout_redirect_url):
                next_url = auth_ext.logout_redirect_url(user)
            else:
                next_url = auth_ext.logout_redirect_url

        if not next_url:
            next_url = url_for("shopyo_auth.login")
    return redirect(next_url)


@module_blueprint.route("/api/tokens", methods=["GET"])
@login_required
def list_tokens():
    tokens = current_user.tokens.all()
    return jsonify(
        [
            {
                "id": t.id,
                "name": t.name,
                "created_at": t.created_at.isoformat(),
                "last_used_at": t.last_used_at.isoformat() if t.last_used_at else None,
            }
            for t in tokens
        ]
    )


@module_blueprint.route("/api/tokens", methods=["POST"])
@login_required
def create_token():
    name = request.json.get("name")
    if not name:
        return jsonify({"message": "Token name is required"}), 400
    token = current_user.generate_api_token(name)
    return (
        jsonify(
            {
                "token": token,
                "message": "Store this token safely, it won't be shown again!",
            }
        ),
        201,
    )


@module_blueprint.route("/api/tokens/<int:token_id>", methods=["DELETE"])
@login_required
def delete_token(token_id):
    token = UserToken.query.filter_by(id=token_id, user_id=current_user.id).first()
    if not token:
        return jsonify({"message": "Token not found"}), 404
    token.delete()
    return jsonify({"message": "Token deleted"}), 200
