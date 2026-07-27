from flask import Flask, jsonify, request
import product_api_client

app = Flask(__name__)


def respond(result):
    """Turn a client result into a JSON response with the matching status code."""

    if result["success"]:
        return jsonify(result), 200
    if result.get("code") == "not_found":
        return jsonify(result), 404
    return jsonify(result), 502


@app.route("/products")
def products():
    include_discontinued = request.args.get("include_discontinued") == "true"

    return respond(product_api_client.list_products(include_discontinued))


@app.route("/products/<sku>")
def product_details(sku):
    return respond(product_api_client.get_product_details(sku))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
