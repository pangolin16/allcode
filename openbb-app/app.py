import streamlit as st
from openbb import obb
import plotly.express as px
import os

# Set provider credentials
obb.user.credentials.fmp_api_key = os.getenv("FRED_API_KEY")



obb.user.credentials.set(
    {
        "alpha_vantage_api_key": "YOUR_KEY",
        "fred_api_key": "a7febb3893d76b71c576a2c774bf4fe5",
    }
)
st.set_page_config(page_title="OpenBB Dashboard", layout="wide")
st.title("📈 Financial Dashboard")

ticker = st.text_input("Enter ticker symbol", "AAPL")
provider = st.selectbox("Provider", ["yfinance", "fmp"])

if ticker:
    try:
        with st.spinner("Fetching data..."):
            df = obb.equity.price.historical(
                ticker,
                provider=provider
            ).to_dataframe()

        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(df, y="close", title=f"{ticker} Closing Price")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.bar(df, y="volume", title=f"{ticker} Volume")
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df.tail(20))

    except Exception as e:
        st.error(f"Error: {e}")