import json

from src.export_service import ExportService


def test_generate_csv_empty():
    assert ExportService.generate_csv([]) == ""


def test_generate_csv_simple_rows():
    rows = [
        {"symbol": "ABC", "price": 100, "name": "Alpha"},
        {"symbol": "XYZ", "price": 200, "name": "Zeta"},
    ]
    csv_text = ExportService.generate_csv(rows)
    # Header must contain the keys from the first row in order
    assert csv_text.splitlines()[0].strip() == "symbol,price,name"
    assert "ABC" in csv_text and "Zeta" in csv_text


def test_export_endpoint_returns_csv():
    # Create a Flask test client from the app
    from app import app as flask_app

    client = flask_app.test_client()
    payload = {"rows": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}
    resp = client.post(
        "/export", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 200
    # Content-Type may include charset, so startswith check is safer
    assert resp.headers.get("Content-Type", "").startswith("text/csv")
    body = resp.get_data(as_text=True)
    assert "a,b" in body
    assert "1" in body and "4" in body
