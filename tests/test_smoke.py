"""
Basic smoke tests for Citylight Sindhi Samaj Marriage Bureau.
Run with:  pytest tests/ -v
"""
import pytest
import os
os.environ["FLASK_ENV"] = "development"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["WTF_CSRF_ENABLED"] = "False"
os.environ["SECRET_KEY"] = "test-secret-key"


@pytest.fixture(scope="session")
def app():
    from app import create_app
    _app = create_app("development")
    _app.config["TESTING"] = True
    _app.config["WTF_CSRF_ENABLED"] = False
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return _app


@pytest.fixture(scope="session")
def db(app):
    from app.extensions import db as _db
    with app.app_context():
        _db.create_all()
        from app.utils.seed import run_seed
        run_seed()
        yield _db
        _db.drop_all()


@pytest.fixture
def client(app, db):
    return app.test_client()


def test_home_page_loads(client, app):
    with app.app_context():
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Sindhi" in resp.data


def test_login_page_loads(client, app):
    with app.app_context():
        resp = client.get("/auth/login")
        assert resp.status_code == 200


def test_register_page_loads(client, app):
    with app.app_context():
        resp = client.get("/auth/register")
        assert resp.status_code == 200


def test_admin_redirects_anonymous(client, app):
    with app.app_context():
        resp = client.get("/admin/dashboard", follow_redirects=False)
        # Should redirect to login or return 403
        assert resp.status_code in (302, 403)


def test_view_persons_redirects_anonymous(client, app):
    with app.app_context():
        resp = client.get("/persons", follow_redirects=False)
        assert resp.status_code in (302, 403)


def test_about_page(client, app):
    with app.app_context():
        resp = client.get("/about")
        assert resp.status_code == 200


def test_404_page(client, app):
    with app.app_context():
        resp = client.get("/this-does-not-exist")
        assert resp.status_code == 404


def test_admin_login(client, app):
    with app.app_context():
        resp = client.post("/auth/login", data={
            "email": "admin@citylightsindhisamaj.org",
            "password": "Admin@123",
            "remember": False,
        }, follow_redirects=True)
        assert resp.status_code == 200


def test_numerology_helpers():
    from datetime import date
    from app.utils.astrology import calculate_mulank, calculate_bhagyank, estimate_rashi, estimate_nakshatra

    dob = date(1990, 3, 15)
    assert calculate_mulank(dob) == 6          # digit_sum(15) = 6
    assert calculate_bhagyank(dob) is not None
    assert estimate_rashi(dob) is not None
    assert estimate_nakshatra(dob) is not None
    assert calculate_mulank(None) is None


def test_registration_number_format(app, db):
    with app.app_context():
        from app.utils.helpers import generate_registration_no
        reg_no = generate_registration_no()
        assert reg_no.startswith("CSS")
        assert len(reg_no) >= 7
