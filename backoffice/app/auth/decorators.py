from app.models import User
from functools import wraps
from flask import session, abort, redirect, url_for
from app.extensions import db


def login_required(func):

    @wraps(func)
    def wrapped(*args, **kwargs):
        """Checkpoint run on every request: routes if user is logged in
        And returns the Checkpoint at the end"""
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapped


def admin_required(func):
    """Checks if the logged in user is an admin and still exists"""
    @wraps(func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        user = db.session.get(User, session["user_id"])
        if user is None or not user.is_admin or not user.is_active:
            abort(403)
        return func(*args, **kwargs)
    return wrapped