import os
import json
import uuid
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile
from app.models.lookup import Caste, Occupation, Education, Country, State, City, BloodGroup, Habit, Language, \
    SiteSetting

BACKUP_MODELS = {
    "users": User,
    "profiles": Profile,
    "castes": Caste,
    "occupations": Occupation,
    "educations": Education,
    "countries": Country,
    "states": State,
    "cities": City,
    "blood_groups": BloodGroup,
    "habits": Habit,
    "languages": Language,
    "site_settings": SiteSetting,
}


def _serialize(obj):
    data = {}
    for col in obj.__table__.columns:
        value = getattr(obj, col.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        elif hasattr(value, "isoformat"):
            value = value.isoformat()
        else:
            try:
                json.dumps(value)
            except TypeError:
                value = str(value)
        data[col.name] = value
    return data


def create_backup():
    backup = {"created_at": datetime.utcnow().isoformat(), "tables": {}}
    for table_name, model in BACKUP_MODELS.items():
        backup["tables"][table_name] = [_serialize(obj) for obj in model.query.all()]

    out_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "backups")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
    path = os.path.join(out_dir, filename)
    with open(path, "w") as f:
        json.dump(backup, f, indent=2, default=str)
    return path, filename


def list_backups():
    out_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "backups")
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(os.listdir(out_dir), reverse=True)
    return files


def restore_backup_users_and_lookups(filepath):
    """Restores lookup tables and site settings only (safe, non-destructive
    restore of master data). Profile/user restore is intentionally NOT
    overwritten automatically to avoid clobbering live data; admins can
    review the JSON manually for full profile restoration."""
    with open(filepath) as f:
        backup = json.load(f)

    restored = 0
    for table_name in ("castes", "occupations", "educations", "countries", "states", "cities",
                        "blood_groups", "habits", "languages", "site_settings"):
        model = BACKUP_MODELS[table_name]
        for row in backup["tables"].get(table_name, []):
            existing = None
            if hasattr(model, "key"):
                existing = model.query.filter_by(key=row.get("key")).first()
            elif hasattr(model, "name"):
                existing = model.query.filter_by(name=row.get("name")).first()
            if not existing:
                row.pop("id", None)
                db.session.add(model(**row))
                restored += 1
    db.session.commit()
    return restored
