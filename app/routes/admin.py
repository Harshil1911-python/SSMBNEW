from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile, ProfileNote
from app.models.lookup import (
    Caste, Occupation, Education, Country, State, City, BloodGroup, Habit, Language,
    SiteSetting, ActivityLog, LoginLog, BiodataTemplate,
)
from app.utils.decorators import admin_required
from app.utils.helpers import log_activity
from app.utils.image_utils import save_photo
from app.services.export_service import export_profiles_excel, export_profiles_csv, csv_import_template_path
from app.services.import_service import import_profiles_csv
from app.services.backup_service import create_backup, list_backups, restore_backup_users_and_lookups
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

LOOKUP_MODELS = {
    "castes": Caste, "occupations": Occupation, "educations": Education, "countries": Country,
    "states": State, "cities": City, "blood_groups": BloodGroup, "habits": Habit, "languages": Language,
}


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    today = datetime.utcnow().date()
    stats = {
        "total": Profile.query.filter_by(is_deleted=False).count(),
        "male": Profile.query.filter_by(is_deleted=False, gender="Male").count(),
        "female": Profile.query.filter_by(is_deleted=False, gender="Female").count(),
        "married": Profile.query.filter_by(is_deleted=False, marital_status="Married").count(),
        "single": Profile.query.filter_by(is_deleted=False, marital_status="Single").count(),
        "divorced": Profile.query.filter_by(is_deleted=False, marital_status="Divorced").count(),
        "pending": Profile.query.filter_by(is_deleted=False, status="pending").count(),
        "approved": Profile.query.filter_by(is_deleted=False, status="approved").count(),
        "rejected": Profile.query.filter_by(is_deleted=False, status="rejected").count(),
        "today_registrations": Profile.query.filter(func.date(Profile.created_at) == today).count(),
        "total_members": User.query.filter_by(role="member", is_deleted=False).count(),
        "total_admins": User.query.filter_by(role="admin", is_deleted=False).count(),
    }
    recent_registrations = Profile.query.order_by(Profile.created_at.desc()).limit(10).all()
    recent_activity = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(15).all()

    # chart data: registrations per month (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly = (
        db.session.query(func.strftime("%Y-%m", Profile.created_at).label("month"), func.count(Profile.id))
        .filter(Profile.created_at >= six_months_ago)
        .group_by("month")
        .order_by("month")
        .all()
    )
    chart_labels = [m[0] for m in monthly]
    chart_values = [m[1] for m in monthly]

    return render_template("admin/dashboard.html", stats=stats, recent_registrations=recent_registrations,
                            recent_activity=recent_activity, chart_labels=chart_labels, chart_values=chart_values)


# ---------------- Registrations / Approvals ----------------

@admin_bp.route("/registrations")
@login_required
@admin_required
def registrations():
    status = request.args.get("status", "pending")
    page = request.args.get("page", 1, type=int)
    query = Profile.query.filter_by(is_deleted=False)
    if status != "all":
        query = query.filter_by(status=status)
    pagination = query.order_by(Profile.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/registrations.html", pagination=pagination, status=status)


@admin_bp.route("/registrations/<int:profile_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_registration(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    profile.status = "approved"
    profile.approved_at = datetime.utcnow()
    db.session.commit()
    log_activity(current_user.id, "Registration Approved", profile.registration_no)
    flash(f"{profile.full_name} approved.", "success")
    return redirect(request.referrer or url_for("admin.registrations"))


@admin_bp.route("/registrations/<int:profile_id>/reject", methods=["POST"])
@login_required
@admin_required
def reject_registration(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    profile.status = "rejected"
    db.session.commit()
    log_activity(current_user.id, "Registration Rejected", profile.registration_no)
    flash(f"{profile.full_name} rejected.", "info")
    return redirect(request.referrer or url_for("admin.registrations"))


@admin_bp.route("/registrations/<int:profile_id>/assign-member", methods=["POST"])
@login_required
@admin_required
def assign_member(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    member_id = request.form.get("member_id", type=int)
    profile.assigned_member_id = member_id
    db.session.commit()
    flash("Member assigned.", "success")
    return redirect(request.referrer or url_for("admin.registrations"))


@admin_bp.route("/registrations/<int:profile_id>/delete", methods=["POST"])
@login_required
@admin_required
def soft_delete_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    profile.is_deleted = True
    profile.deleted_at = datetime.utcnow()
    db.session.commit()
    log_activity(current_user.id, "Profile Deleted (Soft)", profile.registration_no)
    flash("Profile moved to trash bin.", "info")
    return redirect(request.referrer or url_for("admin.registrations"))


@admin_bp.route("/trash")
@login_required
@admin_required
def trash_bin():
    deleted = Profile.query.filter_by(is_deleted=True).order_by(Profile.deleted_at.desc()).all()
    return render_template("admin/trash.html", deleted=deleted)


@admin_bp.route("/trash/<int:profile_id>/restore", methods=["POST"])
@login_required
@admin_required
def restore_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    profile.is_deleted = False
    profile.deleted_at = None
    db.session.commit()
    log_activity(current_user.id, "Profile Restored", profile.registration_no)
    flash("Profile restored.", "success")
    return redirect(url_for("admin.trash_bin"))


# ---------------- Add Bride/Groom directly ----------------

@admin_bp.route("/add-person", methods=["GET", "POST"])
@login_required
@admin_required
def add_person():
    from app.forms.profile_forms import ProfileForm
    from app.routes.profile import _populate_profile_from_form, _handle_uploads
    from app.utils.helpers import generate_registration_no, calculate_completeness
    from app.utils.astrology import calculate_mulank, calculate_bhagyank, estimate_rashi, estimate_nakshatra

    form = ProfileForm()
    if form.validate_on_submit():
        email = form.email.data or f"{form.mobile.data}@placeholder.citylightsindhisamaj.org"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=form.full_name.data, email=email, role="bride_groom")
            user.set_password("Welcome@123")
            db.session.add(user)
            db.session.flush()

        profile = Profile(user_id=user.id, registration_no=generate_registration_no(), created_by_id=current_user.id)
        _populate_profile_from_form(profile, form)
        profile.mulank = calculate_mulank(profile.dob)
        profile.bhagyank = calculate_bhagyank(profile.dob)
        profile.rashi = estimate_rashi(profile.dob)
        profile.nakshatra = estimate_nakshatra(profile.dob)
        profile.status = "approved"
        profile.approved_at = datetime.utcnow()
        db.session.add(profile)
        db.session.commit()
        _handle_uploads(profile, form)
        profile.profile_completeness = calculate_completeness(profile)
        db.session.commit()
        log_activity(current_user.id, "Person Added by Admin", profile.registration_no)
        flash(f"{profile.full_name} added and approved.", "success")
        return redirect(url_for("admin.registrations", status="all"))

    return render_template("profile/profile_form.html", form=form, profile=None, admin_add=True)


# ---------------- Manage Members / Admins ----------------

@admin_bp.route("/users")
@login_required
@admin_required
def manage_users():
    role = request.args.get("role", "member")
    users = User.query.filter_by(role=role, is_deleted=False).order_by(User.created_at.desc()).all()
    return render_template("admin/manage_users.html", users=users, role=role)


@admin_bp.route("/users/<int:user_id>/make-admin", methods=["POST"])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.role = "admin"
    db.session.commit()
    log_activity(current_user.id, "Made Admin", user.email)
    flash(f"{user.name} is now an admin.", "success")
    return redirect(request.referrer or url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/make-member", methods=["POST"])
@login_required
@admin_required
def make_member(user_id):
    user = User.query.get_or_404(user_id)
    user.role = "member"
    db.session.commit()
    log_activity(current_user.id, "Made Member", user.email)
    flash(f"{user.name} is now a member.", "success")
    return redirect(request.referrer or url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_account = not user.is_active_account
    db.session.commit()
    log_activity(current_user.id, "Toggled Active Status", f"{user.email} -> {user.is_active_account}")
    flash(f"{user.name} is now {'active' if user.is_active_account else 'disabled'}.", "info")
    return redirect(request.referrer or url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    db.session.commit()
    log_activity(current_user.id, "User Deleted", user.email)
    flash(f"{user.name} deleted.", "info")
    return redirect(request.referrer or url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    user.set_password("Welcome@123")
    db.session.commit()
    log_activity(current_user.id, "Password Reset by Admin", user.email)
    flash(f"Password for {user.name} reset to default (Welcome@123).", "success")
    return redirect(request.referrer or url_for("admin.manage_users"))


# ---------------- Import / Export ----------------

@admin_bp.route("/import-export")
@login_required
@admin_required
def import_export():
    return render_template("admin/import_export.html")


@admin_bp.route("/import-csv", methods=["POST"])
@login_required
@admin_required
def import_csv():
    file = request.files.get("csv_file")
    if not file or not file.filename:
        flash("Please select a file.", "warning")
        return redirect(url_for("admin.import_export"))
    success_count, errors = import_profiles_csv(file, current_user.id)
    log_activity(current_user.id, "CSV Import", f"{success_count} imported, {len(errors)} errors")
    flash(f"Imported {success_count} profiles. {len(errors)} rows skipped/errored.", "success" if success_count else "warning")
    return render_template("admin/import_export.html", errors=errors, success_count=success_count)


@admin_bp.route("/download-csv-template")
@login_required
@admin_required
def download_csv_template():
    path = csv_import_template_path()
    return send_file(path, as_attachment=True, download_name="csv_import_template.csv")


@admin_bp.route("/export/excel")
@login_required
@admin_required
def export_excel():
    profiles = Profile.query.filter_by(is_deleted=False).all()
    path = export_profiles_excel(profiles, "all_profiles")
    log_activity(current_user.id, "Excel Export", f"{len(profiles)} profiles")
    return send_file(path, as_attachment=True)


@admin_bp.route("/export/csv")
@login_required
@admin_required
def export_csv():
    profiles = Profile.query.filter_by(is_deleted=False).all()
    path = export_profiles_csv(profiles, "all_profiles")
    log_activity(current_user.id, "CSV Export", f"{len(profiles)} profiles")
    return send_file(path, as_attachment=True)


# ---------------- Backup / Restore ----------------

@admin_bp.route("/backup")
@login_required
@admin_required
def backup_page():
    backups = list_backups()
    return render_template("admin/backup.html", backups=backups)


@admin_bp.route("/backup/create", methods=["POST"])
@login_required
@admin_required
def backup_create():
    path, filename = create_backup()
    log_activity(current_user.id, "Backup Created", filename)
    flash(f"Backup created: {filename}", "success")
    return redirect(url_for("admin.backup_page"))


@admin_bp.route("/backup/download/<filename>")
@login_required
@admin_required
def backup_download(filename):
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], "backups", filename)
    return send_file(path, as_attachment=True)


@admin_bp.route("/backup/restore/<filename>", methods=["POST"])
@login_required
@admin_required
def backup_restore(filename):
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], "backups", filename)
    restored = restore_backup_users_and_lookups(path)
    log_activity(current_user.id, "Backup Restored", f"{filename} ({restored} records)")
    flash(f"Restored {restored} master-data records from {filename}.", "success")
    return redirect(url_for("admin.backup_page"))


# ---------------- Lookups (Caste, Occupation, Education, Geography, etc.) ----------------

@admin_bp.route("/lookups/<table>", methods=["GET", "POST"])
@login_required
@admin_required
def manage_lookup(table):
    model = LOOKUP_MODELS.get(table)
    if not model:
        flash("Unknown lookup table.", "danger")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name and not model.query.filter_by(name=name).first():
            db.session.add(model(name=name))
            db.session.commit()
            flash(f"Added '{name}'.", "success")
        return redirect(url_for("admin.manage_lookup", table=table))

    items = model.query.order_by(model.name).all()
    return render_template("admin/manage_lookup.html", items=items, table=table)


@admin_bp.route("/lookups/<table>/<int:item_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_lookup(table, item_id):
    model = LOOKUP_MODELS.get(table)
    item = model.query.get_or_404(item_id)
    item.is_active = not item.is_active
    db.session.commit()
    return redirect(url_for("admin.manage_lookup", table=table))


@admin_bp.route("/lookups/<table>/<int:item_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_lookup(table, item_id):
    model = LOOKUP_MODELS.get(table)
    item = model.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("admin.manage_lookup", table=table))


# ---------------- Site Settings / Theme ----------------

@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def site_settings():
    if request.method == "POST":
        for key in ("site_name", "site_city", "primary_color", "secondary_color",
                    "footer_text", "contact_email", "contact_phone", "address",
                    "facebook_url", "instagram_url", "whatsapp_number"):
            value = request.form.get(key)
            if value is not None:
                setting = SiteSetting.query.filter_by(key=key).first()
                if not setting:
                    setting = SiteSetting(key=key)
                    db.session.add(setting)
                setting.value = value

        logo_file = request.files.get("logo")
        if logo_file and logo_file.filename:
            filename, _ = save_photo(logo_file, subfolder="branding", max_size=(500, 500))
            setting = SiteSetting.query.filter_by(key="logo_path").first()
            if not setting:
                setting = SiteSetting(key="logo_path")
                db.session.add(setting)
            setting.value = f"branding/{filename}"

        bg_file = request.files.get("background")
        if bg_file and bg_file.filename:
            filename, _ = save_photo(bg_file, subfolder="branding", max_size=(1920, 1080))
            setting = SiteSetting.query.filter_by(key="background_path").first()
            if not setting:
                setting = SiteSetting(key="background_path")
                db.session.add(setting)
            setting.value = f"branding/{filename}"

        db.session.commit()
        log_activity(current_user.id, "Site Settings Updated", "")
        flash("Settings updated successfully.", "success")
        return redirect(url_for("admin.site_settings"))

    settings = {s.key: s.value for s in SiteSetting.query.all()}
    return render_template("admin/site_settings.html", settings=settings)


@admin_bp.route("/biodata-templates")
@login_required
@admin_required
def biodata_templates():
    templates = BiodataTemplate.query.order_by(BiodataTemplate.sort_order).all()
    return render_template("admin/biodata_templates.html", templates=templates)


@admin_bp.route("/biodata-templates/<int:template_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_biodata_template(template_id):
    t = BiodataTemplate.query.get_or_404(template_id)
    t.is_active = not t.is_active
    db.session.commit()
    return redirect(url_for("admin.biodata_templates"))


# ---------------- Logs / Reports ----------------

@admin_bp.route("/logs/activity")
@login_required
@admin_required
def activity_logs():
    page = request.args.get("page", 1, type=int)
    pagination = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template("admin/activity_logs.html", pagination=pagination)


@admin_bp.route("/logs/login")
@login_required
@admin_required
def login_logs():
    page = request.args.get("page", 1, type=int)
    pagination = LoginLog.query.order_by(LoginLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template("admin/login_logs.html", pagination=pagination)


@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    by_education = dict(db.session.query(Profile.education, func.count(Profile.id)).filter(
        Profile.is_deleted.is_(False), Profile.education.isnot(None)).group_by(Profile.education).all())
    by_occupation = dict(db.session.query(Profile.occupation, func.count(Profile.id)).filter(
        Profile.is_deleted.is_(False), Profile.occupation.isnot(None)).group_by(Profile.occupation).all())
    by_city = dict(db.session.query(Profile.city, func.count(Profile.id)).filter(
        Profile.is_deleted.is_(False), Profile.city.isnot(None)).group_by(Profile.city).all())
    by_marital_status = dict(db.session.query(Profile.marital_status, func.count(Profile.id)).filter(
        Profile.is_deleted.is_(False)).group_by(Profile.marital_status).all())
    by_religion = dict(db.session.query(Profile.religion, func.count(Profile.id)).filter(
        Profile.is_deleted.is_(False)).group_by(Profile.religion).all())
    by_blood_group = dict(db.session.query(Profile.blood_group, func.count(Profile.id)).filter(
        Profile.is_deleted.is_(False), Profile.blood_group.isnot(None)).group_by(Profile.blood_group).all())

    return render_template("admin/reports.html", by_education=by_education, by_occupation=by_occupation,
                            by_city=by_city, by_marital_status=by_marital_status, by_religion=by_religion,
                            by_blood_group=by_blood_group)


@admin_bp.route("/users/add-member", methods=["GET", "POST"])
@login_required
@admin_required
def add_member():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        mobile = request.form.get("mobile", "").strip()
        if not name or not email:
            flash("Name and email are required.", "warning")
            return redirect(url_for("admin.add_member"))
        if User.query.filter_by(email=email).first():
            flash("A user with this email already exists.", "warning")
            return redirect(url_for("admin.add_member"))
        user = User(name=name, email=email, mobile=mobile or None, role="member",
                    is_active_account=True, is_email_verified=True)
        user.set_password("Welcome@123")
        db.session.add(user)
        db.session.commit()
        from app.services.email_service import send_member_welcome
        send_member_welcome(user)
        log_activity(current_user.id, "Member Added", f"{email} added as member")
        flash(f"Member account created for {name}. Temporary password: Welcome@123", "success")
        return redirect(url_for("admin.manage_users", role="member"))
    return render_template("admin/add_member.html")
