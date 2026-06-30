from functools import wraps
from flask import abort
from flask_login import current_user


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def admin_required(f):
    return roles_required("admin")(f)


def member_or_admin_required(f):
    return roles_required("admin", "member")(f)
