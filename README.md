# stock_fundamental

Stock Analysis Automation Project

Overview
This project is designed to automate the analysis of Indian stock market data from various indexes including Nifty 200, Nifty 500, Nifty 50, Nifty Large Midcap 250, Nifty Midcap 100, and Nifty Smallcap 250. The script fetches financial data using Yahoo Finance, calculates industry averages, and scores each stock based on predefined weights, ultimately providing a sorted list of top-performing stocks.

Features
Automated Data Fetching: Retrieves financial data for each stock ticker from Yahoo Finance.
Industry Averages Calculation: Computes average P/E ratio, P/B ratio, and EPS for each sector.
Stock Scoring: Scores each stock based on P/E ratio, P/B ratio, and EPS.
Top Stocks Selection: Identifies and lists the top 10 stocks within each sector.
Customizable Analysis: Allows selection of specific datasets or analysis of all available datasets.
Detailed Output: Generates both text and CSV files with detailed analysis and scores.
Requirements
Python 3.x
Pandas
yfinance
OS module (standard library)
Installation
Clone the Repository:

sh
Copy code
git clone https://github.com/your-repo/stock_fundamental.git
cd stock_fundamental
Install Dependencies:

sh
Copy code
pip install pandas yfinance
Usage
Place Input Files:
Ensure all input CSV files are placed in the input directory. The supported files are:

Indian_stocks_nifty_200.csv
Indian_stocks_nifty_500.csv
Indian_stocks_nifty_50.csv
Indian_stocks_nifty_large_midcap_250.csv
Indian_stocks_nifty_midcap_100.csv
Indian_stocks_nifty_smallcap_250.csv
Run the Script:
Execute the script to start the analysis:

sh
Copy code
python analyze_stocks.py
Select Dataset:
When prompted, select the dataset you want to analyze:

markdown
Copy code
Select the dataset:
1. Indian_stocks_nifty_200.csv
2. Indian_stocks_nifty_500.csv
3. Indian_stocks_nifty_50.csv
4. Indian_stocks_nifty_large_midcap_250.csv
5. Indian_stocks_nifty_midcap_100.csv
6. Indian_stocks_nifty_smallcap_250.csv
7. All files
Enter 1, 2, 3, 4, 5, 6, or 7:
Output
The output files are saved in the output directory with the original input file name appended with _analyzed. For example, if analyzing Indian_stocks_nifty_200.csv, the output files will be:

Indian_stocks_nifty_200_analyzed.txt
Indian_stocks_nifty_200_analyzed.csv
File Structure
lua
Copy code
stock_fundamental/
│
├── input/
│   ├── Indian_stocks_nifty_200.csv
│   ├── Indian_stocks_nifty_500.csv
│   ├── Indian_stocks_nifty_50.csv
│   ├── Indian_stocks_nifty_large_midcap_250.csv
│   ├── Indian_stocks_nifty_midcap_100.csv
│   └── Indian_stocks_nifty_smallcap_250.csv
│
├── output/
│   ├── Indian_stocks_nifty_200_analyzed.txt
│   ├── Indian_stocks_nifty_200_analyzed.csv
│   └── ...
│
├── analyze_stocks.py
└── README.md
Example Analysis
Each output file provides a detailed analysis of the stocks including market price, EPS, book value, P/E ratio, P/B ratio, and a normalized rating. The top stocks are identified and listed with their respective scores and sector comparisons.

Contribution
Feel free to contribute to this project by submitting pull requests. For major changes, please open an issue first to discuss what you would like to change.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
For any questions or feedback, please contact:

Puneethraddy M R
Email: puneethr09@gmail.com
GitHub: https://github.com/puneethr09

Happy Analyzing! 📈