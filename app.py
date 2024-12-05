from flask import Flask, render_template, request
import pandas as pd
from src.basic_analysis import get_financial_ratios, analyze_ratios
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form['ticker'].upper() + ".NS"  # Ensure ticker is formatted correctly
    try:
        ratios_df = get_financial_ratios(ticker)

        if ratios_df is not None and not ratios_df.empty:
            plot_filename = analyze_ratios(ratios_df)  # Call analyze_ratios to get the plot filename
            company_name = ratios_df["Company"].iloc[0]  # Get the company name from the DataFrame
            return render_template('results.html', tables=[ratios_df.to_html(classes='data')], titles=ratios_df.columns.values, plot=plot_filename, company_name=company_name)
        else:
            return render_template('results.html', error="No data available for the provided ticker.")
    except Exception as e:
        return render_template('results.html', error=f"An error occurred: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
