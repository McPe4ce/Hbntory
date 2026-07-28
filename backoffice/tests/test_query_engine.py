"""Tests of the answers given to the public client page.

Nobody has HB-KEY-2003 in stock, so it is the product we use to check that
we say "no stock" instead of inventing one.
"""

from app.products import mcp_client
from app.public import query_engine


def test_where_a_product_is_in_stock(app, catalog):
    answer = query_engine.answer("Which branch has stock of HB-LAP-1001?", catalog)

    assert "Branch Thonon: 10 units" in answer
    assert "Branch Geneve: 2 units" in answer


def test_a_product_nobody_has(app, catalog):
    answer = query_engine.answer("Which branch has stock of HB-KEY-2003?", catalog)

    assert answer == "No branch has Mechanical Keyboard in stock."


def test_products_of_one_branch(app, catalog):
    answer = query_engine.answer("What products can I find in Branch Thonon?", catalog)

    assert "Business Laptop 14: 10 units" in answer
    assert "Monitor 27 4K: 4 units" in answer
    # Thonon has no desk lamp
    assert "Desk Lamp LED" not in answer


def test_quantity_in_one_branch(app, catalog):
    answer = query_engine.answer(
        "How many units of HB-LGT-1801 are there in Branch Geneve?", catalog
    )

    assert answer == "Branch Geneve has 30 units of Desk Lamp LED."


def test_a_product_can_be_found_by_its_name(app, catalog):
    answer = query_engine.answer("Do you have the Desk Lamp LED?", catalog)

    assert "Desk Lamp LED is in stock in:" in answer


def test_details_of_a_product(app, catalog, monkeypatch):
    def fake_details(sku):
        return {
            "sku": "HB-LAP-1001",
            "name": "Business Laptop 14",
            "description": "A 14 inch laptop for office work.",
            "category": "Computers",
            "brand": "Hbnt",
            "unit_price": 899.0,
            "currency": "EUR",
            "discontinued": False,
        }

    monkeypatch.setattr(mcp_client, "get_product_details", fake_details)

    answer = query_engine.answer("Give me details about HB-LAP-1001", catalog)

    assert "A 14 inch laptop for office work." in answer
    assert "Price: 899.0 EUR" in answer
    # The details always end with where the product is in stock
    assert "Branch Thonon: 10 units" in answer


def test_shopping_list_served_by_one_branch(app, catalog):
    answer = query_engine.answer(
        "I want to buy 2 units of HB-LAP-1001 and 3 units of HB-MON-2101", catalog
    )

    assert answer == "You can buy your whole list in Branch Thonon."


def test_shopping_list_split_between_branches(app, catalog):
    answer = query_engine.answer(
        "I want to buy 5 units of HB-LAP-1001 and 5 units of HB-LGT-1801", catalog
    )

    assert "No branch has your whole list" in answer
    assert "5 Business Laptop 14 in Branch Thonon" in answer
    assert "5 Desk Lamp LED in Branch Geneve" in answer


def test_shopping_list_says_what_nobody_has(app, catalog):
    answer = query_engine.answer(
        "I want to buy 2 units of HB-LAP-1001 and 1 unit of HB-KEY-2003", catalog
    )

    assert "Mechanical Keyboard: no branch has enough of it" in answer


def test_unknown_product_id(app, catalog):
    answer = query_engine.answer("Which branch has stock of HB-XXX-9999?", catalog)

    assert answer == "I do not know any product with the id HB-XXX-9999."


def test_question_we_do_not_understand(app, catalog):
    answer = query_engine.answer("What is the weather like today?", catalog)

    assert answer.startswith("Sorry, I did not understand the question.")
