import os
import requests

BASE_URL = os.environ.get("PRODUCT_API_BASE_URL", "http://localhost:5001")
API_URL = BASE_URL + "/api/v1/products"

PAGE_SIZE = 100  # the Product API refuses any limit above 100

NO_RESPONSE = {"success": False, "error": "The Product API is not responding."}
API_ERROR = {"success": False, "error": "The Product API returned an error."}


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

        data = response.json()

        for p in data["results"]:
            products.append({
                "sku": p["sku"],
                "name": p["name"],
                "category": p["category"],
                "brand": p["brand"],
                "unit_price": p["unit_price"],
                "currency": p["currency"],
                "discontinued": p["discontinued"],
            })

        offset += len(data["results"])

        if not data["results"] or offset >= data["count"]:
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

    p = response.json()

    return {
        "success": True,
        "product": {
            "sku": p["sku"],
            "name": p["name"],
            "description": p["description"],
            "category": p["category"],
            "brand": p["brand"],
            "unit_price": p["unit_price"],
            "currency": p["currency"],
            "discontinued": p["discontinued"],
            "supplier_name": p["supplier"]["name"],
            "supplier_country": p["supplier"]["country"],
        },
    }
