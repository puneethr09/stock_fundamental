from flask import Flask
import os

# Use absolute path for templates so the smoke test finds them reliably
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(ROOT, "templates")
app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config["SERVER_NAME"] = "localhost"
# Provide some Python builtins to the Jinja environment to match app runtime
app.jinja_env.globals["zip"] = zip


# Minimal routes used by templates
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


def render_all():
    templates = [
        "index.html",
        "results.html",
        "tool_challenge.html",
        "news.html",
        "achievements.html",
    ]

    contexts = {
        "results.html": {
            "company_name": "ACME Corp",
            "show_stage_progress": False,
            "stage_progress": {
                "progress_within_stage": 10,
                "next_stage_readiness": 5,
                "stage_name": "Novice",
                "confidence_score": 50,
            },
            "learning_stage": {
                "educational_content": {"focus": "Basics"},
                "ui_adaptations": {"show_tooltips": False},
            },
            "charts": [],
            "recommendations": [],
            "summary": "Test summary",
            "ticker": "ACME",
        },
        "news.html": {
            "publishers": ["Reuters"],
            "categories": ["Market", "Stocks"],
            "organized_news": {"Reuters": {"Market": [], "Stocks": []}},
        },
        "index.html": {},
        "tool_challenge.html": {},
        "achievements.html": {"badges": []},
    }

    with app.app_context():
        for t in templates:
            ctx = contexts.get(t, {})
            try:
                tpl = app.jinja_env.get_template(t)
                tpl.render(**ctx)
                print(f"[OK] Rendered {t}")
            except Exception as e:
                import traceback

                print(f"[ERROR] Rendering {t}:")
                traceback.print_exc()


if __name__ == "__main__":
    render_all()
