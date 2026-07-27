from fastmcp import FastMCP
import product_api_client

mcp = FastMCP("product-mcp-server")


@mcp.tool()
def list_products(include_discontinued: bool = False) -> dict:
    """List the products available in the external catalog.

    Discontinued products are hidden unless include_discontinued is true.
    Set it to true when resolving a product that a branch still holds in stock.
    """

    return product_api_client.list_products(include_discontinued)


@mcp.tool()
def get_product_details(sku: str) -> dict:
    """Get the details of one product, identified by its SKU (example: HB-LAP-1001)."""

    return product_api_client.get_product_details(sku)


if __name__ == "__main__":
    mcp.run()
