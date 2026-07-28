from flask import Blueprint, request, jsonify, current_app, make_response, g
from datetime import datetime, timezone
from app.auth.decorators import login_required
from app.models import User
from app.extensions import db
import jwt

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    # A malformed body is not a server error: hashing a missing password raises.
    # Same generic answer as wrong credentials, so nothing leaks either way.
    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Email or Password is wrong"}), 401

    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if not (user and user.verify_password(password) and user.is_active):
        return jsonify({"error": "Email or Password is wrong"}), 401

    exp = datetime.now(timezone.utc) + current_app.config["JWT_EXPIRES"]
    token = jwt.encode(
        {"user_id": user.id, "exp": exp},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    resp = make_response(jsonify({"message": "Successfully logged in"}))
    resp.set_cookie(
        "access_token", token,
        httponly=True, samesite="Lax", secure=False, path="/",
        max_age=int(current_app.config["JWT_EXPIRES"].total_seconds())
    )
    return resp


@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"message": "You logged out"}))
    resp.delete_cookie("access_token", path="/", samesite="Lax")
    return resp


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    """Who is logged in, and which branch they operate on.

    The interface needs the branch *name*, not just its id, to state clearly
    which branch the user is acting on.
    """
    user = g.current_user

    return jsonify({
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "branch_id": user.branch_id,
        "branch_name": user.branch.branch_name if user.branch else None,
    }), 200


