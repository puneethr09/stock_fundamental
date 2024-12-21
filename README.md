# Stock Fundamental Analysis Web Application

This web application provides a platform for analyzing the fundamental financial data of Indian stocks. It fetches data from Yahoo Finance, calculates key financial ratios, and presents them in an interactive and user-friendly manner. The application also includes a news feed to keep users updated on the latest market developments.

## Features

- **Stock Analysis**:
  - Fetches financial data for Indian stocks from Yahoo Finance.
  - Calculates key financial ratios such as ROE, ROA, ROIC, Quick Ratio, Current Ratio, Debt to Equity, P/E Ratio, P/B Ratio, EBIT Margin, Asset Turnover, Operating Margin, Net Profit Margin, Working Capital Ratio, and Interest Coverage.
  - Presents the ratios in a tabular format with color-coded values (positive in green, negative in red).
  - Provides warnings and explanations for potentially concerning ratios.
  - Generates interactive plots using Plotly to visualize the trends of financial ratios over time.
  - Supports searching for stocks by ticker symbol or company name with suggestions.
- **Market News**:
  - Fetches the latest market news from multiple sources (Economic Times, Business Standard, Financial Express, LiveMint).
  - Displays news in a tabbed interface, categorized by source.
  - Prioritizes news based on keyword relevance and recency.
  - Filters out news older than two days.
  - Allows news items to belong to multiple categories.
  - Shows a "No news available" message for empty categories.
- **Over-the-Air (OTA) Updates**:
  - Provides a button to trigger OTA updates for the application.
  - Displays the update progress in a console modal.
- **User Interface**:
  - Clean and responsive design using Bootstrap.
  - Interactive elements for a better user experience.
  - Dynamic date and time display in the navigation bar.

## Technologies Used

- **Python**: Core logic and backend.
- **Flask**: Web framework.
- **yfinance**: Library to fetch financial data from Yahoo Finance.
- **pandas**: Data manipulation and analysis.
- **matplotlib**: Plotting library (used for static plots).
- **plotly**: Interactive plotting library.
- **requests**: HTTP library for fetching news feeds.
- **xml.etree.ElementTree**: XML parsing for news feeds.
- **Bootstrap**: CSS framework for styling.
- **jQuery**: JavaScript library for DOM manipulation.

## Setup and Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python app.py
   ```

   The application will be available at `http://0.0.0.0:5000`.

## Code Structure

- `app.py`: Main Flask application file.
- `src/`: Contains the core logic for fetching and analyzing financial data.
  - `basic_analysis.py`: Contains functions for fetching data, calculating ratios, analyzing ratios, and plotting.
- `templates/`: Contains HTML templates for the web pages.
  - `index.html`: Home page with stock search input.
  - `results.html`: Page to display analysis results.
  - `news.html`: Page to display market news.
- `static/`: Contains static files like CSS, JavaScript, and images.
- `utils.py`: Contains utility functions for calculations.
- `docker_compose_restart.py`: Script to restart docker compose.

## Usage

1. **Stock Analysis**:
   - Navigate to the home page (`/`).
   - Enter a stock ticker symbol or company name in the search input.
   - Click the "Analyze" button to view the financial ratios, warnings, and plots.
   - Use the search bar in the results page to analyze another stock.
2. **Market News**:
   - Navigate to the market news page (`/news`).
   - Browse the latest news from different sources using the tabs.
   - Explore news within categories using the sub-tabs.
3. **OTA Updates**:
   - Click the "Update System" button to trigger an OTA update.
   - Monitor the update progress in the console modal.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for any bugs or feature requests.

## License

This project is licensed under the MIT License.