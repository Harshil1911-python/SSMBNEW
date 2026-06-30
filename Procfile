web: gunicorn wsgi:app --workers=3 --threads=2 --timeout=120
release: flask db upgrade && flask seed
