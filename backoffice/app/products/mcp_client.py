"""Gets the product data from our MCP server.

We never store products in our database, so every time we need product
information we ask the MCP server, which asks the external Product API.
"""

import os

import requests

BASE_URL = os.environ.get("PRODUCT_MCP_URL", "http://localhost:8001")


def list_products():
    """Return the list of all products, or None if it did not work."""
    try:
        response = requests.get(BASE_URL + "/products", timeout=10)
    except requests.exceptions.RequestException:
        return None

    data = response.json()
    if not data["success"]:
        return None

    return data["products"]


def get_product_details(sku):
    """Return the details of one product, or None if it did not work."""
    try:
        response = requests.get(BASE_URL + "/products/" + sku, timeout=10)
    except requests.exceptions.RequestException:
        return None

    data = response.json()
    if not data["success"]:
        return None

    return data["product"]
