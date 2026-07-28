"""Public route used by the client web page.

There is no login here: anybody can send a question and get an answer.
We use REST because each question is independent (see docs/decisions.md).
"""

from flask import Blueprint, jsonify, request

from app.products import mcp_client
from app.public import query_engine

public_bp = Blueprint("public", __name__, url_prefix="/api")


@public_bp.after_request
def allow_the_page_to_call_us(response):
    """The page is served on another port, so we must allow it (CORS)."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@public_bp.route("/query", methods=["POST", "OPTIONS"])
def query():
    # The browser sends an OPTIONS request before the POST one.
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    question = data.get("question")

    # .strip() so that a question made only of spaces is refused too
    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "Please write a question."}), 400

    if len(question) > 500:
        return jsonify({"error": "Your question is too long (500 characters max)."}), 400

    # A branch can still have stock of a discontinued product, so we need
    # them too to be able to answer about it.
    catalog = mcp_client.list_products(include_discontinued=True)
    if catalog is None:
        return jsonify({"error": "The product catalog is not available right now."}), 503

    return jsonify({"answer": query_engine.answer(question, catalog)}), 200
