from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.lookup import Caste, Occupation, Education, City

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/lookup/<table>")
@login_required
def lookup_autocomplete(table):
    models = {"castes": Caste, "occupations": Occupation, "educations": Education, "cities": City}
    model = models.get(table)
    if not model:
        return jsonify([])
    q = request.args.get("q", "")
    items = model.query.filter(model.name.ilike(f"%{q}%"), model.is_active.is_(True)).limit(10).all()
    return jsonify([i.name for i in items])


@api_bp.route("/biodata-assistant", methods=["POST"])
@login_required
def biodata_assistant():
    """Lightweight rule-based 'About Yourself' writing assistant.
    Generates a polished paragraph from structured profile fields the user
    supplies, without calling any external AI service."""
    data = request.get_json(force=True) or {}
    name = data.get("full_name", "").split(" ")[0] or "I"
    occupation = data.get("occupation", "a professional")
    education = data.get("education", "")
    hobbies = data.get("hobbies", "")
    family_values = data.get("family_values", "balanced")

    parts = [f"I am {occupation}" + (f" with a background in {education}." if education else ".")]
    if hobbies:
        parts.append(f"In my free time, I enjoy {hobbies}.")
    parts.append(f"I come from a family that values {family_values.lower()} principles, "
                 "and I am looking for a like-minded life partner to build a happy, respectful future together.")
    suggestion = " ".join(parts)
    return jsonify({"suggestion": suggestion})
