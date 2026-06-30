import os
from flask import Flask, render_template, request
from config import config_map
from app.extensions import db, migrate, login_manager, mail, cache, limiter, csrf


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    for sub in ("photos", "documents", "qr", "biodata"):
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], sub), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.public import public_bp
    from app.routes.member import member_bp
    from app.routes.admin import admin_bp
    from app.routes.profile import profile_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(api_bp)

    from app.utils.context_processors import register_context_processors
    register_context_processors(app)

    from app.utils.template_filters import register_filters
    register_filters(app)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.before_request
    def make_session_permanent():
        from flask import session
        session.permanent = True

    @app.cli.command("seed")
    def seed_command():
        """Seed the database with an admin user and lookup data."""
        from app.utils.seed import run_seed
        run_seed()
        print("Database seeded successfully.")

    return app
