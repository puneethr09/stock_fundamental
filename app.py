from flask import Flask, render_template, request
import pandas as pd
import os
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

    try:
        ratios_df = get_financial_ratios(ticker)
        if ratios_df is not None and not ratios_df.empty:
            warnings, explanations, plot_filename = analyze_ratios(ratios_df)
            company_name = ratios_df["Company"].iloc[0]
            # Format DataFrame
            ratios_df = ratios_df.drop(columns=["Company"])
            # Round numbers to 2 decimal places
            ratios_df = ratios_df.round(2)
            
            return render_template(
                "results.html",
                tables=[ratios_df.to_html(classes="data table-hover", index=False)],
                titles=ratios_df.columns.values,
                plot_filename=plot_filename,
                warnings=warnings,
                explanations=explanations,
                company_name=company_name,
            )
        else:
            return render_template(
                "results.html",
                error="No data available for the provided ticker.",
                plot_filename=[],
            )
    except Exception as e:
        return render_template(
            "results.html", error=f"An error occurred: {e}", plot_filename=[]
        )

# Load company data from CSV files in the input directory
def load_company_data():
    input_dir = "input"
    company_data = pd.DataFrame()

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(input_dir, file))
            company_data = pd.concat([company_data, df], ignore_index=True)

    return company_data[["Company Name", "Ticker"]]


# Load the company data at the start
company_data = load_company_data()


@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query", "").strip()
    suggestions = company_data[
        company_data["Company Name"].str.contains(query, case=False, na=False)
    ]
    result = {
        row["Company Name"]: row["Ticker"] for index, row in suggestions.iterrows()
    }
    return {"suggestions": result}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
