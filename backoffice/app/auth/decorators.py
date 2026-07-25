"""Route guards for the backoffice API.

Provides two decorators that authenticate requests via the JWT stored in the
``access_token`` cookie:

Permissions are never read from the token itself — only ``user_id`` is — so
authorization always reflects the current database state.
"""

from app.models import User
from functools import wraps
from flask import abort, request, current_app
from app.extensions import db
import jwt


def _user_id_from_token():
    """Reads and verifes the JWT from the "access_token" cookie and returns user_id"""
    token = request.cookies.get("access_token")
    if token is None:
        abort(401)

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.InvalidTokenError:
        abort(401)
    return payload["user_id"]


def login_required(func):
    """Allow the route only if the request carries a valid, unexpired token."""
    @wraps(func)
    def wrapped(*args, **kwargs):
        user_id = _user_id_from_token()
        user = db.session.get(User, user_id)
        if user is None or not user.is_active:
            return abort(403)
        return func(*args, **kwargs)
    return wrapped


def admin_required(func):
    """Checks if the logged in user is an admin and still exists"""
    @wraps(func)
    def wrapped(*args, **kwargs):
        user_id = _user_id_from_token()
        user = db.session.get(User, user_id)
        if user is None or not user.is_admin or not user.is_active:
            abort(403)
        return func(*args, **kwargs)
    return wrapped


def common_user_required(func):
    """Checks if the user is not an admin and still exists, for stocks modifications"""
    @wraps(func)
    def wrapped(*args, **kwargs):
        user_id = _user_id_from_token()
        user = db.session.get(User, user_id)

        if user is None or user.is_admin or not user.is_active:
            abort(403)
        return func(*args, **kwargs)
    return wrapped