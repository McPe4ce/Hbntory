from app.models import User, Branch
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

def weak_password(password):
    if not password:
        return True
    return (len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password) or not re.search(r"[^A-Za-z0-9]", password))


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

    if weak_password(password):
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


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404
    user.deactivate()
    return jsonify(_user_json(user)), 200


@admin_bp.route("/users/<user_id>", methods=["PATCH"])
@admin_required
def update_user(user_id):
    user = db.session.get(User, user_id)
    data = request.get_json(silent=True) or {}

    if user is None:
        return jsonify({"error": "User not found"}), 404

    if "branch_id" in data:
        new_branch_id = data["branch_id"]
        if not new_branch_id:
            return jsonify({"error": "branch_id cant be empty"}), 400
        
        if db.session.get(Branch, new_branch_id) is None:
            return jsonify({"error": "branch not found"}), 400
        user.branch_id = new_branch_id

    if "password" in data:
        new_password = data["password"]
        if weak_password(new_password):
            return jsonify({"error": "Password is too weak"}), 400
        user.set_password(new_password)
        
    user.save()
    return jsonify(_user_json(user)), 200

    