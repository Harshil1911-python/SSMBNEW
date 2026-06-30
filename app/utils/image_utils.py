import os
import uuid
from PIL import Image, ImageOps, ImageDraw, ImageFont
from flask import current_app


def _ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def allowed_image(filename):
    return _ext(filename) in current_app.config["ALLOWED_IMAGE_EXT"]


def allowed_document(filename):
    return _ext(filename) in current_app.config["ALLOWED_DOC_EXT"]


def save_photo(file_storage, subfolder="photos", max_size=(1200, 1200), watermark_text=None):
    """Save an uploaded image: auto-orient, resize/compress, optional watermark.
    Returns (filename, thumbnail_filename)."""
    ext = _ext(file_storage.filename) or "jpg"
    base_name = f"{uuid.uuid4().hex}.{ext if ext in ('jpg', 'jpeg', 'png', 'webp') else 'jpg'}"

    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, base_name)

    img = Image.open(file_storage.stream)
    img = ImageOps.exif_transpose(img)  # auto rotate
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail(max_size, Image.LANCZOS)

    if watermark_text:
        img = apply_watermark(img, watermark_text)

    img.save(full_path, quality=85, optimize=True)

    # thumbnail
    thumb_name = f"thumb_{base_name}"
    thumb_path = os.path.join(upload_dir, thumb_name)
    thumb_img = img.copy()
    thumb_img.thumbnail((300, 300), Image.LANCZOS)
    thumb_img.save(thumb_path, quality=80, optimize=True)

    return base_name, thumb_name


def apply_watermark(img, text):
    """Apply a semi-transparent diagonal watermark text to the bottom of an image."""
    watermarked = img.convert("RGBA")
    overlay = Image.new("RGBA", watermarked.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=max(14, watermarked.width // 25))
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = watermarked.width - text_w - 12
    y = watermarked.height - text_h - 12
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 140))

    combined = Image.alpha_composite(watermarked, overlay).convert("RGB")
    return combined


def save_document(file_storage, subfolder="documents"):
    ext = _ext(file_storage.filename) or "pdf"
    base_name = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, base_name)
    file_storage.save(full_path)
    return base_name


def delete_file(subfolder, filename):
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder, filename)
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
