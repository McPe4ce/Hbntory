"""Answers the questions asked on the public page.

We do not have the AI service yet, so we look at the words of the question to
guess what the user wants. Then we build the answer with the stock from our
database and the products from the MCP server. We never invent an answer: if
we do not understand the question we say it.
"""

import re

from app.models import Branch, Stock
from app.products import mcp_client

HELP = (
    "Sorry, I did not understand the question. You can ask for example:\n"
    "  - Give me details about HB-LAP-1001\n"
    "  - Which branch has stock of HB-LAP-1001?\n"
    "  - What products can I find in Branch Thonon?\n"
    "  - I want to buy 3 units of HB-LAP-1001 and 2 units of HB-KEY-2003"
)

DETAIL_WORDS = ["detail", "description", "describe", "price", "about"]


def find_product(text, catalog):
    """Find the product the text talks about (by id or by name), or None."""
    text = text.lower()

    for product in catalog:
        if product["sku"].lower() in text:
            return product

    # No id in the text, so we look for the product name that has the most
    # words in common with the text ("barcode scanner" -> Barcode Scanner USB).
    best = None
    best_count = 0
    for product in catalog:
        count = 0
        for word in product["name"].lower().split():
            if word in text.split():
                count += 1
        if count > best_count:
            best = product
            best_count = count

    if best_count >= 2:
        return best
    return None


def find_branch(text):
    """Find the branch the text talks about, or None."""
    text = text.lower()

    for branch in Branch.query.all():
        name = branch.branch_name.lower()
        # We accept the full name ("Branch Thonon") or only the city ("Thonon")
        if name in text or name.split()[-1] in text:
            return branch

    return None


def quantity_in_branch(branch, sku):
    """How many units of this product this branch has."""
    stock = Stock.query.filter_by(branch_id=branch.id, product_id=sku).first()

    if stock is None:
        return 0
    return stock.quantity


def branches_with_product(sku):
    """List of (branch, quantity) for the branches that have this product."""
    result = []

    for branch in Branch.query.all():
        quantity = quantity_in_branch(branch, sku)
        if quantity > 0:
            result.append((branch, quantity))

    return result


def is_detail_question(question):
    """True if the user wants the full description of a product."""
    question = question.lower()

    for word in DETAIL_WORDS:
        if word in question:
            return True

    return False


def unknown_id(question, catalog):
    """Return an id written in the question that we do not know, or None."""
    for word in question.split():
        word = word.strip("?.,!")
        if word.count("-") >= 2 and find_product(word, catalog) is None:
            return word

    return None


def read_shopping_list(question, catalog):
    """Read "3 units of X and 2 units of Y" as a list of (quantity, product)."""
    items = []

    for quantity, name in re.findall(r"(\d+)\s*(?:units?)?\s*of\s+([\w-]+)", question, re.I):
        product = find_product(name, catalog)
        if product is not None:
            items.append((int(quantity), product))

    return items


def answer_details(product):
    """Give all the information we have about one product."""
    details = mcp_client.get_product_details(product["sku"])

    if details is None:
        return "Sorry, I cannot get the details of this product right now."

    answer = details["name"] + " (" + details["sku"] + ")\n\n"
    answer += details["description"] + "\n\n"
    answer += "Category: " + details["category"] + "\n"
    answer += "Brand: " + details["brand"] + "\n"
    answer += "Price: " + str(details["unit_price"]) + " " + details["currency"] + "\n"

    if details["discontinued"]:
        answer += "This product is discontinued.\n"

    return answer + "\n" + answer_where(details)


def answer_where(product):
    """Say in which branches the product is in stock."""
    branches = branches_with_product(product["sku"])

    if not branches:
        return "No branch has " + product["name"] + " in stock."

    lines = [product["name"] + " is in stock in:"]
    for branch, quantity in branches:
        lines.append("  - " + branch.branch_name + ": " + str(quantity) + " units")

    return "\n".join(lines)


def answer_branch_products(branch, catalog):
    """Say what one branch has in stock."""
    lines = [branch.branch_name + " has in stock:"]

    for stock in branch.stocks:
        if stock.quantity == 0:
            continue
        product = find_product(stock.product_id, catalog)
        name = product["name"] if product else stock.product_id
        lines.append("  - " + name + ": " + str(stock.quantity) + " units")

    if len(lines) == 1:
        return branch.branch_name + " has no product in stock."

    return "\n".join(lines)


def answer_shopping_list(items):
    """Say which branch (or branches) the user should visit."""
    # First we look for a branch that has everything on the list.
    for branch in Branch.query.all():
        has_everything = True
        for quantity, product in items:
            if quantity_in_branch(branch, product["sku"]) < quantity:
                has_everything = False

        if has_everything:
            return "You can buy your whole list in " + branch.branch_name + "."

    # No branch has everything, so we say what each branch can give.
    lines = ["No branch has your whole list. You can buy:"]
    found = []

    for branch in Branch.query.all():
        for quantity, product in items:
            if quantity_in_branch(branch, product["sku"]) >= quantity:
                lines.append("  - " + str(quantity) + " " + product["name"]
                             + " in " + branch.branch_name)
                found.append(product["sku"])

    for quantity, product in items:
        if product["sku"] not in found:
            lines.append("  - " + product["name"] + ": no branch has enough of it")

    return "\n".join(lines)


def answer(question, catalog):
    """Read the question and return the text to show on the page."""
    items = read_shopping_list(question, catalog)
    if len(items) > 1:
        return answer_shopping_list(items)

    branch = find_branch(question)
    product = find_product(question, catalog)

    if product is None:
        if branch is not None:
            return answer_branch_products(branch, catalog)

        wrong_id = unknown_id(question, catalog)
        if wrong_id is not None:
            return "I do not know any product with the id " + wrong_id + "."

        return HELP

    if is_detail_question(question):
        return answer_details(product)

    if branch is not None:
        quantity = quantity_in_branch(branch, product["sku"])
        return (branch.branch_name + " has " + str(quantity) + " units of "
                + product["name"] + ".")

    return answer_where(product)
