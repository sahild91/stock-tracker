import logging
import yfinance as yf
import pandas as pd
import json
import streamlit as st
import altair as alt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InvalidInputError(Exception):
    pass

def get_stock_data_yahoo(ticker, market):
    try:
        yahoo_ticker = f"{ticker}.{market}"
        stock_data = yf.download(yahoo_ticker, period="max")
        if stock_data.empty:
            raise InvalidInputError(f"No data found for ticker: {ticker}")
        return stock_data
    except Exception as e:
        logger.error(f"Error occurred while fetching stock data from Yahoo Finance: {str(e)}")
        raise

def save_data_to_json(data, ticker):
    try:
        json_data = data.to_json(orient='records')
        with open(f"{ticker}_data.json", 'w') as file:
            file.write(json_data)
        logger.info(f"Stock data saved successfully for ticker: {ticker}")
    except Exception as e:
        logger.error(f"Error occurred while saving data to JSON: {str(e)}")
        raise

def filter_data_by_duration(data, duration):
    if duration == "YTD":
        start_date = pd.to_datetime(data.index[0]).strftime("%Y-01-01")
        filtered_data = data[start_date:]
    elif duration == "Max":
        filtered_data = data
    else:
        filtered_data = data.tail({"1D": 1, "5D": 5, "1W": 7, "1M": 30, "1Y": 365, "3Y": 365*3}[duration])
    return filtered_data

def create_chart(data):
    min_value = data["Close"].min()
    max_value = data["Close"].max()
    y_min = min_value - (max_value - min_value) * 0.1
    y_max = max_value + (max_value - min_value) * 0.1

    chart = alt.Chart(data.reset_index()).mark_line().encode(
        x=alt.X('Date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('Close:Q', scale=alt.Scale(domain=[y_min, y_max]), axis=alt.Axis(title='Closing Price'))
    )

    return chart

def main():
    st.title("Stock Data Collector")

    ticker = st.text_input("Enter the Ticker symbol of the Company you want details for:")
    market = st.selectbox("Select the market:", ["NS", "BO"])

    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None

    if st.button("Fetch Data"):
        try:
            st.session_state.stock_data = get_stock_data_yahoo(ticker, market)
            save_data_to_json(st.session_state.stock_data, ticker)
        except InvalidInputError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

    if st.session_state.stock_data is not None:
        durations = ["5D", "1D", "1W", "1M", "YTD", "1Y", "3Y", "Max"]
        default_duration = "5D"

        if 'selected_duration' not in st.session_state:
            st.session_state.selected_duration = default_duration

        selected_duration = st.selectbox("Select the duration:", durations, index=durations.index(st.session_state.selected_duration), key='duration_selectbox')

        if selected_duration != st.session_state.selected_duration:
            st.session_state.selected_duration = selected_duration

        filtered_data = filter_data_by_duration(st.session_state.stock_data, st.session_state.selected_duration)
        chart = create_chart(filtered_data)
        st.altair_chart(chart, use_container_width=True)

if __name__ == '__main__':
    main()