"""Tests of the public endpoint POST /api/query used by the client page."""

from app.products import mcp_client


def test_a_question_gets_an_answer(app, monkeypatch, catalog):
    monkeypatch.setattr(mcp_client, "list_products", lambda **kwargs: catalog)

    response = app.test_client().post(
        "/api/query", json={"question": "Which branch has stock of HB-LAP-1001?"}
    )

    assert response.status_code == 200
    assert "Branch Thonon: 10 units" in response.get_json()["answer"]


def test_an_empty_question_is_refused(app):
    response = app.test_client().post("/api/query", json={"question": "  "})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please write a question."


def test_a_too_long_question_is_refused(app):
    response = app.test_client().post("/api/query", json={"question": "a" * 501})

    assert response.status_code == 400


def test_we_say_it_when_the_catalog_is_down(app, monkeypatch):
    monkeypatch.setattr(mcp_client, "list_products", lambda **kwargs: None)

    response = app.test_client().post("/api/query", json={"question": "HB-LAP-1001"})

    assert response.status_code == 503
    assert "not available" in response.get_json()["error"]


def test_the_page_is_allowed_to_call_us(app):
    """The client page is served from another port, so CORS must be open."""
    response = app.test_client().post("/api/query", json={"question": "hello"})

    assert response.headers["Access-Control-Allow-Origin"] == "*"
