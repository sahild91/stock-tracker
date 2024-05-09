# Stock Trader

Stock Insights: Interactive Dashboard and Trend Analysis
This Python script, stock_data_collector.py, is a Streamlit application that fetches stock data from Yahoo Finance, displays it as an interactive line chart, and provides analytics based on the selected duration.

## Features

- Fetches stock data from Yahoo Finance for a given ticker symbol and market.
- Saves the fetched stock data to a JSON file for future reference.
- Displays an interactive line chart of the stock's closing price using Altair.
- Provides analytics based on the selected duration, including:
  - Opening and closing prices at the start and end of the period.
  - Total volume traded over the period.
  - Percentage change in price over the period.
- Allows the user to select the duration for which they want to view the data and analytics.
- Handles errors and logs them to a file for debugging purposes.

## Prerequistes

Before running the script, make sure you have the following dependencies installed:

- Python 3.x
- yfinance
- pandas
- streamlit
- altair

You can install the required libraries using pip:

```bash
pip install yfinance pandas streamlit altair
```

## Usage

- Clone the repository or download the stock_data_collector.py file.
- Open a terminal and navigate to the directory containing the script.
- Run the following command to start the Streamlit application:

```bash
streamlit run stock_data_collector.py
```

- The application will open in your default web browser.
- Enter the ticker symbol of the company you want to fetch data for in the text input field.
- Select the market from the dropdown menu (options: "NS" for NSE, "BO" for BSE).
- Click the "Fetch Data" button to retrieve the stock data from Yahoo Finance.
- Once the data is fetched, you can select the duration for which you want to view the data and analytics from the dropdown menu.
- The line chart and analytics will update automatically based on the selected duration.
- The fetched stock data will be saved as a JSON file in the same directory as the script, with the filename format {ticker}\_data.json.

## Error Handling and Logging

The script includes error handling and logging capabilities to capture and log any errors that occur during execution. The errors are logged to a file named stock_data_collector.log in the same directory as the script.
If an error occurs while fetching stock data or saving data to JSON, the error message will be logged to the file and displayed on the Streamlit app using st.error().

## Customization

You can customize the script by modifying the following constants:

- DURATIONS_DAYS: A dictionary that maps duration labels to the corresponding number of days. You can add or remove durations as needed.
- MARKET_OPTIONS: A list of market codes available for selection. You can add or remove market codes based on your requirements.
- LOG_FILE: The name of the file where the logs will be written. You can change the filename or path if desired.

## License

This project is open-source and available under the MIT License.

## Acknowledgements

This script utilizes the following libraries:

- [yfinance](https://pypi.org/project/yfinance/) - Yahoo Finance market data downloader
- [pandas](https://pandas.pydata.org/) - Data manipulation and analysis library
- [Streamlit](https://streamlit.io/) - Framework for building interactive web apps
- [Altair](https://altair-viz.github.io/) - Declarative statistical visualization library

## Contact

If you have any questions, suggestions, or issues, please feel free to contact the author or open an issue on the GitHub repository.
