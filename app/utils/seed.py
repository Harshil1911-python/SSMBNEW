from app.extensions import db
from app.models.user import User
from app.models.lookup import Caste, Occupation, Education, Country, State, City, BloodGroup, Habit, Language, \
    SiteSetting, BiodataTemplate

DEFAULT_CASTES = ["Amil", "Bhaiband", "Sakkhar", "Shikarpuri", "Hyderabadi", "Larkana", "Other Sindhi"]
DEFAULT_OCCUPATIONS = ["Business", "Service - Private", "Service - Government", "Doctor", "Engineer", "CA/CS",
                        "Lawyer", "Teacher", "Self Employed", "Student", "Not Working"]
DEFAULT_EDUCATIONS = ["High School", "Diploma", "Graduate", "Post Graduate", "Doctorate", "Professional Degree"]
DEFAULT_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
DEFAULT_HABITS = ["Reading", "Travelling", "Cooking", "Sports", "Music", "Dancing", "Gaming", "Fitness"]
DEFAULT_LANGUAGES = ["Sindhi", "Hindi", "Gujarati", "English", "Marathi", "Punjabi"]

DEFAULT_BIODATA_TEMPLATES = [
    ("Classic Blue", "classic-blue", "#1E88E5"),
    ("Elegant Ivory", "elegant-ivory", "#C9A66B"),
    ("Modern Minimal", "modern-minimal", "#37474F"),
    ("Royal Maroon", "royal-maroon", "#8E2A38"),
    ("Floral Pink", "floral-pink", "#D81B60"),
    ("Traditional Gold", "traditional-gold", "#B8860B"),
    ("Corporate Grey", "corporate-grey", "#455A64"),
    ("Sindhi Heritage", "sindhi-heritage", "#0F6E51"),
    ("Soft Lavender", "soft-lavender", "#7E57C2"),
    ("Festive Saffron", "festive-saffron", "#E65100"),
]


def run_seed():
    if not User.query.filter_by(role="admin").first():
        admin = User(
            name="Citylight Admin",
            email="admin@citylightsindhisamaj.org",
            mobile="9999999999",
            role="admin",
            is_super_admin=True,
            is_active_account=True,
            is_email_verified=True,
        )
        admin.set_password("Admin@123")
        db.session.add(admin)

    def seed_lookup(model, names):
        for n in names:
            if not model.query.filter_by(name=n).first():
                db.session.add(model(name=n))

    seed_lookup(Caste, DEFAULT_CASTES)
    seed_lookup(Occupation, DEFAULT_OCCUPATIONS)
    seed_lookup(Education, DEFAULT_EDUCATIONS)
    seed_lookup(BloodGroup, DEFAULT_BLOOD_GROUPS)
    seed_lookup(Habit, DEFAULT_HABITS)
    seed_lookup(Language, DEFAULT_LANGUAGES)

    if not Country.query.filter_by(name="India").first():
        db.session.add(Country(name="India"))
    if not State.query.filter_by(name="Gujarat").first():
        db.session.add(State(name="Gujarat"))
    if not City.query.filter_by(name="Surat").first():
        db.session.add(City(name="Surat"))

    for name, slug, color in DEFAULT_BIODATA_TEMPLATES:
        if not BiodataTemplate.query.filter_by(slug=slug).first():
            db.session.add(BiodataTemplate(name=name, slug=slug, accent_color=color))

    defaults = {
        "site_name": "Citylight Sindhi Samaj Marriage Bureau",
        "site_city": "Surat",
        "primary_color": "#1E88E5",
        "secondary_color": "#E3F2FD",
        "logo_path": "",
    }
    for k, v in defaults.items():
        if not SiteSetting.query.filter_by(key=k).first():
            db.session.add(SiteSetting(key=k, value=v))

    db.session.commit()
