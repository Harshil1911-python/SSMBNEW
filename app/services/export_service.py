import os
import uuid
import pandas as pd
from flask import current_app

EXPORT_COLUMNS = [
    "registration_no", "full_name", "gender", "bride_or_groom", "dob", "mobile", "email",
    "caste", "sub_caste", "marital_status", "height_cm", "weight_kg", "blood_group",
    "education", "occupation", "company", "annual_income", "city", "state", "country",
    "diet", "smoking", "drinking", "status", "created_at",
]


def _profile_to_row(p):
    return {col: getattr(p, col, None) for col in EXPORT_COLUMNS}


def export_profiles_excel(profiles, filename_prefix="profiles"):
    rows = [_profile_to_row(p) for p in profiles]
    df = pd.DataFrame(rows, columns=EXPORT_COLUMNS)

    out_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "exports")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.xlsx"
    path = os.path.join(out_dir, filename)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Profiles")
        worksheet = writer.sheets["Profiles"]
        for i, col in enumerate(EXPORT_COLUMNS, start=1):
            worksheet.column_dimensions[worksheet.cell(row=1, column=i).column_letter].width = 18

    return path


def export_profiles_csv(profiles, filename_prefix="profiles"):
    rows = [_profile_to_row(p) for p in profiles]
    df = pd.DataFrame(rows, columns=EXPORT_COLUMNS)

    out_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "exports")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.csv"
    path = os.path.join(out_dir, filename)
    df.to_csv(path, index=False)
    return path


def csv_import_template_path():
    out_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "exports")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "csv_import_template.csv")
    df = pd.DataFrame(columns=[
        "full_name", "gender", "bride_or_groom", "father_name", "mother_name", "mobile", "email",
        "dob", "caste", "sub_caste", "marital_status", "height_cm", "weight_kg", "blood_group",
        "education", "occupation", "company", "annual_income", "city", "state", "country", "diet",
    ])
    df.to_csv(path, index=False)
    return path
