from flask import current_app
from datetime import datetime


def register_context_processors(app):
    @app.context_processor
    def inject_globals():
        site_settings = {}
        try:
            from app.models.lookup import SiteSetting
            rows = SiteSetting.query.all()
            site_settings = {r.key: r.value for r in rows}
        except Exception:
            pass

        return dict(
            site_name=site_settings.get("site_name", current_app.config["SITE_NAME"]),
            site_city=site_settings.get("site_city", current_app.config["SITE_CITY"]),
            primary_color=site_settings.get("primary_color", current_app.config["PRIMARY_COLOR"]),
            secondary_color=site_settings.get("secondary_color", current_app.config["SECONDARY_COLOR"]),
            logo_path=site_settings.get("logo_path", ""),
            watermark_text=current_app.config["WATERMARK_TEXT"],
            footer_credit=current_app.config["FOOTER_CREDIT"],
            current_year=datetime.utcnow().year,
        )
