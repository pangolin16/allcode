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


def get_period_labels(df):
    """Find the best date/period index for chart labels."""
    if isinstance(df.index, pd.PeriodIndex):
        return format_to_quarter(df.index.to_timestamp())

    if isinstance(df.index, pd.DatetimeIndex):
        return format_to_quarter(df.index)

    if df.index.inferred_type in ("string", "unicode"):
        values = [str(x) for x in df.index]
        if all(re.fullmatch(r"\d{4}", v) for v in values):
            return values
        parsed_index = pd.to_datetime(df.index, errors="coerce")
        if parsed_index.notna().all():
            return format_to_quarter(parsed_index)

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
                return format_to_quarter(parsed_col)

    for col in df.columns:
        values = df[col].astype(str)
        if values.str.match(r"^Q[1-4]\s*\d{2,4}$").all():
            return values.tolist()

    return [str(x) for x in df.index]


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


st.set_page_config(page_title="Stock Price Comparison", layout="wide")
st.title("📈 Stock Price Comparison & Metrics")

# Tab selection
tab1, tab2 = st.tabs(["Price Comparison", "Financial Metrics"])

with tab1:
    # Date range picker
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
    with col_date2:
        end_date = st.date_input("End Date", value=datetime.now())

    # Multiple stock inputs
    st.subheader("Enter Stock Tickers")
    col1, col2, col3, col4 = st.columns(4)
    tickers = []

    with col1:
        ticker1 = st.text_input(
            "Stock 1",
            "AAPL",
            placeholder="Search ticker",
            label_visibility="collapsed",
        )
        st.caption("Company 1")
        if ticker1:
            tickers.append(ticker1.upper())

    with col2:
        ticker2 = st.text_input(
            "Stock 2",
            "MSFT",
            placeholder="Search ticker",
            label_visibility="collapsed",
        )
        st.caption("Company 2")
        if ticker2:
            tickers.append(ticker2.upper())

    with col3:
        ticker3 = st.text_input(
            "Stock 3",
            "",
            placeholder="Search ticker",
            label_visibility="collapsed",
        )
        st.caption("Company 3")
        if ticker3:
            tickers.append(ticker3.upper())

    with col4:
        ticker4 = st.text_input(
            "Stock 4",
            "",
            placeholder="Search ticker",
            label_visibility="collapsed",
        )
        st.caption("Company 4")
        if ticker4:
            tickers.append(ticker4.upper())

    if tickers:
        try:
            with st.spinner("Fetching data..."):
                # Create figure
                fig = go.Figure()
                
                # Fetch data for each ticker and add to chart
                for ticker in tickers:
                    df = obb.equity.price.historical(
                        ticker,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                        provider="yfinance"
                    ).to_dataframe()
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df["close"],
                        mode="lines",
                        name=ticker,
                        line=dict(width=2)
                    ))
                
                # Update layout with white background
                fig.update_layout(
                    title="Stock Price Comparison",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    hovermode="x unified",
                    template="plotly_white",
                    height=600,
                    font=dict(size=12)
                )
                
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.subheader("Financial Metrics Comparison")
    
    # Stock inputs for metrics
    st.markdown("#### Search Companies")
    col1, col2, col3, col4 = st.columns(4)
    metric_tickers = []

    with col1:
        m_ticker1 = st.text_input(
            "Company 1",
            "AAPL",
            placeholder="Search ticker",
            label_visibility="collapsed",
            key="m1",
        )
        st.caption("Company 1")
        if m_ticker1:
            metric_tickers.append(m_ticker1.upper())

    with col2:
        m_ticker2 = st.text_input(
            "Company 2",
            "MSFT",
            placeholder="Search ticker",
            label_visibility="collapsed",
            key="m2",
        )
        st.caption("Company 2")
        if m_ticker2:
            metric_tickers.append(m_ticker2.upper())

    with col3:
        m_ticker3 = st.text_input(
            "Company 3",
            "",
            placeholder="Search ticker",
            label_visibility="collapsed",
            key="m3",
        )
        st.caption("Company 3")
        if m_ticker3:
            metric_tickers.append(m_ticker3.upper())

    with col4:
        m_ticker4 = st.text_input(
            "Company 4",
            "",
            placeholder="Search ticker",
            label_visibility="collapsed",
            key="m4",
        )
        st.caption("Company 4")
        if m_ticker4:
            metric_tickers.append(m_ticker4.upper())

    # Metric selection
    st.subheader("Select Metrics to Compare")
    metrics_to_compare = st.multiselect(
        "Metrics",
        ["Revenues", "Revenue Growth", "Net Earnings", "Earnings Growth", "Net Margins"],
        default=["Revenues", "Net Earnings"]
    )

    if metric_tickers and metrics_to_compare:
        try:
            with st.spinner("Fetching financial data..."):
                metrics_data = {}
                
                # Fetch financial data for each ticker
                for ticker in metric_tickers:
                    income_statement = obb.equity.fundamental.income(
                        ticker,
                        provider="yfinance"
                    ).to_dataframe(index="period_ending")
                    
                    if income_statement is not None and not income_statement.empty:
                        if not isinstance(income_statement.index, pd.DatetimeIndex):
                            income_statement.index = pd.to_datetime(
                                income_statement.index, errors="coerce"
                            )
                        income_statement = income_statement.sort_index(ascending=True)
                        metrics_data[ticker] = income_statement
                
                # Debug info - show available data
                if metrics_data:
                    with st.expander("📊 Debug Info - Available Data Columns"):
                        for ticker, df in metrics_data.items():
                            st.write(f"**{ticker}**: {len(df)} records")
                            st.write(f"Columns: {list(df.columns)}")
                            st.write(f"Date range: {df.index[0]} to {df.index[-1]}")

                # Display metrics in separate charts
                if "Revenues" in metrics_to_compare:
                    st.subheader("Revenues")
                    fig_rev = go.Figure()
                    has_revenue_data = False
                    for ticker in metric_tickers:
                        if ticker in metrics_data:
                            df = metrics_data[ticker]
                            # Try different column names for revenue
                            revenue_col = None
                            for col in df.columns:
                                if 'revenue' in col.lower() or 'sales' in col.lower():
                                    revenue_col = col
                                    break
                            
                            if revenue_col is not None:
                                has_revenue_data = True
                                quarter_labels = get_period_labels(df)
                                fig_rev.add_trace(go.Bar(
                                    x=quarter_labels,
                                    y=df[revenue_col],
                                    name=ticker,
                                    text=[format_large_value(v) for v in df[revenue_col]],
                                    textposition="auto",
                                    texttemplate="%{text}"
                                ))
                    
                    if has_revenue_data:
                        fig_rev.update_layout(
                            template="plotly_white",
                            hovermode="x unified",
                            height=400,
                            barmode="group",
                            xaxis_type="category",
                            xaxis_title="Period",
                            yaxis_title="Revenue (USD)",
                            yaxis_tickformat="~s"
                        )
                        st.plotly_chart(fig_rev, use_container_width=True)
                    else:
                        st.warning("No revenue data available for selected companies")

                if "Revenue Growth" in metrics_to_compare:
                    st.subheader("Revenue Growth")
                    fig_rev_growth = go.Figure()
                    has_growth_data = False
                    for ticker in metric_tickers:
                        if ticker in metrics_data:
                            df = metrics_data[ticker]
                            # Find revenue column
                            revenue_col = None
                            for col in df.columns:
                                if 'revenue' in col.lower() or 'sales' in col.lower():
                                    revenue_col = col
                                    break
                            
                            if revenue_col is not None:
                                revenue_growth = df[revenue_col].pct_change() * 100
                                quarter_labels = get_period_labels(df)
                                has_growth_data = True
                                fig_rev_growth.add_trace(go.Scatter(
                                    x=quarter_labels,
                                    y=revenue_growth,
                                    mode="lines+markers+text",
                                    name=ticker,
                                    line=dict(width=2),
                                    text=[format_percentage_label(v) for v in revenue_growth],
                                    textposition="top center"
                                ))
                    
                    if has_growth_data:
                        fig_rev_growth.update_layout(
                            template="plotly_white",
                            hovermode="x unified",
                            height=400,
                            xaxis_type="category",
                            xaxis_title="Period",
                            yaxis_title="Revenue Growth (%)"
                        )
                        st.plotly_chart(fig_rev_growth, use_container_width=True)
                    else:
                        st.warning("No revenue growth data available")

                if "Net Earnings" in metrics_to_compare:
                    st.subheader("Net Earnings")
                    fig_earnings = go.Figure()
                    has_earnings_data = False
                    for ticker in metric_tickers:
                        if ticker in metrics_data:
                            df = metrics_data[ticker]
                            # Try different column names for net income
                            earnings_col = None
                            for col in df.columns:
                                if 'net_income' in col.lower() or 'net income' in col.lower():
                                    earnings_col = col
                                    break
                            
                            if earnings_col is not None:
                                has_earnings_data = True
                                quarter_labels = get_period_labels(df)
                                fig_earnings.add_trace(go.Bar(
                                    x=quarter_labels,
                                    y=df[earnings_col],
                                    name=ticker,
                                    text=[format_large_value(v) for v in df[earnings_col]],
                                    textposition="auto",
                                    texttemplate="%{text}"
                                ))
                    
                    if has_earnings_data:
                        fig_earnings.update_layout(
                            template="plotly_white",
                            hovermode="x unified",
                            height=400,
                            barmode="group",
                            xaxis_type="category",
                            xaxis_title="Period",
                            yaxis_title="Net Earnings (USD)",
                            yaxis_tickformat="~s"
                        )
                        st.plotly_chart(fig_earnings, use_container_width=True)
                    else:
                        st.warning("No net earnings data available for selected companies")

                if "Earnings Growth" in metrics_to_compare:
                    st.subheader("Earnings Growth")
                    fig_earnings_growth = go.Figure()
                    has_earnings_growth_data = False
                    for ticker in metric_tickers:
                        if ticker in metrics_data:
                            df = metrics_data[ticker]
                            # Find net income column
                            earnings_col = None
                            for col in df.columns:
                                if 'net_income' in col.lower() or 'net income' in col.lower():
                                    earnings_col = col
                                    break
                            
                            if earnings_col is not None:
                                earnings_growth = df[earnings_col].pct_change() * 100
                                quarter_labels = get_period_labels(df)
                                has_earnings_growth_data = True
                                fig_earnings_growth.add_trace(go.Scatter(
                                    x=quarter_labels,
                                    y=earnings_growth,
                                    mode="lines+markers+text",
                                    name=ticker,
                                    line=dict(width=2),
                                    text=[format_percentage_label(v) for v in earnings_growth],
                                    textposition="top center"
                                ))
                    
                    if has_earnings_growth_data:
                        fig_earnings_growth.update_layout(
                            template="plotly_white",
                            hovermode="x unified",
                            height=400,
                            xaxis_type="category",
                            xaxis_title="Period",
                            yaxis_title="Earnings Growth (%)"
                        )
                        st.plotly_chart(fig_earnings_growth, use_container_width=True)
                    else:
                        st.warning("No earnings growth data available")

                if "Net Margins" in metrics_to_compare:
                    st.subheader("Net Margins")
                    fig_margins = go.Figure()
                    has_margin_data = False
                    for ticker in metric_tickers:
                        if ticker in metrics_data:
                            df = metrics_data[ticker]
                            # Find revenue and net income columns
                            revenue_col = None
                            earnings_col = None
                            for col in df.columns:
                                if 'revenue' in col.lower() or 'sales' in col.lower():
                                    revenue_col = col
                                if 'net_income' in col.lower() or 'net income' in col.lower():
                                    earnings_col = col
                            
                            if revenue_col is not None and earnings_col is not None:
                                net_margin = (df[earnings_col] / df[revenue_col]) * 100
                                quarter_labels = get_period_labels(df)
                                has_margin_data = True
                                fig_margins.add_trace(go.Scatter(
                                    x=quarter_labels,
                                    y=net_margin,
                                    mode="lines+markers+text",
                                    name=ticker,
                                    line=dict(width=2),
                                    text=[format_percentage_label(v) for v in net_margin],
                                    textposition="top center"
                                ))
                    
                    if has_margin_data:
                        fig_margins.update_layout(
                            template="plotly_white",
                            hovermode="x unified",
                            height=400,
                            xaxis_type="category",
                            xaxis_title="Period",
                            yaxis_title="Net Margin (%)"
                        )
                        st.plotly_chart(fig_margins, use_container_width=True)
                    else:
                        st.warning("No net margin data available")

        except Exception as e:
            st.error(f"Error fetching financial data: {e}")
            st.info("Note: Make sure the ticker symbols are correct and financial data is available.")