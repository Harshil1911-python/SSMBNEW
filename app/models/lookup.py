from datetime import datetime
from app.extensions import db


class LookupBase:
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Caste(LookupBase, db.Model):
    __tablename__ = "castes"


class Occupation(LookupBase, db.Model):
    __tablename__ = "occupations"


class Education(LookupBase, db.Model):
    __tablename__ = "educations"


class Country(LookupBase, db.Model):
    __tablename__ = "countries"


class State(LookupBase, db.Model):
    __tablename__ = "states"
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"))


class City(LookupBase, db.Model):
    __tablename__ = "cities"
    state_id = db.Column(db.Integer, db.ForeignKey("states.id"))


class BloodGroup(LookupBase, db.Model):
    __tablename__ = "blood_groups"


class Habit(LookupBase, db.Model):
    __tablename__ = "habits"


class Language(LookupBase, db.Model):
    __tablename__ = "languages"


class SiteSetting(db.Model):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")


class LoginLog(db.Model):
    __tablename__ = "login_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    email_attempted = db.Column(db.String(150))
    success = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BiodataTemplate(db.Model):
    __tablename__ = "biodata_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    accent_color = db.Column(db.String(20), default="#1E88E5")
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
