import pandas as pd
from datetime import datetime
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile
from app.utils.helpers import generate_registration_no
from app.utils.astrology import calculate_mulank, calculate_bhagyank, estimate_rashi, estimate_nakshatra

REQUIRED_COLUMNS = ["full_name", "gender", "bride_or_groom", "mobile", "dob"]


def import_profiles_csv(file_storage, created_by_id):
    """Parses uploaded CSV/Excel, validates rows, skips duplicates (by mobile),
    and creates Profile + a generated User account for each valid row.
    Returns (success_count, errors list of {row, reason})."""
    filename = file_storage.filename.lower()
    if filename.endswith(".csv"):
        df = pd.read_csv(file_storage)
    else:
        df = pd.read_excel(file_storage)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        return 0, [{"row": 0, "reason": f"Missing required columns: {', '.join(missing_cols)}"}]

    success_count = 0
    errors = []

    for idx, row in df.iterrows():
        row_num = idx + 2  # account for header row, 1-indexed
        try:
            full_name = str(row.get("full_name", "")).strip()
            mobile = str(row.get("mobile", "")).strip()
            gender = str(row.get("gender", "")).strip().capitalize()
            bride_or_groom = str(row.get("bride_or_groom", "")).strip().capitalize()

            if not full_name or full_name == "nan":
                errors.append({"row": row_num, "reason": "Missing full_name"})
                continue
            if not mobile or mobile == "nan":
                errors.append({"row": row_num, "reason": "Missing mobile"})
                continue
            if gender not in ("Male", "Female"):
                errors.append({"row": row_num, "reason": "Invalid gender"})
                continue

            if Profile.query.filter_by(mobile=mobile).first():
                errors.append({"row": row_num, "reason": f"Duplicate mobile {mobile} - skipped"})
                continue

            dob_raw = row.get("dob")
            dob = pd.to_datetime(dob_raw, errors="coerce")
            dob = dob.date() if pd.notnull(dob) else None

            email = str(row.get("email", "")).strip()
            if not email or email == "nan":
                email = f"{mobile}@placeholder.citylightsindhisamaj.org"

            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(name=full_name, email=email, mobile=mobile if not User.query.filter_by(mobile=mobile).first() else None,
                            role="bride_groom")
                user.set_password("Welcome@123")
                db.session.add(user)
                db.session.flush()

            profile = Profile(
                user_id=user.id,
                registration_no=generate_registration_no(),
                full_name=full_name,
                gender=gender,
                bride_or_groom=bride_or_groom if bride_or_groom in ("Bride", "Groom") else ("Bride" if gender == "Female" else "Groom"),
                mobile=mobile,
                email=email,
                dob=dob,
                caste=str(row.get("caste", "")).strip() or None,
                sub_caste=str(row.get("sub_caste", "")).strip() or None,
                marital_status=str(row.get("marital_status", "Single")).strip() or "Single",
                height_cm=_safe_int(row.get("height_cm")),
                weight_kg=_safe_int(row.get("weight_kg")),
                blood_group=str(row.get("blood_group", "")).strip() or None,
                education=str(row.get("education", "")).strip() or None,
                occupation=str(row.get("occupation", "")).strip() or None,
                company=str(row.get("company", "")).strip() or None,
                annual_income=_safe_float(row.get("annual_income")),
                city=str(row.get("city", "")).strip() or "Surat",
                state=str(row.get("state", "")).strip() or "Gujarat",
                country=str(row.get("country", "")).strip() or "India",
                diet=str(row.get("diet", "")).strip() or "Vegetarian",
                status="pending",
                created_by_id=created_by_id,
                declaration_accepted=True,
            )
            profile.mulank = calculate_mulank(profile.dob)
            profile.bhagyank = calculate_bhagyank(profile.dob)
            profile.rashi = estimate_rashi(profile.dob)
            profile.nakshatra = estimate_nakshatra(profile.dob)

            db.session.add(profile)
            success_count += 1
        except Exception as e:
            errors.append({"row": row_num, "reason": str(e)})

    db.session.commit()
    return success_count, errors


def _safe_int(value):
    try:
        if pd.isnull(value):
            return None
        return int(value)
    except (ValueError, TypeError):
        return None


def _safe_float(value):
    try:
        if pd.isnull(value):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None
