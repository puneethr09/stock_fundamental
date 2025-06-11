from flask import Flask, render_template, jsonify, Response, request
from src.basic_analysis import (
    get_financial_ratios,
    analyze_ratios,
    get_market_news,
    get_news_categories,
)
from src.utils import load_company_data
import subprocess, os, time

app = Flask(__name__)
REPO_PATH = os.path.expanduser("~/repo/stock_fundamental/")

_news_cache = {"data": None, "timestamp": 0}
NEWS_CACHE_TTL = 3600  # seconds (1 hour)

# Add this cache for financial ratios
_ratios_cache = {}
RATIOS_CACHE_TTL = 30 * 24 * 3600  # 1 month in seconds


def get_market_news_cached():
    now = time.time()
    if _news_cache["data"] is None or now - _news_cache["timestamp"] > NEWS_CACHE_TTL:
        _news_cache["data"] = get_market_news()
        _news_cache["timestamp"] = now
    return _news_cache["data"]


def get_financial_ratios_cached(ticker):
    now = time.time()
    entry = _ratios_cache.get(ticker)
    if entry and now - entry["timestamp"] < RATIOS_CACHE_TTL:
        return entry["data"]
    data = get_financial_ratios(ticker)
    _ratios_cache[ticker] = {"data": data, "timestamp": now}
    return data


@app.route("/")
@app.route("/home")  # Adding both routes for flexibility
def home():
    news_items = get_market_news_cached()
    return render_template("index.html", news=news_items)


@app.route("/analyze", methods=["POST", "GET"])
def analyze():
    start_time = time.time()
    print(f"[PROFILE] /analyze request received at {start_time:.3f}")

    t0 = time.time()
    news_items = get_market_news_cached()
    print(f"[PROFILE] get_market_news: {time.time() - t0:.2f}s")

    if request.method == "POST":
        ticker = request.form["ticker"].upper() + ".NS"
    else:
        ticker = request.args.get("ticker", "").upper() + ".NS"

    t1 = time.time()
    ratios_df = get_financial_ratios_cached(ticker)  # <-- Use the cached version
    print(f"[PROFILE] get_financial_ratios: {time.time() - t1:.2f}s")

    t2 = time.time()
    if ratios_df is not None and not ratios_df.empty:
        warnings, explanations, plot_html = analyze_ratios(ratios_df)
        print(f"[PROFILE] analyze_ratios: {time.time() - t2:.2f}s")
        company_name = ratios_df["Company"].iloc[0]
        display_df = ratios_df.drop(columns=["Company"])
        response = render_template(
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
        response = render_template(
            "results.html",
            error="No data available for the provided ticker.",
            plot_html=None,
            zip=zip,
        )

    end_time = time.time()
    print(f"[PROFILE] /analyze response sent at {end_time:.3f} (elapsed: {end_time - start_time:.3f} seconds)")
    return response


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
    news_items = get_market_news_cached()
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
