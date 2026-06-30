"""Email notification service using Flask-Mail.

All sending is wrapped in try/except so a mail failure never crashes
a user-facing request. In development (no MAIL_USERNAME set) the email
content is printed to stdout instead.
"""
import traceback
from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail


def _send(subject: str, recipients: list, body: str = None, html: str = None):
    if not current_app.config.get("MAIL_USERNAME"):
        current_app.logger.info(f"[MAIL STUB] To: {recipients} | Subject: {subject}")
        return
    try:
        msg = Message(subject, recipients=recipients,
                      sender=current_app.config["MAIL_DEFAULT_SENDER"])
        if body:
            msg.body = body
        if html:
            msg.html = html
        mail.send(msg)
    except Exception:
        current_app.logger.error(f"Failed to send email: {traceback.format_exc()}")


def send_registration_confirmation(user, profile):
    _send(
        subject="Registration Received — Citylight Sindhi Samaj Marriage Bureau",
        recipients=[user.email],
        body=(
            f"Dear {user.name},\n\n"
            f"Thank you for registering with Citylight Sindhi Samaj Marriage Bureau.\n"
            f"Your registration number is: {profile.registration_no}\n\n"
            "Your profile is currently under review and will be activated once approved by our committee.\n\n"
            "Regards,\nCitylight Sindhi Samaj Marriage Bureau Team, Surat"
        ),
    )


def send_approval_notification(user, profile):
    _send(
        subject="Profile Approved — Citylight Sindhi Samaj Marriage Bureau",
        recipients=[user.email],
        body=(
            f"Dear {user.name},\n\n"
            f"Great news! Your marriage bureau profile (Reg No: {profile.registration_no}) "
            "has been approved by our committee and is now active.\n\n"
            "Our members will now be able to view your profile. "
            "You may contact us for any matches or queries.\n\n"
            "Regards,\nCitylight Sindhi Samaj Marriage Bureau Team, Surat"
        ),
    )


def send_rejection_notification(user, profile, reason: str = ""):
    _send(
        subject="Profile Update Required — Citylight Sindhi Samaj Marriage Bureau",
        recipients=[user.email],
        body=(
            f"Dear {user.name},\n\n"
            f"Your profile (Reg No: {profile.registration_no}) requires attention before it can be published.\n\n"
            f"{('Reason: ' + reason + chr(10)) if reason else ''}"
            "Please log in, update your details, and re-submit for review.\n\n"
            "Regards,\nCitylight Sindhi Samaj Marriage Bureau Team, Surat"
        ),
    )


def send_otp_email(user, otp_code: str, purpose: str = "verification"):
    subject_map = {
        "email_verify": "Email Verification OTP",
        "password_reset": "Password Reset OTP",
    }
    _send(
        subject=f"{subject_map.get(purpose, 'OTP')} — Citylight Sindhi Samaj",
        recipients=[user.email],
        body=(
            f"Dear {user.name},\n\n"
            f"Your one-time password (OTP) is: {otp_code}\n"
            "This OTP is valid for 15 minutes and can only be used once.\n\n"
            "If you did not request this, please ignore this email.\n\n"
            "Regards,\nCitylight Sindhi Samaj Marriage Bureau"
        ),
    )


def send_member_welcome(user, temp_password: str = "Welcome@123"):
    _send(
        subject="Member Account Created — Citylight Sindhi Samaj",
        recipients=[user.email],
        body=(
            f"Dear {user.name},\n\n"
            "A member account has been created for you on the Citylight Sindhi Samaj Marriage Bureau portal.\n\n"
            f"Email:    {user.email}\n"
            f"Password: {temp_password}\n\n"
            "Please log in and change your password immediately.\n\n"
            "Regards,\nCitylight Sindhi Samaj Marriage Bureau Admin"
        ),
    )
