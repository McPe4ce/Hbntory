from fastmcp import FastMCP
import requests

mcp = FastMCP("product-mcp-server")

API_URL = "http://localhost:5001/api/v1/products"


@mcp.tool()
def list_products() -> dict:
    """List the products available in the external catalog."""

    try:
        response = requests.get(API_URL, timeout=10)
    except requests.exceptions.RequestException:
        return {"success": False, "error": "The Product API is not responding."}

    if response.status_code != 200:
        return {"success": False, "error": "The Product API returned an error."}

    data = response.json()

    products = []
    for p in data["results"]:
        products.append({
            "sku": p["sku"],
            "name": p["name"],
            "category": p["category"],
            "brand": p["brand"],
            "unit_price": p["unit_price"],
            "currency": p["currency"],
        })

    return {"success": True, "count": data["count"], "products": products}


@mcp.tool()
def get_product_details(sku: str) -> dict:
    """Get the details of one product, identified by its SKU (example: HB-LAP-1001)."""

    try:
        response = requests.get(API_URL + "/" + sku, timeout=10)
    except requests.exceptions.RequestException:
        return {"success": False, "error": "The Product API is not responding."}

    if response.status_code == 404:
        return {"success": False, "error": "No product found with SKU " + sku}

    if response.status_code != 200:
        return {"success": False, "error": "The Product API returned an error."}

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


if __name__ == "__main__":
    mcp.run()
