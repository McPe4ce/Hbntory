"""Stand-in for the external Product API container.

This is NOT part of the delivered system. It exists so the team can run and test
the full stack without the provided Product API image. Swap it out by starting
compose with the `real` profile instead of `stub` (see docker-compose.yml).

The response shape is mirrored from what product_mcp_server/product_api_client.py
reads, so if the real API differs, that client is the file to compare against.
"""
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

MAX_LIMIT = 100

PRODUCTS = [
    {
        "sku": "HB-LAP-1001", "name": "Business Laptop 14",
        "description": "A 14 inch laptop for office work.",
        "category": "Computers", "brand": "Hbnt", "unit_price": 899.0,
        "currency": "EUR", "discontinued": False,
        "supplier": {"name": "NordSupply", "country": "SE"},
    },
    {
        "sku": "HB-MON-2101", "name": "Monitor 27 4K",
        "description": "A 27 inch 4K monitor.",
        "category": "Displays", "brand": "Hbnt", "unit_price": 349.0,
        "currency": "EUR", "discontinued": False,
        "supplier": {"name": "NordSupply", "country": "SE"},
    },
    {
        "sku": "HB-LGT-1801", "name": "Desk Lamp LED",
        "description": "An LED desk lamp with three light levels.",
        "category": "Office", "brand": "Hbnt", "unit_price": 39.0,
        "currency": "EUR", "discontinued": False,
        "supplier": {"name": "LumiCorp", "country": "FR"},
    },
    {
        "sku": "HB-KEY-2003", "name": "Mechanical Keyboard",
        "description": "A mechanical keyboard, no longer sold.",
        "category": "Peripherals", "brand": "Hbnt", "unit_price": 79.0,
        "currency": "EUR", "discontinued": True,
        "supplier": {"name": "LumiCorp", "country": "FR"},
    },
]


@app.route("/api/v1/products")
def list_products():
    include_discontinued = request.args.get("include_discontinued") == "true"

    try:
        limit = int(request.args.get("limit", MAX_LIMIT))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "limit and offset must be integers"}), 400

    # The real API refuses any limit above 100, so the stub does too.
    if limit > MAX_LIMIT:
        return jsonify({"error": "limit must be 100 or less"}), 400

    items = [p for p in PRODUCTS if include_discontinued or not p["discontinued"]]

    return jsonify({"count": len(items), "results": items[offset:offset + limit]})


@app.route("/api/v1/products/<sku>")
def product_details(sku):
    for product in PRODUCTS:
        if product["sku"] == sku:
            return jsonify(product)

    return jsonify({"error": "No product found with SKU " + sku}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
