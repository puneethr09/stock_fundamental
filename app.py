from flask import Flask, render_template, request
from utils import load_company_data
from src.basic_analysis import get_financial_ratios, analyze_ratios

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST", "GET"])
def analyze():
    if request.method == "POST":
        ticker = request.form["ticker"].upper() + ".NS"
    else:
        ticker = request.args.get("ticker", "").upper() + ".NS"

    ratios_df = get_financial_ratios(ticker)
    if ratios_df is not None and not ratios_df.empty:
        warnings, explanations, plot_html = analyze_ratios(ratios_df)
        company_name = ratios_df["Company"].iloc[0]
        
        # Remove Company column before displaying
        display_df = ratios_df.drop(columns=['Company'])
        
        return render_template(
            "results.html",
            tables=[display_df.to_html(classes="data table-hover", index=False)],
            titles=display_df.columns.values,
            plot_html=plot_html,
            warnings=warnings,
            explanations=explanations,
            company_name=company_name
        )    
    else:
        return render_template(
            "results.html",
            error="No data available for the provided ticker.",
            plot_html=None,
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
