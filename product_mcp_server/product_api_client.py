import os
import requests

BASE_URL = os.environ.get("PRODUCT_API_BASE_URL", "http://localhost:5001")
API_URL = BASE_URL + "/api/v1/products"

PAGE_SIZE = 100  # the Product API refuses any limit above 100

NO_RESPONSE = {"success": False, "error": "The Product API is not responding."}
API_ERROR = {"success": False, "error": "The Product API returned an error."}


def read_json(response):
    """Read the JSON of a response, or None if there is no JSON in it."""

    try:
        return response.json()
    except ValueError:
        return None


def summary(p):
    """Keep the fields we show in a list.

    We read every field with .get(): if the real Product API names one
    differently we return it empty instead of crashing with a 500.
    """

    return {
        "sku": p.get("sku"),
        "name": p.get("name"),
        "category": p.get("category"),
        "brand": p.get("brand"),
        "unit_price": p.get("unit_price"),
        "currency": p.get("currency"),
        "discontinued": p.get("discontinued"),
    }


def details(p):
    """Keep the fields we show for one product."""

    supplier = p.get("supplier") or {}

    product = summary(p)
    product["description"] = p.get("description")
    product["supplier_name"] = supplier.get("name")
    product["supplier_country"] = supplier.get("country")

    return product


def list_products(include_discontinued: bool = False) -> dict:
    """List the products available in the external catalog."""

    products = []
    offset = 0

    while True:
        params = {
            "limit": PAGE_SIZE,
            "offset": offset,
            "include_discontinued": str(include_discontinued).lower(),
        }

        try:
            response = requests.get(API_URL, params=params, timeout=10)
        except requests.exceptions.RequestException:
            return NO_RESPONSE

        if response.status_code != 200:
            return API_ERROR

        data = read_json(response)
        if data is None:
            return API_ERROR

        results = data.get("results", [])

        for p in results:
            products.append(summary(p))

        offset += len(results)

        if not results or offset >= data.get("count", 0):
            break

    return {"success": True, "count": len(products), "products": products}


def get_product_details(sku: str) -> dict:
    """Get the details of one product, identified by its SKU (example: HB-LAP-1001)."""

    try:
        response = requests.get(API_URL + "/" + sku, timeout=10)
    except requests.exceptions.RequestException:
        return NO_RESPONSE

    if response.status_code == 404:
        return {
            "success": False,
            "code": "not_found",
            "error": "No product found with SKU " + sku,
        }

    if response.status_code != 200:
        return API_ERROR

    p = read_json(response)
    if p is None:
        return API_ERROR

    return {"success": True, "product": details(p)}
