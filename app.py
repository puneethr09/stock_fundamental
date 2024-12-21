from flask import Flask, render_template, jsonify, Response, request
from src.basic_analysis import (
    get_financial_ratios,
    analyze_ratios,
    get_market_news,
    get_news_categories,
)
from utils import load_company_data
import subprocess, os

app = Flask(__name__)
REPO_PATH = "/home/puneeth/repo/stock_fundamental/"


@app.route("/")
@app.route("/home")  # Adding both routes for flexibility
def home():
    news_items = get_market_news()
    return render_template("index.html", news=news_items)


@app.route("/analyze", methods=["POST", "GET"])
def analyze():
    news_items = get_market_news()
    if request.method == "POST":
        ticker = request.form["ticker"].upper() + ".NS"
    else:
        ticker = request.args.get("ticker", "").upper() + ".NS"

    ratios_df = get_financial_ratios(ticker)
    if ratios_df is not None and not ratios_df.empty:
        warnings, explanations, plot_html = analyze_ratios(ratios_df)
        company_name = ratios_df["Company"].iloc[0]
        display_df = ratios_df.drop(columns=["Company"])
        return render_template(
            "results.html",
            tables=[display_df.to_html(classes="data table-hover", index=False)],
            titles=display_df.columns.values,
            plot_html=plot_html,
            warnings=warnings,
            explanations=explanations,
            company_name=company_name,
            news=news_items,
            zip=zip,
        )
    else:
        return render_template(
            "results.html",
            error="No data available for the provided ticker.",
            plot_html=None,
            zip=zip,
        )


@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query", "").strip()
    company_data = load_company_data()
    suggestions = company_data[
        company_data["Company Name"].str.contains(query, case=False, na=False)
    ]
    result = {
        row["Company Name"]: row["Ticker"] for index, row in suggestions.iterrows()
    }
    return {"suggestions": result}


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_PATH,  # Set working directory to repo path
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)


@app.route("/trigger-ota")
def trigger_ota():

    # First verify repo path exists
    if not os.path.exists(REPO_PATH):
        return jsonify(
            {"success": False, "error": f"Repository path {REPO_PATH} does not exist"}
        )

    commands = [
        "git pull",
        "docker compose down",
        "docker compose build",
        "docker compose up -d",
    ]

    results = []
    for cmd in commands:
        success, output = run_command(cmd)
        results.append({"command": cmd, "success": success, "output": output})

    all_successful = all(result["success"] for result in results)

    return jsonify({"success": all_successful, "results": results})


@app.route("/news")
def news():
    news_items = get_market_news()
    organized_news = {}

    for item in news_items:
        publisher = item["publisher"]

        if publisher not in organized_news:
            organized_news[publisher] = {}

        # Add the news item to each of its categories
        for category in item["categories"]:
            if category not in organized_news[publisher]:
                organized_news[publisher][category] = []
            organized_news[publisher][category].append(item)

    # Sort each category by score
    for publisher in organized_news:
        for category in organized_news[publisher]:
            organized_news[publisher][category].sort(
                key=lambda x: x["score"], reverse=True
            )

    return render_template(
        "news.html",
        organized_news=organized_news,
        publishers=list(organized_news.keys()),
        categories=list(get_news_categories().keys()),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
