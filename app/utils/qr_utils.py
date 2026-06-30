import os
import qrcode
from qrcode.image.pil import PilImage
from flask import current_app, url_for


def generate_profile_qr(profile):
    """Generates a QR code pointing to the public profile view page.
    Returns the filename saved under uploads/qr."""
    qr_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "qr")
    os.makedirs(qr_dir, exist_ok=True)

    target_url = url_for("public.view_qr_profile", registration_no=profile.registration_no, _external=True)

    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=PilImage, fill_color="#1E88E5", back_color="white")

    filename = f"qr_{profile.registration_no}.png"
    full_path = os.path.join(qr_dir, filename)
    img.save(full_path)
    return filename
