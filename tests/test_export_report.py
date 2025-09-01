import json
from io import BytesIO


def test_report_csv():
    from app import app as flask_app

    client = flask_app.test_client()
    payload = {"rows": [{"x": 1, "y": 2}], "format": "csv", "filename": "myreport"}
    resp = client.post(
        "/export/report", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 200
    assert resp.headers.get("Content-Type", "").startswith("text/csv")
    assert "x,y" in resp.get_data(as_text=True)


def test_report_xlsx():
    from app import app as flask_app

    client = flask_app.test_client()
    payload = {"rows": [{"a": 5, "b": 6}], "format": "xlsx", "filename": "sheet1"}
    resp = client.post(
        "/export/report", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 200
    ct = resp.headers.get("Content-Type", "")
    assert "spreadsheetml" in ct or "application/octet-stream" in ct
    data = resp.get_data()
    assert len(data) > 0


def test_report_pdf():
    from app import app as flask_app

    client = flask_app.test_client()
    payload = {
        "rows": [{"label": "A", "value": 10}],
        "format": "pdf",
        "filename": "pdfreport",
    }
    resp = client.post(
        "/export/report", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 200
    assert resp.headers.get("Content-Type", "").startswith("application/pdf")
    data = resp.get_data()
    # PDF files start with %PDF
    assert data[:4] == b"%PDF"
