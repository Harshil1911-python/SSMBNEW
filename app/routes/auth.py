import random
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models.user import User, OTPVerification
from app.models.lookup import LoginLog
from app.forms.auth_forms import LoginForm, RegisterAccountForm, ForgotPasswordForm, ResetPasswordForm
from app.utils.helpers import log_activity

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _redirect_for_role(user):
    if user.is_admin:
        return redirect(url_for("admin.dashboard"))
    if user.is_member:
        return redirect(url_for("member.dashboard"))
    return redirect(url_for("profile.my_profile"))


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return _redirect_for_role(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        success = bool(user and user.check_password(form.password.data) and not user.is_deleted)

        db.session.add(LoginLog(
            user_id=user.id if user else None,
            email_attempted=form.email.data,
            success=success,
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:255],
        ))
        db.session.commit()

        if not success:
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_active_account:
            flash("Your account has been disabled. Please contact the admin.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember.data)
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        log_activity(user.id, "Login", f"{user.email} logged in")
        flash(f"Welcome back, {user.name}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else _redirect_for_role(user)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    """Public self-registration -> creates a bride_groom role account."""
    if current_user.is_authenticated:
        return _redirect_for_role(current_user)

    form = RegisterAccountForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "warning")
            return render_template("auth/register.html", form=form)
        if User.query.filter_by(mobile=form.mobile.data).first():
            flash("An account with this mobile number already exists.", "warning")
            return render_template("auth/register.html", form=form)

        user = User(name=form.name.data, email=email, mobile=form.mobile.data, role="bride_groom")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_activity(user.id, "Account Registered", f"New bride/groom account: {email}")

        login_user(user)
        flash("Account created! Please complete your marriage bureau registration form.", "success")
        return redirect(url_for("profile.create_profile"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_activity(current_user.id, "Logout", f"{current_user.email} logged out")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            code = f"{random.randint(100000, 999999)}"
            otp = OTPVerification(
                user_id=user.id, code=code, purpose="password_reset",
                expires_at=datetime.utcnow() + timedelta(minutes=15),
            )
            db.session.add(otp)
            db.session.commit()
            # In production this would be emailed via Flask-Mail.
            flash(f"An OTP has been generated. (Demo mode OTP: {code})", "info")
            return redirect(url_for("auth.reset_password", user_id=user.id))
        flash("If that email exists, an OTP has been sent.", "info")
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/reset-password/<int:user_id>", methods=["GET", "POST"])
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        otp = (
            OTPVerification.query.filter_by(user_id=user.id, code=form.code.data, purpose="password_reset",
                                              is_used=False)
            .order_by(OTPVerification.id.desc())
            .first()
        )
        if not otp or otp.expires_at < datetime.utcnow():
            flash("Invalid or expired OTP.", "danger")
            return render_template("auth/reset_password.html", form=form, user=user)

        otp.is_used = True
        user.set_password(form.password.data)
        db.session.commit()
        log_activity(user.id, "Password Reset", "Password reset via OTP")
        flash("Password reset successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, user=user)
