"""Gets the product data from our MCP server.

We never store products in our database, so every time we need product
information we ask the MCP server, which asks the external Product API.
"""

import os

import requests

BASE_URL = os.environ.get("PRODUCT_MCP_URL", "http://localhost:8001")


def read_answer(response):
    """Read the JSON of an answer, or None if it is not a good answer."""
    try:
        data = response.json()
    except ValueError:
        # Not JSON at all (a proxy error page, for example)
        return None

    if not data.get("success"):
        return None

    return data


def list_products(include_discontinued=False):
    """Return the list of all products, or None if it did not work.

    Discontinued products are hidden by default, but a branch can still have
    some in stock, so we can ask for them with include_discontinued.
    """
    params = {"include_discontinued": str(include_discontinued).lower()}

    try:
        response = requests.get(BASE_URL + "/products", params=params, timeout=10)
    except requests.exceptions.RequestException:
        return None

    data = read_answer(response)
    if data is None:
        return None

    return data["products"]


def get_product_details(sku):
    """Return the details of one product, or None if it did not work."""
    try:
        response = requests.get(BASE_URL + "/products/" + sku, timeout=10)
    except requests.exceptions.RequestException:
        return None

    data = read_answer(response)
    if data is None:
        return None

    return data["product"]
