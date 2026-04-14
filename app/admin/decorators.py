from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """
    Decorator to protect admin-only routes.
    Usage: @admin_required (place below @login_required)

    - If user is not authenticated     → 401 Unauthorized
    - If user is not an admin          → 403 Forbidden
    - If user is admin                 → proceed normally
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function