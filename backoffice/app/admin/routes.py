from app.models import User
from flask import Blueprint, request, jsonify
from app.auth.decorators import admin_required
import re
from sqlalchemy.exc import IntegrityError
from app.extensions import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _user_json(user):
    return {
            "id": user.id,
            "email": user.email,
            "branch_id": user.branch_id,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }


@admin_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    branch_id = data.get("branch_id")

    if not email or not password or not branch_id:
        return jsonify({"error": "email, branch_id and password are required"}), 400

    if not _EMAIL_RE.match(email):
        return jsonify({"error": "Email invalid format"}), 400

    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password) or not re.search(r"[^A-Za-z0-9]", password):
        return jsonify({"error": "Password is too weak"}), 400

    user = User(email, branch_id, is_admin=False)
    user.set_password(password)

    try:
        user.save()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "email already exists"}), 409
    return jsonify(_user_json(user)), 201


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([_user_json(user) for user in users]), 200