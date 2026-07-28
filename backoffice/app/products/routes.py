from flask import Blueprint, jsonify

from app.auth.decorators import login_required
from app.products import mcp_client

products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.route("", methods=["GET"])
@login_required
def list_products():
    products = mcp_client.list_products()

    if products is None:
        return jsonify({"error": "The product catalog is not available right now."}), 503

    return jsonify(products), 200

