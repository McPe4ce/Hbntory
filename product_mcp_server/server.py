from fastmcp import FastMCP
import requests

mcp = FastMCP("product-mcp-server")

PRODUCT_API_BASE_URL = "http://localhost:5001"  # à ajuster plus tard pour Docker

@mcp.tool()
def list_products(query: str = None) -> dict:
    """
    Liste les produits disponibles dans le catalogue externe.
    Si 'query' est fourni, recherche les produits correspondant au mot-clé.
    """
    if query:
        url = f"{PRODUCT_API_BASE_URL}/api/v1/products/search"
        params = {"q": query}
    else:
        url = f"{PRODUCT_API_BASE_URL}/api/v1/products"
        params = {}

    response = requests.get(url, params=params)

    return response.json()

if __name__ == "__main__":
    mcp.run()