from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, abort, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.profile import Profile, ProfilePhoto, ProfileDocument, ProfileNote, Shortlist
from app.models.lookup import BiodataTemplate
from app.forms.profile_forms import ProfileForm
from app.utils.decorators import member_or_admin_required
from app.utils.helpers import generate_registration_no, log_activity, calculate_completeness
from app.utils.astrology import calculate_mulank, calculate_bhagyank, estimate_rashi, estimate_nakshatra
from app.utils.image_utils import save_photo, save_document, allowed_image, allowed_document, delete_file
from app.utils.qr_utils import generate_profile_qr
from app.utils.biodata_pdf import generate_biodata_pdf
from app.utils.kundli_matching import calculate_gun_milan, find_best_matches

profile_bp = Blueprint("profile", __name__)

DOC_FIELD_MAP = {
    "aadhar_doc": "aadhar",
    "pan_doc": "pan",
    "education_doc": "education_certificate",
    "income_doc": "income_proof",
}


def _populate_profile_from_form(profile, form):
    skip = {"profile_photo", "full_length_photo", "family_photo", "gallery_photos",
            "aadhar_doc", "pan_doc", "education_doc", "income_doc", "submit", "csrf_token"}
    for field in form:
        if field.name in skip:
            continue
        setattr(profile, field.name, field.data)


def _handle_uploads(profile, form):
    watermark = current_app.config.get("WATERMARK_TEXT")

    def handle_single(file_field, photo_type, set_main=False):
        f = form[file_field].data
        if f and f.filename and allowed_image(f.filename):
            filename, thumb = save_photo(f, watermark_text=watermark)
            if set_main:
                profile.photos.filter_by(is_main=True).update({"is_main": False})
            db.session.add(ProfilePhoto(profile_id=profile.id, filename=filename, thumbnail=thumb,
                                         photo_type=photo_type, is_main=set_main))

    handle_single("profile_photo", "profile", set_main=True)
    handle_single("full_length_photo", "full_length")
    handle_single("family_photo", "family")

    for f in (form.gallery_photos.data or []):
        if f and getattr(f, "filename", None) and allowed_image(f.filename):
            filename, thumb = save_photo(f, watermark_text=watermark)
            db.session.add(ProfilePhoto(profile_id=profile.id, filename=filename, thumbnail=thumb, photo_type="gallery"))

    for field_name, doc_type in DOC_FIELD_MAP.items():
        f = form[field_name].data
        if f and getattr(f, "filename", None) and allowed_document(f.filename):
            filename = save_document(f)
            db.session.add(ProfileDocument(profile_id=profile.id, filename=filename, doc_type=doc_type))


@profile_bp.route("/register/profile", methods=["GET", "POST"])
@login_required
def create_profile():
    if current_user.profile is not None:
        return redirect(url_for("profile.my_profile"))

    form = ProfileForm()
    if form.validate_on_submit():
        profile = Profile(
            user_id=current_user.id,
            registration_no=generate_registration_no(),
            created_by_id=current_user.id,
        )
        _populate_profile_from_form(profile, form)
        profile.mulank = calculate_mulank(profile.dob)
        profile.bhagyank = calculate_bhagyank(profile.dob)
        profile.rashi = estimate_rashi(profile.dob)
        profile.nakshatra = estimate_nakshatra(profile.dob)
        profile.status = "pending"
        db.session.add(profile)
        db.session.commit()

        _handle_uploads(profile, form)
        profile.profile_completeness = calculate_completeness(profile)
        db.session.commit()

        log_activity(current_user.id, "Profile Created", f"Registration {profile.registration_no}")
        flash("Registration submitted! It is now pending admin approval.", "success")
        return redirect(url_for("profile.my_profile"))

    return render_template("profile/profile_form.html", form=form, profile=None)


@profile_bp.route("/my-profile")
@login_required
def my_profile():
    if current_user.is_admin or current_user.is_member:
        return redirect(url_for("member.dashboard" if current_user.is_member else "admin.dashboard"))
    if not current_user.profile:
        return redirect(url_for("profile.create_profile"))
    return render_template("profile/my_profile.html", profile=current_user.profile)


@profile_bp.route("/my-profile/edit", methods=["GET", "POST"])
@login_required
def edit_my_profile():
    profile = current_user.profile
    if not profile:
        return redirect(url_for("profile.create_profile"))
    if profile.status == "approved":
        flash("Your profile is approved and is now read-only. Contact admin for changes.", "warning")
        return redirect(url_for("profile.my_profile"))

    form = ProfileForm(obj=profile)
    if form.validate_on_submit():
        _populate_profile_from_form(profile, form)
        profile.mulank = calculate_mulank(profile.dob)
        profile.bhagyank = calculate_bhagyank(profile.dob)
        profile.rashi = estimate_rashi(profile.dob)
        profile.nakshatra = estimate_nakshatra(profile.dob)
        _handle_uploads(profile, form)
        profile.profile_completeness = calculate_completeness(profile)
        db.session.commit()
        log_activity(current_user.id, "Profile Updated", f"Registration {profile.registration_no}")
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.my_profile"))

    return render_template("profile/profile_form.html", form=form, profile=profile)


# ---------------- VIEW PERSONS (Members/Admins) ----------------

@profile_bp.route("/persons")
@member_or_admin_required
def view_persons():
    category = request.args.get("category", "all")  # all, male, female, single, married, divorced, widow, widower
    page = request.args.get("page", 1, type=int)

    query = Profile.query.filter_by(is_deleted=False, status="approved")

    if category == "male":
        query = query.filter_by(gender="Male")
    elif category == "female":
        query = query.filter_by(gender="Female")
    elif category in ("single", "married", "divorced"):
        query = query.filter_by(marital_status=category.capitalize())
    elif category == "widow":
        query = query.filter_by(marital_status="Widow")
    elif category == "widower":
        query = query.filter_by(marital_status="Widower")

    # Advanced filters
    f = request.args
    if f.get("age_min"):
        pass  # age filtered client-side via dob below
    if f.get("city"):
        query = query.filter(Profile.city.ilike(f"%{f['city']}%"))
    if f.get("country"):
        query = query.filter(Profile.country.ilike(f"%{f['country']}%"))
    if f.get("caste"):
        query = query.filter(Profile.caste.ilike(f"%{f['caste']}%"))
    if f.get("education"):
        query = query.filter(Profile.education.ilike(f"%{f['education']}%"))
    if f.get("occupation"):
        query = query.filter(Profile.occupation.ilike(f"%{f['occupation']}%"))
    if f.get("blood_group"):
        query = query.filter(Profile.blood_group == f["blood_group"])
    if f.get("diet"):
        query = query.filter(Profile.diet == f["diet"])
    if f.get("smoking"):
        query = query.filter(Profile.smoking == f["smoking"])
    if f.get("drinking"):
        query = query.filter(Profile.drinking == f["drinking"])
    if f.get("marital_status"):
        query = query.filter(Profile.marital_status == f["marital_status"])
    if f.get("mother_tongue"):
        query = query.filter(Profile.mother_tongue.ilike(f"%{f['mother_tongue']}%"))

    query = query.order_by(Profile.created_at.desc())
    pagination = query.paginate(page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False)

    shortlisted_ids = set()
    if current_user.is_member:
        shortlisted_ids = {s.profile_id for s in Shortlist.query.filter_by(member_id=current_user.id).all()}

    return render_template("profile/view_persons.html", pagination=pagination, category=category,
                            shortlisted_ids=shortlisted_ids, filters=f)


@profile_bp.route("/persons/search")
@member_or_admin_required
def global_search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        like = f"%{q}%"
        results = Profile.query.filter(
            Profile.is_deleted.is_(False),
            db.or_(
                Profile.full_name.ilike(like),
                Profile.registration_no.ilike(like),
                Profile.mobile.ilike(like),
                Profile.education.ilike(like),
                Profile.occupation.ilike(like),
                Profile.city.ilike(like),
            ),
        ).limit(50).all()
    return render_template("profile/search_results.html", results=results, q=q)


@profile_bp.route("/profile/<int:profile_id>")
@member_or_admin_required
def view_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    is_shortlisted = False
    if current_user.is_member:
        is_shortlisted = Shortlist.query.filter_by(member_id=current_user.id, profile_id=profile.id).first() is not None
    return render_template("profile/profile_detail.html", profile=profile, is_shortlisted=is_shortlisted)


@profile_bp.route("/profile/<int:profile_id>/shortlist", methods=["POST"])
@member_or_admin_required
def toggle_shortlist(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    existing = Shortlist.query.filter_by(member_id=current_user.id, profile_id=profile.id).first()
    if existing:
        db.session.delete(existing)
        flash("Removed from shortlist.", "info")
    else:
        db.session.add(Shortlist(member_id=current_user.id, profile_id=profile.id))
        flash("Added to shortlist.", "success")
    db.session.commit()
    return redirect(request.referrer or url_for("profile.view_profile", profile_id=profile.id))


@profile_bp.route("/profile/<int:profile_id>/note", methods=["POST"])
@member_or_admin_required
def add_note(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    note_text = request.form.get("note", "").strip()
    is_interested = request.form.get("is_interested") == "on"
    if note_text or is_interested:
        db.session.add(ProfileNote(profile_id=profile.id, member_id=current_user.id, note=note_text,
                                    is_interested=is_interested))
        db.session.commit()
        flash("Note added.", "success")
    return redirect(url_for("profile.view_profile", profile_id=profile.id))


@profile_bp.route("/profile/<int:profile_id>/biodata/<template_slug>")
@member_or_admin_required
def download_biodata(profile_id, template_slug):
    profile = Profile.query.get_or_404(profile_id)
    template = BiodataTemplate.query.filter_by(slug=template_slug, is_active=True).first()
    if not template:
        abort(404)
    path, filename = generate_biodata_pdf(profile, template_slug)
    log_activity(current_user.id, "Biodata Downloaded", f"{profile.registration_no} ({template_slug})")
    return send_file(path, as_attachment=True, download_name=filename)


@profile_bp.route("/profile/<int:profile_id>/qr")
@member_or_admin_required
def view_qr(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    if not profile.qr_code_path:
        profile.qr_code_path = generate_profile_qr(profile)
        db.session.commit()
    return render_template("profile/qr_view.html", profile=profile)


@profile_bp.route("/profile/<int:profile_id>/kundli")
@member_or_admin_required
def view_kundli(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    opposite_gender = "Female" if profile.gender == "Male" else "Male"
    candidates = Profile.query.filter_by(is_deleted=False, status="approved", gender=opposite_gender).all()
    matches = find_best_matches(profile, candidates, limit=int(request.args.get("limit", 10)))
    return render_template("profile/kundli_view.html", profile=profile, matches=matches)


@profile_bp.route("/compare")
@member_or_admin_required
def compare_profiles():
    id_a = request.args.get("a", type=int)
    id_b = request.args.get("b", type=int)
    profile_a = Profile.query.get(id_a) if id_a else None
    profile_b = Profile.query.get(id_b) if id_b else None
    match_result = None
    if profile_a and profile_b:
        match_result = calculate_gun_milan(profile_a, profile_b)
    return render_template("profile/compare.html", profile_a=profile_a, profile_b=profile_b, match=match_result)
