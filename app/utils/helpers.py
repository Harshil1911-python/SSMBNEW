from datetime import datetime
from flask import request
from app.extensions import db
from app.models.lookup import ActivityLog


def generate_registration_no():
    from app.models.profile import Profile
    year = datetime.utcnow().strftime("%y")
    prefix = f"CSS{year}"
    last = (
        Profile.query.filter(Profile.registration_no.like(f"{prefix}%"))
        .order_by(Profile.id.desc())
        .first()
    )
    if last:
        try:
            last_num = int(last.registration_no.replace(prefix, ""))
        except ValueError:
            last_num = 0
    else:
        last_num = 0
    next_num = last_num + 1
    return f"{prefix}{next_num:04d}"


def log_activity(user_id, action, details=None):
    try:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr if request else None,
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


def calculate_completeness(profile):
    fields = [
        profile.full_name, profile.gender, profile.dob, profile.mobile, profile.email,
        profile.education, profile.occupation, profile.city, profile.height_cm,
        profile.about_yourself, profile.father_name, profile.mother_name,
        profile.caste, profile.diet, profile.family_type, profile.pref_age_min,
        profile.about_desired_partner, profile.current_address,
    ]
    filled = sum(1 for f in fields if f not in (None, "", 0))
    has_photo = profile.photos.count() > 0 if profile.id else False
    total = len(fields) + 1
    filled += 1 if has_photo else 0
    return round((filled / total) * 100)
