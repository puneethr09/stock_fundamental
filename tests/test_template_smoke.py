import pytest
import os
from flask import Flask

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(ROOT, "templates")


@pytest.fixture
def app():
    app = Flask(__name__, template_folder=TEMPLATE_DIR)
    app.config["SERVER_NAME"] = "localhost"
    app.jinja_env.globals["zip"] = zip

    # Minimal routes referenced by templates
    @app.route("/")
    def home():
        return "home"

    @app.route("/pattern")
    def pattern_training_home():
        return "pattern"

    @app.route("/news")
    def news():
        return "news"

    @app.route("/analyze")
    def analyze():
        return "analyze"

    @app.route("/achievements")
    def achievements():
        return "achievements"

    return app


def test_templates_render(app):
    templates = [
        "index.html",
        "results.html",
        "tool_challenge.html",
        "news.html",
        "achievements.html",
        "research_assignment.html",
    ]

    with app.app_context():
        common_ctx = {
            "learning_stage": {
                "ui_adaptations": {"show_tooltips": False},
                "educational_content": {},
            },
            "stage_progress": {
                "progress_within_stage": 10,
                "next_stage_readiness": 5,
                "stage_name": "Novice",
                "confidence_score": 50,
            },
            "company_name": "ACME Corp",
            "warnings": [],
            "explanations": [],
            "tables": [],
            "plot_html": "",
            "gaps": [],
            "research_guides": [],
            "charts": [],
            "recommendations": [],
            "summary": "Test summary",
            "ticker": "ACME",
        }
        # Minimal assignment object for research_assignment.html
        common_ctx["assignment"] = {
            "title": "Sample Assignment",
            "company": "ACME Corp",
            "category": "MOAT_ANALYSIS",
            "difficulty": "Easy",
            "time_estimate_minutes": 30,
            "instructions": ["Step 1", "Step 2"],
            "success_criteria": ["Cite at least 2 sources"],
        }
        for t in templates:
            tpl = app.jinja_env.get_template(t)
            rendered = tpl.render(**common_ctx)
            assert rendered and rendered.strip().startswith(
                "<"
            ), f"Template {t} did not render"
