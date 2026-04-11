import re
import streamlit as st
from openbb import obb
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
import pandas as pd

# Set provider credentials via env vars (keep secrets out of source code)
obb.user.credentials.fred_api_key = os.getenv("FRED_API_KEY")
obb.user.credentials.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

# Helper function to format dates to fiscal quarters
def format_to_quarter(date_index):
    """Convert date index to fiscal quarter format (Q# YY)"""
    quarters = []
    for date in date_index:
        if pd.isna(date):
            quarters.append("N/A")
        else:
            date_obj = pd.to_datetime(date)
            quarter = (date_obj.month - 1) // 3 + 1
            year = date_obj.year % 100
            quarters.append(f"Q{quarter} {year:02d}")
    return quarters


def format_large_value(value):
    if pd.isna(value):
        return ""
    num = float(value)
    sign = "-" if num < 0 else ""
    num = abs(num)
    if num >= 1_000_000_000:
        return f"{sign}{num / 1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"{sign}{num / 1_000_000:.2f}M"
    if num >= 1_000:
        return f"{sign}{num / 1_000:.2f}K"
    return f"{sign}{num:,.0f}"


def format_percentage_label(value):
    if pd.isna(value):
        return ""
    return f"{value:.1f}%"


def format_period_label(date_index, frequency="quarter"):
    if frequency == "annual":
        labels = []
        for date in date_index:
            if pd.isna(date):
                labels.append("N/A")
            else:
                d = pd.to_datetime(date)
                labels.append(str(d.year))
        return labels
    return format_to_quarter(date_index)


def find_column(df, keywords):
    if df is None:
        return None
    for col in df.columns:
        lower = col.lower()
        if all(keyword in lower for keyword in keywords):
            return col
    return None


def get_period_labels(df, frequency="quarter"):
    """Find the best date/period index for chart labels."""
    if isinstance(df.index, pd.PeriodIndex):
        return format_period_label(df.index.to_timestamp(), frequency=frequency)

    if isinstance(df.index, pd.DatetimeIndex):
        return format_period_label(df.index, frequency=frequency)

    if df.index.inferred_type in ("string", "unicode"):
        values = [str(x) for x in df.index]
        if all(re.fullmatch(r"\d{4}", v) for v in values):
            return values
        parsed_index = pd.to_datetime(df.index, errors="coerce")
        if parsed_index.notna().all():
            return format_period_label(parsed_index, frequency=frequency)

    if df.index.inferred_type in ("integer", "mixed-integer"):
        years = [int(x) for x in df.index if str(x).isdigit() and 1900 <= int(x) <= 2100]
        if len(years) == len(df.index):
            return [str(year) for year in years]

    known_columns = [
        "period_ending",
        "period",
        "period_end",
        "periodend",
        "end_date",
        "fiscal_date",
        "report_date",
        "date",
        "filing_date",
        "calendar_date",
        "date_filed",
    ]
    for col in known_columns:
        if col in df.columns:
            parsed_col = pd.to_datetime(df[col], errors="coerce")
            if parsed_col.notna().all():
                return format_period_label(parsed_col, frequency=frequency)

    for col in df.columns:
        values = df[col].astype(str)
        if values.str.match(r"^Q[1-4]\s*\d{2,4}$").all():
            return values.tolist()

    return [str(x) for x in df.index]


METRIC_OPTIONS = [
    "Price",
    "Revenues",
    "Gross Profit",
    "Operating Income",
    "EBITDA",
    "Net Earnings",
    "EPS",
    "Free Cash Flow",
    "Operating Cash Flow",
    "Total Assets",
    "Total Liabilities",
    "Total Equity",
    "Cash & Equivalents",
    "Revenue Growth",
    "Earnings Growth",
    "Net Income Growth",
    "EPS Growth",
    "Gross Margin",
    "Operating Margin",
    "Net Margins",
    "Current Ratio",
    "Quick Ratio",
    "Debt to Equity",
    "Return on Assets",
    "Return on Equity",
    "GMV per buyer",
    "GMV",
    "GMV growth",
    "unique active buyers",
    "Active seller count",
    "NPS score",
    "Advertising take rate",
    "Advertising revenue",
    "Advertising revenue growth rate",
    "Annual Items per Buyer",
    "Customer acquisition cost",
    "Avg. Ticket (AOV)",
    "website Traffic Share",
    "market share",
    "Non performing loans past 90 days due",
    "15-90 Day NPL",
    "Net Interest Margin After Losses",
    "customer deposits amount",
    "Total Customers",
    "Monthly Active Users (MAU) in Fintech",
    "Net Revenue Margin on TPV (Fintech Take Rate)",
    "Float & Deposits Growth",
]

MANUAL_METRICS = [
    "GMV per buyer",
    "GMV",
    "GMV growth",
    "unique active buyers",
    "Active seller count",
    "NPS score",
    "Advertising take rate",
    "Advertising revenue",
    "Advertising revenue growth rate",
    "Annual Items per Buyer",
    "Customer acquisition cost",
    "Avg. Ticket (AOV)",
    "website Traffic Share",
    "market share",
    "Non performing loans past 90 days due",
    "15-90 Day NPL",
    "Net Interest Margin After Losses",
    "customer deposits amount",
    "Total Customers",
    "Monthly Active Users (MAU) in Fintech",
    "Net Revenue Margin on TPV (Fintech Take Rate)",
    "Float & Deposits Growth",
]

API_METRICS = [m for m in METRIC_OPTIONS if m not in MANUAL_METRICS]


def get_price_series(ticker, start_date, end_date):
    df = obb.equity.price.historical(
        ticker,
        start_date=start_date,
        end_date=end_date,
        provider="yfinance"
    ).to_dataframe()
    return df['close'] if 'close' in df.columns else None


def get_metric_series(ticker_data, metric):
    income = ticker_data.get("income")
    balance = ticker_data.get("balance")
    cash = ticker_data.get("cash")

    if metric == "Revenues":
        col = find_column(income, ["revenue"]) or find_column(income, ["sales"])
        return income[col] if col is not None else None

    if metric == "Gross Profit":
        col = find_column(income, ["gross", "profit"])
        return income[col] if col is not None else None

    if metric == "Operating Income":
        col = find_column(income, ["operating", "income"])
        return income[col] if col is not None else None

    if metric == "EBITDA":
        col = find_column(income, ["ebitda"])
        return income[col] if col is not None else None

    if metric in ["Net Income", "Net Earnings"]:
        col = find_column(income, ["net", "income"]) or find_column(income, ["net_income"])
        return income[col] if col is not None else None

    if metric == "EPS":
        col = find_column(income, ["eps"]) or find_column(income, ["earnings", "per", "share"])
        return income[col] if col is not None else None

    if metric == "Operating Cash Flow":
        col = find_column(cash, ["operating", "cash"])
        return cash[col] if col is not None else None

    if metric == "Free Cash Flow":
        col = find_column(cash, ["free", "cash"])
        return cash[col] if col is not None else None

    if metric == "Cash & Equivalents":
        col = find_column(balance, ["cash"]) or find_column(balance, ["cash", "equivalents"])
        return balance[col] if col is not None else None

    if metric == "Total Assets":
        col = find_column(balance, ["total", "assets"])
        return balance[col] if col is not None else None

    if metric == "Total Liabilities":
        col = find_column(balance, ["total", "liabilities"])
        return balance[col] if col is not None else None

    if metric == "Total Equity":
        col = find_column(balance, ["total", "equity"]) or find_column(balance, ["shareholders", "equity"])
        return balance[col] if col is not None else None

    if metric == "Gross Margin":
        revenue = get_metric_series(ticker_data, "Revenues")
        gross_profit = get_metric_series(ticker_data, "Gross Profit")
        return (gross_profit / revenue) * 100 if revenue is not None and gross_profit is not None else None

    if metric == "Operating Margin":
        revenue = get_metric_series(ticker_data, "Revenues")
        operating_income = get_metric_series(ticker_data, "Operating Income")
        return (operating_income / revenue) * 100 if revenue is not None and operating_income is not None else None

    if metric in ["Net Margin", "Net Margins"]:
        revenue = get_metric_series(ticker_data, "Revenues")
        net_income = get_metric_series(ticker_data, "Net Income")
        return (net_income / revenue) * 100 if revenue is not None and net_income is not None else None

    if metric == "Revenue Growth":
        series = get_metric_series(ticker_data, "Revenues")
        return series.pct_change() * 100 if series is not None else None

    if metric in ["Net Income Growth", "Earnings Growth"]:
        series = get_metric_series(ticker_data, "Net Income")
        return series.pct_change() * 100 if series is not None else None

    if metric == "EPS Growth":
        series = get_metric_series(ticker_data, "EPS")
        return series.pct_change() * 100 if series is not None else None

    if metric == "Current Ratio":
        current_assets = find_column(balance, ["current", "assets"])
        current_liabilities = find_column(balance, ["current", "liabilities"])
        if current_assets is not None and current_liabilities is not None:
            return balance[current_assets] / balance[current_liabilities]
        return None

    if metric == "Quick Ratio":
        current_liabilities = find_column(balance, ["current", "liabilities"])
        quick_assets = None
        for col in balance.columns:
            lower = col.lower()
            if "cash" in lower and "equivalent" in lower:
                quick_assets = col
                break
        if quick_assets is None:
            quick_assets = find_column(balance, ["cash"]) or find_column(balance, ["cash", "equivalents"])
        if current_liabilities is not None and quick_assets is not None:
            return balance[quick_assets] / balance[current_liabilities]
        return None

    if metric == "Debt to Equity":
        total_liabilities = get_metric_series(ticker_data, "Total Liabilities")
        total_equity = get_metric_series(ticker_data, "Total Equity")
        return total_liabilities / total_equity if total_liabilities is not None and total_equity is not None else None

    if metric == "Return on Assets":
        net_income = get_metric_series(ticker_data, "Net Income")
        total_assets = get_metric_series(ticker_data, "Total Assets")
        return (net_income / total_assets) * 100 if net_income is not None and total_assets is not None else None

    if metric == "Return on Equity":
        net_income = get_metric_series(ticker_data, "Net Income")
        total_equity = get_metric_series(ticker_data, "Total Equity")
        return (net_income / total_equity) * 100 if net_income is not None and total_equity is not None else None

    return None


st.set_page_config(page_title="Stock Price Comparison", layout="wide")
st.title("📈 Stock Price Comparison & Metrics")

st.set_page_config(page_title="Stock Analysis & Metrics", layout="wide")
st.title("📈 Stock Analysis & Metrics")

# Date range for price
col_date1, col_date2 = st.columns(2)
with col_date1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
with col_date2:
    end_date = st.date_input("End Date", value=datetime.now())

# Ticker input
ticker_input = st.text_input("Search Company Ticker", "AAPL", placeholder="e.g. AAPL")

if ticker_input:
    ticker = ticker_input.upper()
    
    # Metric selector
    metrics_to_compare = st.multiselect(
        "Select Metrics",
        METRIC_OPTIONS,
        default=["Price", "Revenues", "Net Earnings"]
    )
    
    if metrics_to_compare:
        # Provider and period
        col_a, col_b = st.columns([1, 1])
        with col_a:
            provider = st.selectbox(
                "Fundamentals Provider",
                ["yfinance", "fmp"],
                index=0,
                help="yfinance works without API keys; fmp may require FMP_API_KEY in your environment."
            )
        with col_b:
            period_type = st.radio(
                "Frequency",
                ["Quarterly (Q/Q)", "Annual (Y/Y)"],
                index=0,
                horizontal=True
            )
        
        selected_period = "quarter" if period_type.startswith("Quarterly") else "annual"
        
        # Manual data inputs
        manual_data = {}
        for metric in metrics_to_compare:
            if metric in MANUAL_METRICS:
                with st.expander(f"Manual Input for {metric}"):
                    st.write("Enter data manually. Format: Period,Value (one per line, e.g. 2023,100)")
                    data_input = st.text_area(f"Data for {metric}", "", key=f"manual_{metric}")
                    if data_input.strip():
                        lines = data_input.strip().split('\n')
                        periods = []
                        values = []
                        for line in lines:
                            if ',' in line:
                                parts = line.split(',', 1)
                                if len(parts) == 2:
                                    p, v = parts
                                    periods.append(p.strip())
                                    try:
                                        values.append(float(v.strip()))
                                    except ValueError:
                                        values.append(0.0)
                        if periods and values:
                            manual_data[metric] = pd.Series(values, index=periods)
        
        # Fetch API data
        with st.spinner("Fetching data..."):
            metrics_data = {}
            ticker_data = {}
            for func, key_name in [
                (obb.equity.fundamental.income, "income"),
                (obb.equity.fundamental.balance, "balance"),
                (obb.equity.fundamental.cash, "cash"),
            ]:
                try:
                    df = func(
                        ticker,
                        provider=provider,
                        period=selected_period,
                    ).to_dataframe(index="period_ending")
                    ticker_data[key_name] = normalize_financial_df(df)
                except Exception:
                    ticker_data[key_name] = pd.DataFrame()
            
            metrics_data[ticker] = ticker_data
        
        # Chart each selected metric
        for metric in metrics_to_compare:
            series = None
            if metric == "Price":
                series = get_price_series(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            elif metric in API_METRICS:
                series = get_metric_series(metrics_data.get(ticker, {}), metric)
            elif metric in manual_data:
                series = manual_data[metric]
            
            if series is not None and not series.empty:
                fig = go.Figure()
                
                if metric == "Price":
                    # Line chart for price
                    fig.add_trace(go.Scatter(
                        x=series.index,
                        y=series,
                        mode="lines",
                        name=ticker,
                        line=dict(width=2)
                    ))
                    fig.update_layout(
                        template="plotly_white",
                        title=metric,
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        hovermode="x unified",
                        height=420
                    )
                else:
                    # Bar or line chart for other metrics
                    if metric in manual_data:
                        labels = list(series.index)
                    else:
                        labels = get_period_labels(series.to_frame(), frequency=selected_period)
                    
                    is_percentage_metric = (
                        "Growth" in metric or 
                        "Margin" in metric or 
                        metric in ["Current Ratio", "Quick Ratio", "Debt to Equity", "Return on Assets", "Return on Equity"]
                    )
                    
                    if is_percentage_metric:
                        fig.add_trace(go.Scatter(
                            x=labels,
                            y=series,
                            mode="lines+markers+text",
                            name=ticker,
                            line=dict(width=2),
                            text=[
                                format_percentage_label(v) if "Growth" in metric or "Margin" in metric or metric in ["Return on Assets", "Return on Equity"] else f"{v:.2f}"
                                for v in series
                            ],
                            textposition="top center"
                        ))
                        yaxis_title = metric + (" (%)" if "Growth" in metric or "Margin" in metric or metric in ["Return on Assets", "Return on Equity"] else "")
                        fig.update_layout(
                            template="plotly_white",
                            xaxis_type="category",
                            xaxis_title="Period",
                            yaxis_title=yaxis_title,
                            hovermode="x unified",
                            height=420
                        )
                    else:
                        fig.add_trace(go.Bar(
                            x=labels,
                            y=series,
                            name=ticker,
                            text=[format_large_value(v) for v in series],
                            textposition="auto",
                            texttemplate="%{text}"
                        ))
                        fig.update_layout(
                            template="plotly_white",
                            barmode="group",
                            xaxis_type="category",
                            xaxis_title="Period",
                            yaxis_title=metric,
                            yaxis_tickformat="~s",
                            hovermode="x unified",
                            height=420
                        )
                
                st.subheader(metric)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No data available for {metric}.")
    else:
        st.info("Select at least one metric to analyze.")
else:
    st.info("Enter a ticker symbol to get started.")