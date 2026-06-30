from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user
from app.models.profile import Profile, Shortlist
from app.utils.decorators import roles_required
from app.services.export_service import export_profiles_excel

member_bp = Blueprint("member", __name__, url_prefix="/member")


@member_bp.route("/dashboard")
@login_required
@roles_required("member")
def dashboard():
    stats = {
        "total_approved": Profile.query.filter_by(is_deleted=False, status="approved").count(),
        "male": Profile.query.filter_by(is_deleted=False, status="approved", gender="Male").count(),
        "female": Profile.query.filter_by(is_deleted=False, status="approved", gender="Female").count(),
        "shortlisted": Shortlist.query.filter_by(member_id=current_user.id).count(),
    }
    recent = Profile.query.filter_by(is_deleted=False, status="approved").order_by(Profile.created_at.desc()).limit(8).all()
    return render_template("member/dashboard.html", stats=stats, recent=recent)


@member_bp.route("/shortlist")
@login_required
@roles_required("member")
def my_shortlist():
    shortlist = Shortlist.query.filter_by(member_id=current_user.id).order_by(Shortlist.created_at.desc()).all()
    profiles = [s.profile_id for s in shortlist]
    profile_objs = Profile.query.filter(Profile.id.in_(profiles)).all() if profiles else []
    return render_template("member/shortlist.html", profiles=profile_objs)


@member_bp.route("/export-selected", methods=["POST"])
@login_required
@roles_required("member", "admin")
def export_selected():
    ids = request.form.getlist("profile_ids")
    profiles = Profile.query.filter(Profile.id.in_(ids)).all() if ids else []
    path = export_profiles_excel(profiles, filename_prefix="selected_profiles")
    return send_file(path, as_attachment=True)
