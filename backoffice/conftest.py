"""Shared setup for the tests.

The config reads DATABASE_URL when it is imported, so we set it here first:
the tests run on a database in memory and never touch hbntory.db.
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest

from app import create_app
from app.extensions import db
from app.models import Branch, Stock

# What the MCP server would return. The tests give it to the query engine
# directly, so they never need the network.
CATALOG = [
    {"sku": "HB-LAP-1001", "name": "Business Laptop 14"},
    {"sku": "HB-MON-2101", "name": "Monitor 27 4K"},
    {"sku": "HB-LGT-1801", "name": "Desk Lamp LED"},
    {"sku": "HB-KEY-2003", "name": "Mechanical Keyboard"},
]


@pytest.fixture
def app():
    """An application with two branches and some stock."""
    app = create_app()

    with app.app_context():
        db.create_all()

        thonon = Branch(branch_name="Branch Thonon")
        geneve = Branch(branch_name="Branch Geneve")
        db.session.add_all([thonon, geneve])
        db.session.commit()

        db.session.add_all([
            Stock(branch_id=thonon.id, product_id="HB-LAP-1001", quantity=10),
            Stock(branch_id=thonon.id, product_id="HB-MON-2101", quantity=4),
            Stock(branch_id=geneve.id, product_id="HB-LAP-1001", quantity=2),
            Stock(branch_id=geneve.id, product_id="HB-LGT-1801", quantity=30),
        ])
        db.session.commit()

        yield app

        db.drop_all()


@pytest.fixture
def catalog():
    return CATALOG
