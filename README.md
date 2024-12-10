# Stock Fundamental Analysis

This repository provides a comprehensive toolkit for analyzing the financial health of companies using their historical financial data. It includes functions to load, process, and analyze financial ratios, as well as generate visualizations to aid in understanding a company's financial performance.

## Features

- **Data Loading**: Load and concatenate company data from CSV files.
- **Financial Ratio Analysis**: Calculate and analyze key financial ratios such as Return on Equity (ROE), Current Ratio, and Debt to Equity.
- **Data Normalization**: Normalize financial data for comparative analysis.
- **Visualization**: Generate plots to visualize financial ratios over time.
- **Data Retrieval**: Fetch historical financial data using Yahoo Finance.

## Prerequisites

- Python 3.x
- Required Python packages: `pandas`, `matplotlib`, `yfinance`, `numpy`, `os`

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/stock-fundamental-analysis.git
   cd stock-fundamental-analysis

   ```

2. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare the Input Data:**

   Ensure that your CSV files containing company data are placed in the input directory. These files should contain the necessary financial data for analysis.

4. **Run the Web Application:**

   Start the web server by running the following command:
   ```bash
   python app.py
   ```
   Open your web browser and navigate to http://localhost:5000 to access the web interface.

5. **Run the Analysis: *Independent Manuel analysis***

   You can start analyzing financial data by executing the main script or using the functions provided in the codebase. For example, to analyze a specific company's financial ratios, you can use the following script:
   
   ```python
   from src.basic_analysis import get_financial_ratios, analyze_ratios

   ticker = "VBL"  # Example stock ticker
   ratios_df = get_financial_ratios(ticker)
   warnings, explanations = analyze_ratios(ratios_df)

   for warning in warnings:
      print(warning)

   for explanation in explanations:
      print(explanation)
   ```

6. **View the Results:**

   The analysis will output warnings and explanations based on the financial ratios calculated. Additionally, visualizations will be saved in the static directory for further inspection.

## Contributing
   Contributions are welcome! Please feel free to submit a Pull Request.

## License
   This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
   For any questions or issues, please open an issue in the repository or contact the maintainer at [puneethr09@gmail.com].

## Acknowledgments
This `README.md` provides a step-by-step guide to setting up and running the project, ensuring that users can directly apply the instructions and have the project work as expected. Adjust any placeholders, such as the GitHub repository URL and contact email, to fit your specific project details.