from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, SelectField, IntegerField, DateField, TextAreaField,
    DecimalField, BooleanField, SubmitField, MultipleFileField
)
from wtforms.validators import DataRequired, Optional, Email, Length

GENDER_CHOICES = [("Male", "Male"), ("Female", "Female")]
ROLE_CHOICES = [("Groom", "Groom"), ("Bride", "Bride")]
MARITAL_CHOICES = [("Single", "Single"), ("Married", "Married"), ("Divorced", "Divorced"),
                    ("Widow", "Widow"), ("Widower", "Widower")]
DIET_CHOICES = [("Vegetarian", "Vegetarian"), ("Non Vegetarian", "Non Vegetarian"), ("Eggitarian", "Eggitarian")]
YN_CHOICES = [("No", "No"), ("Yes", "Yes")]
MANGLIK_CHOICES = [("No", "No"), ("Yes", "Yes"), ("Anshik", "Anshik")]
FAMILY_TYPE_CHOICES = [("Nuclear", "Nuclear"), ("Joint", "Joint")]
FAMILY_VALUES_CHOICES = [("Traditional", "Traditional"), ("Moderate", "Moderate"), ("Liberal", "Liberal")]


class ProfileForm(FlaskForm):
    # Basic
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    gender = SelectField("Gender", choices=GENDER_CHOICES, validators=[DataRequired()])
    bride_or_groom = SelectField("Bride/Groom", choices=ROLE_CHOICES, validators=[DataRequired()])
    father_name = StringField("Father's Name", validators=[Optional(), Length(max=150)])
    mother_name = StringField("Mother's Name", validators=[Optional(), Length(max=150)])
    guardian_name = StringField("Guardian Name", validators=[Optional(), Length(max=150)])

    mobile = StringField("Mobile Number", validators=[DataRequired(), Length(max=20)])
    whatsapp = StringField("WhatsApp Number", validators=[Optional(), Length(max=20)])
    email = StringField("Email", validators=[Optional(), Email()])
    alternate_contact = StringField("Alternate Contact", validators=[Optional(), Length(max=20)])

    dob = DateField("Date of Birth", validators=[DataRequired()])
    time_of_birth = StringField("Time of Birth", validators=[Optional()])
    place_of_birth = StringField("Place of Birth", validators=[Optional()])

    gotra = StringField("Gotra", validators=[Optional()])
    caste = StringField("Sindhi Caste", validators=[Optional()])
    sub_caste = StringField("Sub Caste", validators=[Optional()])
    manglik = SelectField("Manglik", choices=MANGLIK_CHOICES, validators=[Optional()])

    marital_status = SelectField("Marital Status", choices=MARITAL_CHOICES, validators=[DataRequired()])

    height_cm = IntegerField("Height (cm)", validators=[Optional()])
    weight_kg = IntegerField("Weight (kg)", validators=[Optional()])
    blood_group = StringField("Blood Group", validators=[Optional(), Length(max=10)])
    complexion = SelectField("Complexion", choices=[("Fair", "Fair"), ("Wheatish", "Wheatish"), ("Dark", "Dark")],
                              validators=[Optional()])
    body_type = SelectField("Body Type", choices=[("Slim", "Slim"), ("Average", "Average"), ("Athletic", "Athletic"),
                                                    ("Heavy", "Heavy")], validators=[Optional()])
    physical_disability = StringField("Physical Disability", validators=[Optional()])

    nationality = StringField("Nationality", validators=[Optional()], default="Indian")
    religion = StringField("Religion", validators=[Optional()], default="Hindu")
    mother_tongue = StringField("Mother Tongue", validators=[Optional()], default="Sindhi")
    languages_known = StringField("Languages Known (comma separated)", validators=[Optional()])

    current_address = TextAreaField("Current Address", validators=[Optional()])
    permanent_address = TextAreaField("Permanent Address", validators=[Optional()])
    country = StringField("Country", validators=[Optional()], default="India")
    state = StringField("State", validators=[Optional()], default="Gujarat")
    city = StringField("City", validators=[Optional()], default="Surat")
    pincode = StringField("Pincode", validators=[Optional(), Length(max=10)])

    education = StringField("Education", validators=[Optional()])
    college = StringField("College", validators=[Optional()])
    university = StringField("University", validators=[Optional()])
    occupation = StringField("Occupation", validators=[Optional()])
    designation = StringField("Designation", validators=[Optional()])
    company = StringField("Company", validators=[Optional()])
    business_name = StringField("Business Name", validators=[Optional()])
    annual_income = DecimalField("Annual Income", validators=[Optional()])
    monthly_income = DecimalField("Monthly Income", validators=[Optional()])
    career_details = TextAreaField("Career Details", validators=[Optional()])

    diet = SelectField("Diet", choices=DIET_CHOICES, validators=[Optional()])
    smoking = SelectField("Smoking", choices=YN_CHOICES, validators=[Optional()])
    drinking = SelectField("Drinking", choices=YN_CHOICES, validators=[Optional()])
    habits = StringField("Habits", validators=[Optional()])
    hobbies = StringField("Hobbies", validators=[Optional()])
    interests = StringField("Interests", validators=[Optional()])
    about_yourself = TextAreaField("About Yourself", validators=[Optional()])

    father_occupation = StringField("Father's Occupation", validators=[Optional()])
    mother_occupation = StringField("Mother's Occupation", validators=[Optional()])
    brothers = IntegerField("Brothers", validators=[Optional()], default=0)
    sisters = IntegerField("Sisters", validators=[Optional()], default=0)
    family_type = SelectField("Family Type", choices=FAMILY_TYPE_CHOICES, validators=[Optional()])
    family_values = SelectField("Family Values", choices=FAMILY_VALUES_CHOICES, validators=[Optional()])
    native_place = StringField("Native Place", validators=[Optional()])
    property_details = TextAreaField("Property Details", validators=[Optional()])
    vehicle = StringField("Vehicle", validators=[Optional()])
    passport = SelectField("Passport", choices=YN_CHOICES, validators=[Optional()])
    visa_status = StringField("Visa Status", validators=[Optional()])

    instagram = StringField("Instagram", validators=[Optional()])
    facebook = StringField("Facebook", validators=[Optional()])
    linkedin = StringField("LinkedIn", validators=[Optional()])
    website = StringField("Website", validators=[Optional()])

    pref_age_min = IntegerField("Preferred Age (Min)", validators=[Optional()])
    pref_age_max = IntegerField("Preferred Age (Max)", validators=[Optional()])
    pref_height = StringField("Preferred Height", validators=[Optional()])
    pref_education = StringField("Preferred Education", validators=[Optional()])
    pref_occupation = StringField("Preferred Occupation", validators=[Optional()])
    pref_income = StringField("Preferred Income", validators=[Optional()])
    pref_caste = StringField("Preferred Caste", validators=[Optional()])
    pref_location = StringField("Preferred Location", validators=[Optional()])
    pref_country = StringField("Preferred Country", validators=[Optional()])
    pref_marital_status = StringField("Preferred Marital Status", validators=[Optional()])
    about_desired_partner = TextAreaField("About Desired Partner", validators=[Optional()])

    allergies = StringField("Allergies", validators=[Optional()])
    health_conditions = StringField("Health Conditions", validators=[Optional()])
    covid_vaccinated = SelectField("COVID Vaccinated", choices=YN_CHOICES, validators=[Optional()])

    profile_photo = FileField("Profile Photo", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    full_length_photo = FileField("Full Length Photo", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    family_photo = FileField("Family Photo", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"])])
    gallery_photos = MultipleFileField("Additional Photos", validators=[Optional()])

    aadhar_doc = FileField("Aadhar Card", validators=[Optional(), FileAllowed(["pdf", "jpg", "jpeg", "png"])])
    pan_doc = FileField("PAN Card", validators=[Optional(), FileAllowed(["pdf", "jpg", "jpeg", "png"])])
    education_doc = FileField("Education Certificate", validators=[Optional(), FileAllowed(["pdf", "jpg", "jpeg", "png"])])
    income_doc = FileField("Income Proof", validators=[Optional(), FileAllowed(["pdf", "jpg", "jpeg", "png"])])

    declaration_accepted = BooleanField("I declare the above information is true", validators=[DataRequired()])
    submit = SubmitField("Submit Registration")
