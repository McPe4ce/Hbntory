from flask import Blueprint, request, jsonify, g
from app.auth.decorators import common_user_required
from app.extensions import db
from app.models import Stock

stock_bp = Blueprint("stock", __name__, url_prefix="/stock")


def _stock_json(stock):
    return {
        "id": stock.id,
        "product_id": stock.product_id,
        "quantity": stock.quantity,
        "branch_id": stock.branch_id,
    }


def _parse_positive_amount(data):
    amount = data.get("quantity")
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        return None
    return amount


@stock_bp.route("/add", methods=["POST"])
@common_user_required
def add_stock():
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    amount = _parse_positive_amount(data)

    if not product_id or amount is None:
        return jsonify({"error": "product_id and a positive integer quantity are required"}), 400

    branch_id = g.current_user.branch_id
    stock = db.session.execute(
        db.select(Stock).filter_by(branch_id=branch_id, product_id=product_id)
    ).scalar_one_or_none()

    if stock is None:
        stock = Stock(product_id=product_id, quantity=amount, branch_id=branch_id)
        stock.save()
    else:
        stock.add_stock(amount)

    return jsonify(_stock_json(stock)), 200


@stock_bp.route("/remove", methods=["POST"])
@common_user_required
def remove_stock():
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    amount = _parse_positive_amount(data)

    if not product_id or amount is None:
        return jsonify({"error": "product_id and a positive integer quantity are required"}), 400

    branch_id = g.current_user.branch_id
    stock = db.session.execute(
        db.select(Stock).filter_by(branch_id=branch_id, product_id=product_id)
    ).scalar_one_or_none()

    if stock is None:
        return jsonify({"error": "No stock found for this product in your branch"}), 404

    try:
        stock.remove_stock(amount)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(_stock_json(stock)), 200


@stock_bp.route("", methods=["GET"])
@common_user_required
def list_stock():
    branch_id = g.current_user.branch_id
    stocks = db.session.execute(
        db.select(Stock).filter_by(branch_id=branch_id)
    ).scalars().all()
    return jsonify([_stock_json(s) for s in stocks]), 200


@stock_bp.route("/<product_id>", methods=["GET"])
@common_user_required
def consult_stock(product_id):
    branch_id = g.current_user.branch_id
    stock = db.session.execute(
        db.select(Stock).filter_by(branch_id=branch_id, product_id=product_id)
    ).scalar_one_or_none()

    if stock is None:
        return jsonify({"error": "No stock found for this product in your branch"}), 404

    return jsonify(_stock_json(stock)), 200
