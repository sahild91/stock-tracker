import logging
import yfinance as yf
import pandas as pd
import json
import streamlit as st
import altair as alt

# Constants
DURATIONS_DAYS = {"1D": 1, "5D": 5, "1W": 7, "1M": 30, "YTD": 365, "1Y": 365, "3Y": 1095, "Max": float('inf')}
DURATIONS_DAYS_DETAILS = {"1D": "1 Day", "5D": "5 Days", "1W": "1 Week", "1M": "1 Month", "YTD": "Year to Date", "1Y": "1 Year", "3Y": "3 Year", "Max": "Max Duration"}
MARKET_SUFFIXES = {
    "NSE": ".NS",
    "BSE": ".BO",
    "NYSE": "",
    "NASDAQ": "",
    # Add more market codes and their corresponding suffixes
}
LOG_FILE = 'stock_data_collector.log'

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InvalidInputError(Exception):
    """Exception raised for errors in the input."""
    pass

def get_stock_data(ticker, market):
    """
    Fetches stock data from Yahoo Finance for a given ticker and market.
    
    Args:
    ticker (str): Stock ticker symbol.
    market (str): Market code.
    
    Returns:
    DataFrame: Stock data as a pandas DataFrame.
    
    Raises:
    InvalidInputError: If no data is found for the ticker.
    """
    try:
        if market not in MARKET_SUFFIXES:
            raise InvalidInputError(f"Invalid market selected: {market}")
        
        yahoo_ticker = f"{ticker}{MARKET_SUFFIXES[market]}"
        stock_data = yf.download(yahoo_ticker, period="max")
        
        if stock_data.empty:
            raise InvalidInputError(f"No data found for ticker: {ticker} in market: {market}")
        
        return stock_data
    except Exception as e:
        logger.error(f"Error occurred while fetching stock data from Yahoo Finance: {str(e)}")
        raise

def save_data_to_json(data, ticker):
    """
    Saves stock data to a JSON file for a given ticker.
    
    Args:
    data (DataFrame): Stock data.
    ticker (str): Stock ticker symbol.
    """
    try:
        json_data = data.to_json(orient='records')
        with open(f"{ticker}_data.json", 'w') as file:
            file.write(json_data)
        logger.info(f"Stock data saved successfully for ticker: {ticker}")
    except Exception as e:
        logger.error(f"Error occurred while saving data to JSON: {str(e)}")
        raise

def filter_data_by_duration(data, duration):
    """
    Filters data by the specified duration.
    
    Args:
    data (DataFrame): Stock data.
    duration (str): Duration for which data is required.
    
    Returns:
    DataFrame: Filtered data.
    """
    if duration == "YTD":
        start_date = pd.to_datetime(data.index[0]).strftime("%Y-01-01")
        filtered_data = data[start_date:]
    elif duration == "Max":
        filtered_data = data
    else:
        filtered_data = data.tail(DURATIONS_DAYS[duration])
    return filtered_data

def create_chart(data):
    """
    Creates a line chart for the stock data using Altair.
    
    Args:
    data (DataFrame): Stock data.
    
    Returns:
    Chart: Altair chart object.
    """
    min_value = data["Close"].min()
    max_value = data["Close"].max()
    y_min = min_value - (max_value - min_value) * 0.1
    y_max = max_value + (max_value - min_value) * 0.1

    chart = alt.Chart(data.reset_index()).mark_line().encode(
        x=alt.X('Date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('Close:Q', scale=alt.Scale(domain=[y_min, y_max]), axis=alt.Axis(title='Closing Price')),
        tooltip=['Date:T', 'Close:Q']
    ).properties(
        width='container',
        height=400
    ).configure_view(
        strokeWidth=0
    )

    return chart

def display_analytics(filtered_data, duration):
    """
    Displays stock data analytics on the Streamlit app, based on the selected duration.
    
    Args:
    filtered_data (DataFrame): Filtered stock data for the selected duration.
    duration (str): Selected duration for analytics.
    """
    if filtered_data.empty:
        st.write("No data available for the selected duration.")
        return

    # Retrieve the first and last entry in the filtered data to calculate changes
    first_data = filtered_data.iloc[0]
    last_data = filtered_data.iloc[-1]
    
    first_close = first_data["Close"]
    last_close = last_data["Close"]
    first_open = first_data["Open"]
    last_open = last_data["Open"]
    volume_traded = filtered_data["Volume"].sum()  # Total volume traded over the period
    percent_change = ((last_close - first_close) / first_close) * 100 if first_close != 0 else 0

    # Create a DataFrame for the analytics data
    analytics_data = pd.DataFrame({
        "Metric": ["Opening Price at start of period", "Closing Price at start of period",
                   "Opening Price at end of period", "Closing Price at end of period",
                   "Total Volume Traded", "Percentage Change over period"],
        "Value": [f"{first_open:.2f}", f"{first_close:.2f}", f"{last_open:.2f}", f"{last_close:.2f}",
                  f"{volume_traded:,}", f"{percent_change:.2f}%"]
    })

    # Display the analytics table with alternating background colors
    #st.table(analytics_data.style.apply(lambda x: ['background-color: lightgray' if i % 2 == 0 else '' for i in range(len(x))], axis=1), index=False)
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 40px;">
            {analytics_data.style
                .hide(axis="index")
                .set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center')]},
                    {'selector': 'td', 'props': [('text-align', 'center')]}
                ])
                .to_html()}
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    """
    Main function to run the Streamlit app.
    """
    # Set page config and theme
    st.set_page_config(page_title="Stock Data Collector", layout="wide")
    st.markdown(
        """
        <style>
        .streamlit-button {
            margin-right: 10px;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            font-size: 1rem;
            font-weight: 400;
            line-height: 1.5;
            text-align: center;
            white-space: nowrap;
            vertical-align: middle;
            cursor: pointer;
            user-select: none;
            background-color: #f0f0f0;
            border-color: #f0f0f0;
            color: #000;
        }
        .streamlit-button:hover {
            background-color: #e0e0e0;
            border-color: #e0e0e0;
            color: #000;
        }
        .streamlit-button:focus {
            outline: 0;
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        }
        .streamlit-table {
            align: center;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='text-align: center;'>Stock Data Collector</h1>", unsafe_allow_html=True)

    ticker = st.text_input("Enter the Ticker symbol of the Company you want details for:")
    market = st.selectbox("Select the market:", list(MARKET_SUFFIXES.keys()))

    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None

    if st.button("Fetch Data"):
        try:
            st.session_state.stock_data = get_stock_data(ticker, market)
            save_data_to_json(st.session_state.stock_data, ticker)
        except InvalidInputError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

    if st.session_state.stock_data is not None:
        durations = list(DURATIONS_DAYS.keys())
        default_duration = "5D"

        if 'selected_duration' not in st.session_state:
            st.session_state.selected_duration = default_duration

        # Create duration buttons in a single row
        num_columns = len(durations)
        columns = st.columns(num_columns)
        for i, duration in enumerate(durations):
            with columns[i]:
                if st.button(duration, key=f"duration_button_{duration}"):
                    st.session_state.selected_duration = duration

        filtered_data = filter_data_by_duration(st.session_state.stock_data, st.session_state.selected_duration)

        if not filtered_data.empty:
            with st.expander("Analytics"):
                #st.subheader(f"Analytics for {st.session_state.selected_duration}")
                heading = f"Analytics for {DURATIONS_DAYS_DETAILS.get(st.session_state.selected_duration)}"
                st.markdown(f"<h3 style='text-align: center;'>{heading}</h3>", unsafe_allow_html=True)
                display_analytics(filtered_data, st.session_state.selected_duration)

            with st.expander("Chart", expanded=True):
                chart = create_chart(filtered_data)
                st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("No data available for the selected duration.")

if __name__ == '__main__':
    main()