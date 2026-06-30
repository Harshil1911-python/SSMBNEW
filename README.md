# Citylight Sindhi Samaj — Marriage Bureau Management Software

A full-stack Flask matrimonial-bureau management system built for **Citylight Sindhi Samaj, Surat**. Light blue & white themed, glassmorphism UI, role-based access (Admin / Member / Bride-Groom), automated biodata + QR generation, Kundli (Gun Milan) matching, CSV/Excel import-export, backups, and full admin controls. Render.com deploy-ready.

## Tech Stack
Backend: Python 3.12, Flask, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, Flask-Mail, Flask-Caching, Flask-Limiter, Pillow, WeasyPrint, qrcode, pandas, openpyxl.
Frontend: HTML5, Bootstrap 5, vanilla JS, Jinja2.
Database: PostgreSQL (production) / SQLite (development).

## Local Setup

```bash
python3.12 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # edit values as needed

flask db init                     # first time only
flask db migrate -m "init"
flask db upgrade
flask seed                        # creates admin user + master data

flask run                         # http://127.0.0.1:5000
```

**Default admin login (created by `flask seed`):**
`admin@citylightsindhisamaj.org` / `Admin@123` — change this immediately after first login.

### System dependency note (WeasyPrint)
WeasyPrint needs system libraries (Pango, Cairo, GDK-Pixbuf). On Render's Python runtime these are pre-installed; for local Linux: `sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev`. On macOS: `brew install pango`.

## Deploying to Render

1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint** and point it at this repo — `render.yaml` provisions the web service and a free PostgreSQL database automatically.
3. Set the `MAIL_USERNAME` / `MAIL_PASSWORD` secrets in the Render dashboard (Environment tab).
4. The `release` step in `Procfile` runs `flask db upgrade && flask seed` automatically on each deploy.
5. Once live, log in with the seeded admin account and change the password immediately under **Admin → Manage Users**.

## Project Structure

```
app/
  models/        SQLAlchemy models (User, Profile, lookups, logs)
  forms/         Flask-WTF forms
  routes/        Blueprints: auth, public, profile, member, admin, api
  services/      Import/export/backup business logic
  utils/         Astrology/numerology, Kundli matching, image/QR/PDF helpers, decorators
  templates/      Jinja2 templates (auth, public, profile, member, admin, biodata_templates)
  static/        CSS, JS, uploaded photos/documents/qr/biodata/backups
config.py         Environment-based configuration
run.py / wsgi.py   Local dev runner / production WSGI entrypoint
render.yaml        Render Blueprint (web service + Postgres)
Procfile            Process + release commands
requirements.txt    Python dependencies
```

## Roles & Access

- **Admin** — full control: approvals, user/member management, master data, theme/branding, import/export, backups, logs, reports.
- **Member** — approved committee members: browse/search/filter all approved profiles, shortlist, add notes, download biodata/QR/Kundli reports, compare two profiles, export selected profiles.
- **Bride/Groom** — public self-registration; can edit their own profile until admin approval, after which it becomes read-only.

## Key Features Implemented

- Self-registration + admin-added registrations, with a 150+ field marriage-bureau form (basic, astrology/caste, physical, lifestyle, family, career, partner preference, medical, social links).
- Photo upload with auto-orient, compression, thumbnailing, and watermarking; multi-document upload (Aadhar, PAN, education, income proof, etc.).
- **View Persons** page with a left filter panel and a responsive 3-card-per-row grid, sub-categorized by gender/marital status.
- Advanced multi-field filtering + global search by name/registration number/mobile/education/occupation/city.
- Automatic **QR code** generation linking to a public, read-only profile view with confidential fields hidden.
- **10 professional biodata PDF templates** (WeasyPrint, A4, print-ready, branded with logo/QR/footer).
- **Kundli Matching Engine** — Ashtakoot-style Gun Milan scoring (8 kootas, 36-point scale), Manglik compatibility check, Top 10/25/50 recommendations, and a full two-profile compare/match report.
- CSV/Excel **import** with required-field validation, duplicate (mobile) skipping, and a downloadable per-row error report; CSV/Excel **export** of filtered, selected, or the entire database.
- JSON-based one-click **backup** (downloadable) and **restore** of master/lookup data.
- Soft-delete + **Trash Bin** with restore for profiles.
- Admin-manageable master data: Caste, Occupation, Education, Country, State, City, Blood Group, Habits, Languages.
- Site settings: name, city, logo, primary/secondary theme colors, background, contact info, social links — applied live across the site.
- **Activity Logs** and **Login Logs** for full auditability.
- Dashboard with live stats (gender/marital-status/status breakdown, today's registrations) and a 6-month registrations chart (Chart.js).
- Reports: education / occupation / city / marital-status / religion / blood-group distributions.
- OTP-based forgot/reset password flow; account activation/deactivation; default-password reset by admin.
- Rule-based "About Yourself" writing assistant (no external AI dependency) and live profile-completeness percentage.
- Security: Werkzeug password hashing, CSRF protection (Flask-WTF), rate limiting on auth endpoints (Flask-Limiter), session cookie hardening, role-based route decorators, parametrized SQLAlchemy queries.
- Light blue & white glassmorphism theme with a built-in dark-mode toggle, fully responsive (Bootstrap 5 grid), watermarked "TECH SERENIA" footer mark, and "POWERED BY SERENIA UPTIME BOTS" footer credit on every page.

## Honest Scope Notes

This is a large, genuinely production-shaped codebase, but a handful of items from the original spec are implemented as solid, extensible foundations rather than exhaustive subsystems, in the interest of shipping a coherent, working system:

- **Astrology values** (Rashi/Nakshatra/Mulank/Bhagyank/Gun Milan) use deterministic, explainable formulas rather than a licensed Vedic-astrology ephemeris library — accurate for numerology, approximate for sidereal Rashi/Nakshatra. Swap in a dedicated astrology API/library (e.g. via `pyswisseph`) under `app/utils/astrology.py` and `kundli_matching.py` if precise sidereal calculations are required.
- **SMS/WhatsApp** integrations are "ready" (UI buttons, contact fields, `whatsapp_number` setting) but not wired to a paid gateway (Twilio/Gupshup) — add credentials and a thin service module when you choose a provider.
- **AI Photo Quality Check** and **AI Biodata Writing Assistant** are implemented as fast, dependency-free rule-based helpers (resolution/orientation checks, templated paragraph generation) rather than calls to a paid vision/LLM API — easy to upgrade by adding an API call inside `app/utils/image_utils.py` / `app/routes/api.py`.
- **Multi-language UI** (Hindi/Sindhi/Gujarati) — the data model and content support it (`languages_known`, `mother_tongue`, lookup table), but full Flask-Babel i18n wiring for every template string is not included; recommended as the next iteration via `flask-babel`.
- **Infinite scroll** uses classic pagination instead, which is more reliable for the filter-heavy "View Persons" page; infinite scroll can be layered on top via the existing `/persons?page=N` endpoint.

These are clearly isolated and don't block deployment — the system installs, migrates, seeds, and runs end-to-end today.
