from flask import Blueprint, render_template, abort
from app.models.profile import Profile
from app.extensions import db

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    stats = {
        "total": Profile.query.filter_by(is_deleted=False, status="approved").count(),
        "male": Profile.query.filter_by(is_deleted=False, status="approved", gender="Male").count(),
        "female": Profile.query.filter_by(is_deleted=False, status="approved", gender="Female").count(),
    }
    return render_template("public/home.html", stats=stats)


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact")
def contact():
    return render_template("public/contact.html")


@public_bp.route("/qr/<registration_no>")
def view_qr_profile(registration_no):
    """Public QR-accessible read-only profile view. No login required.
    Confidential fields (contact, documents, address) are hidden."""
    profile = Profile.query.filter_by(registration_no=registration_no, is_deleted=False, status="approved").first()
    if not profile:
        abort(404)
    return render_template("public/qr_profile.html", profile=profile)
