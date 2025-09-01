import json


def test_export_analysis_csv(monkeypatch):
    from app import app as flask_app

    # Stub get_financial_ratios and analyze_ratios
    import pandas as pd

    df = pd.DataFrame([{"Company": "TestCo", "Metric": 1}])

    monkeypatch.setattr("src.basic_analysis.get_financial_ratios", lambda t: df)
    monkeypatch.setattr(
        "src.basic_analysis.analyze_ratios", lambda df, t: ([], [], None, [], [], 0.9)
    )

    client = flask_app.test_client()
    resp = client.get("/export/analysis/TCS?format=csv")
    assert resp.status_code == 200
    assert resp.headers.get("Content-Type", "").startswith("text/csv")


def test_export_progress_csv(monkeypatch):
    from app import app as flask_app

    # Stub persistence
    monkeypatch.setattr(
        "src.persistence.get_progress_metrics", lambda uid: {"score": 42}
    )
    monkeypatch.setattr(
        "src.persistence.get_badges_for_user",
        lambda uid: [
            {"badge_type": "starter", "earned_at": "2025-01-01", "payload": {}}
        ],
    )

    client = flask_app.test_client()
    resp = client.get("/export/progress/test-user?format=csv")
    assert resp.status_code == 200
    assert resp.headers.get("Content-Type", "").startswith("text/csv")
    assert "starter" in resp.get_data(as_text=True)


def test_export_portfolio_csv(monkeypatch):
    from app import app as flask_app

    client = flask_app.test_client()
    resp = client.get("/export/portfolio/test-user?format=csv")
    assert resp.status_code == 200
    assert resp.headers.get("Content-Type", "").startswith("text/csv")
    body = resp.get_data(as_text=True)
    assert "ticker" in body
