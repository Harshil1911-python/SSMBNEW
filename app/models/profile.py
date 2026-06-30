from datetime import datetime, date
from app.extensions import db


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    registration_no = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # Basic
    full_name = db.Column(db.String(150), nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # Male, Female
    bride_or_groom = db.Column(db.String(10), nullable=False)  # Bride, Groom
    father_name = db.Column(db.String(150))
    mother_name = db.Column(db.String(150))
    guardian_name = db.Column(db.String(150))

    mobile = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(150))
    alternate_contact = db.Column(db.String(20))

    dob = db.Column(db.Date)
    time_of_birth = db.Column(db.String(20))
    place_of_birth = db.Column(db.String(150))
    birth_year = db.Column(db.Integer)

    # Numerology / Astrology
    mulank = db.Column(db.Integer)
    bhagyank = db.Column(db.Integer)
    rashi = db.Column(db.String(50))
    nakshatra = db.Column(db.String(50))
    manglik = db.Column(db.String(20), default="No")  # Yes / No / Anshik

    gotra = db.Column(db.String(100))
    caste = db.Column(db.String(100))
    sub_caste = db.Column(db.String(100))

    marital_status = db.Column(db.String(20), default="Single")  # Single, Married, Divorced, Widow, Widower

    height_cm = db.Column(db.Integer)
    weight_kg = db.Column(db.Integer)
    blood_group = db.Column(db.String(10))
    complexion = db.Column(db.String(30))
    body_type = db.Column(db.String(30))
    physical_disability = db.Column(db.String(150), default="None")

    nationality = db.Column(db.String(50), default="Indian")
    religion = db.Column(db.String(50), default="Hindu")
    mother_tongue = db.Column(db.String(50), default="Sindhi")
    languages_known = db.Column(db.String(255))

    current_address = db.Column(db.Text)
    permanent_address = db.Column(db.Text)
    country = db.Column(db.String(80), default="India")
    state = db.Column(db.String(80), default="Gujarat")
    city = db.Column(db.String(80), default="Surat")
    pincode = db.Column(db.String(10))

    education = db.Column(db.String(150))
    college = db.Column(db.String(150))
    university = db.Column(db.String(150))
    occupation = db.Column(db.String(150))
    designation = db.Column(db.String(150))
    company = db.Column(db.String(150))
    business_name = db.Column(db.String(150))
    annual_income = db.Column(db.Numeric(12, 2))
    monthly_income = db.Column(db.Numeric(12, 2))
    career_details = db.Column(db.Text)

    diet = db.Column(db.String(20), default="Vegetarian")  # Vegetarian, Non Vegetarian, Eggitarian
    smoking = db.Column(db.String(10), default="No")
    drinking = db.Column(db.String(10), default="No")
    habits = db.Column(db.String(255))
    hobbies = db.Column(db.String(255))
    interests = db.Column(db.String(255))
    about_yourself = db.Column(db.Text)

    father_occupation = db.Column(db.String(150))
    mother_occupation = db.Column(db.String(150))
    brothers = db.Column(db.Integer, default=0)
    sisters = db.Column(db.Integer, default=0)
    family_type = db.Column(db.String(30))  # Joint, Nuclear
    family_values = db.Column(db.String(30))  # Traditional, Moderate, Liberal
    native_place = db.Column(db.String(150))
    property_details = db.Column(db.Text)
    vehicle = db.Column(db.String(150))
    passport = db.Column(db.String(10), default="No")
    visa_status = db.Column(db.String(100))

    instagram = db.Column(db.String(150))
    facebook = db.Column(db.String(150))
    linkedin = db.Column(db.String(150))
    website = db.Column(db.String(150))

    pref_age_min = db.Column(db.Integer)
    pref_age_max = db.Column(db.Integer)
    pref_height = db.Column(db.String(50))
    pref_education = db.Column(db.String(150))
    pref_occupation = db.Column(db.String(150))
    pref_income = db.Column(db.String(100))
    pref_caste = db.Column(db.String(100))
    pref_location = db.Column(db.String(150))
    pref_country = db.Column(db.String(80))
    pref_marital_status = db.Column(db.String(50))
    about_desired_partner = db.Column(db.Text)

    allergies = db.Column(db.String(255))
    health_conditions = db.Column(db.String(255))
    covid_vaccinated = db.Column(db.String(10), default="Yes")

    # Status
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    profile_completeness = db.Column(db.Integer, default=0)

    qr_code_path = db.Column(db.String(255))

    declaration_accepted = db.Column(db.Boolean, default=False)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    assigned_member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)

    photos = db.relationship("ProfilePhoto", backref="profile", cascade="all, delete-orphan", lazy="dynamic")
    documents = db.relationship("ProfileDocument", backref="profile", cascade="all, delete-orphan", lazy="dynamic")
    notes = db.relationship("ProfileNote", backref="profile", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    @property
    def height_display(self):
        if not self.height_cm:
            return "-"
        feet = self.height_cm // 30.48
        inches = round((self.height_cm / 2.54) % 12)
        return f"{int(feet)}'{inches}\" ({self.height_cm} cm)"

    @property
    def main_photo(self):
        return self.photos.filter_by(is_main=True).first() or self.photos.first()

    def __repr__(self):
        return f"<Profile {self.registration_no} {self.full_name}>"


class ProfilePhoto(db.Model):
    __tablename__ = "profile_photos"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255))
    photo_type = db.Column(db.String(20), default="gallery")  # profile, full_length, family, gallery
    is_main = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProfileDocument(db.Model):
    __tablename__ = "profile_documents"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    doc_type = db.Column(db.String(50))  # aadhar, pan, passport, education_certificate, income_proof, job_proof,
    # business_proof, address_proof, kundli_pdf, biodata_pdf, other
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProfileNote(db.Model):
    __tablename__ = "profile_notes"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    note = db.Column(db.Text)
    is_interested = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    member = db.relationship("User")


class Shortlist(db.Model):
    __tablename__ = "shortlists"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("member_id", "profile_id", name="uq_member_profile_shortlist"),)
