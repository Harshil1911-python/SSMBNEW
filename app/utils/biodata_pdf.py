import os
from flask import render_template, current_app
from weasyprint import HTML


def generate_biodata_pdf(profile, template_slug="classic-blue"):
    """Renders the biodata HTML template and converts to PDF. Returns absolute file path."""
    html_string = render_template(
        f"profile/biodata_templates/{template_slug}.html",
        profile=profile,
    )
    out_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "biodata")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"biodata_{profile.registration_no}_{template_slug}.pdf"
    out_path = os.path.join(out_dir, filename)

    HTML(string=html_string, base_url=current_app.root_path).write_pdf(out_path)
    return out_path, filename
