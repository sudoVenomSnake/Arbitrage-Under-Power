from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from utility import alpha
from curl_cffi import requests

st.set_page_config(layout = "wide")

if "form_submit" not in st.session_state:
    st.session_state.form_submit = False

def form_submit():
    st.session_state.form_submit = True

st.title("Arbitrage under Mean Reversion using the Power Utility")
st.caption("Swastik Mishra (sgm9198) & Aman Dhillon (ad8275)")
st.caption("Instructor - Prof. Daniel Totoum-Tangho")

@st.cache_data
def return_futures_data(ticker, hft = False):
    session = requests.Session(impersonate = "chrome")
    end_date = datetime.today()
    start_date = end_date - timedelta(days = 365)
    if hft:
        start_date = end_date - timedelta(days = 4)
        df = yf.download(tickers = ticker, start = start_date, end = end_date, interval = "1m", auto_adjust = True, progress = False, session = session)
    else:
        start_date = end_date - timedelta(days = 365)
        df = yf.download(tickers = ticker, start = start_date, end = end_date, interval = "1d", auto_adjust = True, progress = False, session = session)
    df = df.reset_index()
    return df

def futures_to_df(df, hft):
    df.reset_index(inplace = True)
    if not hft:
        df["t"] = pd.to_datetime(df["Date"])
    else:
        df["t"] = pd.to_datetime(df["Datetime"])
    df = df.set_index("t")
    return df[["Close"]]

with st.expander(label = "Initial Form -", expanded = not st.session_state.form_submit):
    st.markdown("""##### Try these spreads out !!""")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""###### Precious Metals
| Pair                 | Tickers |
| -------------------- | ---------------- |
| Gold – Silver        | `GC=F` vs `SI=F` |
| Gold – Platinum      | `GC=F` vs `PL=F` |
| Platinum – Palladium | `PL=F` vs `PA=F` |""")
    with col2:
        st.markdown("""###### Energy Spreads
| Pair                                 | Tickers |
| ------------------------------------ | ---------------- |
| WTI – Brent                          | `CL=F` vs `BZ=F` |
| Gasoline – Crude       | `RB=F` vs `CL=F` |
| Heating Oil – Crude                  | `HO=F` vs `CL=F` |
| Nat Gas – Crude | `NG=F` vs `CL=F` |""")
    with col3:
        st.markdown("""###### Agricultural Spreads
| Pair                       | Tickers |
| -------------------------- | ---------------- |
| Corn – Wheat               | `ZC=F` vs `ZW=F` |
| Soybeans – Corn            | `ZS=F` vs `ZC=F` |
| Soybeans – Soybean Meal    | `ZS=F` vs `ZM=F` |
| Soybean Meal – Soybean Oil | `ZM=F` vs `ZL=F` |""")
    with col1:
        st.markdown("""###### Equity Index Futures        
| Pair                  | Tickers  |
| --------------------- | ----------------- |
| S&P 500 – Nasdaq      | `ES=F` vs `NQ=F`  |
| S&P 500 – Dow         | `ES=F` vs `YM=F`  |
| Nasdaq – Russell 2000 | `NQ=F` vs `RTY=F` |""")
    with col2:
        st.markdown("""###### Rates / Bonds     
| Pair                      | Tickers                 |
| ------------------------- | -------------------------------- |
| 10Y – 2Y Treasury (curve) | `ZN=F` vs `ZT=F`                 |
| 30Y – 10Y                 | `ZB=F` vs `ZN=F`                 |
| Eurodollar curve (legacy) | `GE=F` vs `GE=F` |""")
    with col3:
        st.markdown("""###### Mean-Reverting Stock Pairs
| Pair              | Tickers        |
| ----------------- | -------------- |
| JPM – BAC         | `JPM` vs `BAC` |
| GS – MS           | `GS` vs `MS`   |
| Visa – Mastercard | `V` vs `MA`    |""")
    with col1:
        st.markdown("""###### Soft Drinks / Tech / Semiconductors              
| Pair              | Tickers          |
| ----------------- | ---------------- |
| Coke – Pepsi      | `KO` vs `PEP`    |
| Apple – Microsoft | `AAPL` vs `MSFT` |
| Nvidia – AMD      | `NVDA` vs `AMD`  |
| Intel – AMD       | `INTC` vs `AMD`  |""")
    with col2:
        st.markdown("""###### Industrials             
| Pair                    | Tickers         |
| ----------------------- | --------------- |
| Ford – GM               | `F` vs `GM`     |
| Boeing – Airbus (proxy) | `BA` vs `EADSY` |""")
    with col3:
        st.markdown("""###### Industrials               
| Pair                  | Tickers        |
| --------------------- | -------------- |
| S&P 500 – Nasdaq      | `SPY` vs `QQQ` |
| Value – Growth        | `VTV` vs `VUG` |
| Gold ETF – Silver ETF | `GLD` vs `SLV` |
| Banks – Brokers       | `XLF` vs `KBE` |
| Semis – Tech          | `SMH` vs `XLK` |
""")
    col1, col2 = st.columns(2)
    with col1:
        ticker1 = st.text_input(label = "Ticker 1", value = "RB=F")
    with col2:
        ticker2 = st.text_input(label = "Ticker 2", value = "HO=F")
    hft = st.checkbox(label = "Minute Data?")
    st.button(label = "Submit", on_click = form_submit)

if st.session_state.form_submit:
    df1 = futures_to_df(return_futures_data(ticker1, hft), hft)
    df2 = futures_to_df(return_futures_data(ticker2, hft), hft)
    if df1.empty or df2.empty:
        st.header("Tickers may be wrong, please try again or use default. We use yfinance API for data so maybe search for yfinance equivalent tickers!")
        st.stop()
    df = df1.join(df2, how = "inner", lsuffix = "_1", rsuffix = "_2")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df.index, y = df["Close"][ticker1], name = ticker1, yaxis = "y1"))
    fig.add_trace(go.Scatter(x = df.index, y = df["Close"][ticker2], name = ticker2, yaxis = "y2"))
    fig.update_layout(title = "Close Prices", yaxis = dict(title = ticker1), yaxis2 = dict(title = ticker2, overlaying = "y", side = "right"), xaxis_title = "Time", height = 500)
    st.plotly_chart(fig, use_container_width = True)

    df["spread"] = df["Close"][ticker1] - df["Close"][ticker2]
    spread = df["spread"].values

    X = spread
    X_lag = X[:-1]
    dX = X[1:] - X[:-1]
    b, a = np.polyfit(X_lag, dX, 1)

    k = -b
    mu = a / k

    residuals = dX - (a + b * X_lag)
    sigma = np.std(residuals)

    st.subheader("Mean Reversion Parameters")

    col1, col2, col3 = st.columns(3)
    col1.metric("Theta (speed)", round(k, 6))
    col2.metric("Mu (long-run mean)", round(mu, 6))
    col3.metric("Sigma (volatility)", round(sigma, 6))

    col1, col2 = st.columns(2)
    with col1:
        gamma = st.number_input(label = "Gamma for Power Utility - ", min_value = -100., max_value = 0.9999, value = -16.)
    with col2:
        W = st.number_input(label = "Weath - ", min_value = 0.1, max_value = 100000000., value = 100.)

    time = np.arange(len(spread))
    T = time[-1]

    dt = 1.0
    steps = len(spread)

    X_path = []
    alpha_path = []
    W_path = []

    for i in range(steps - 1):
        X = spread[i]
        tau = max(T - time[i], 0)

        a = alpha(W, X, tau, k, gamma, sigma)

        dX = spread[i + 1] - spread[i]
        dW = a * dX

        W += dW
        if W <= 0:
            W = 1e-6

        X_path.append(X)
        alpha_path.append(a)
        W_path.append(W)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x = df.index[:len(X_path)], y = X_path, name = "Spread", yaxis = "y1"))
    fig1.add_trace(go.Scatter(x = df.index[:len(alpha_path)], y = alpha_path, name = "Position (Alpha)", yaxis = "y2", line = dict(dash = "dash")))

    fig1.update_layout(title = "Spread and Optimal Position", yaxis = dict(title = "Spread"), yaxis2 = dict(title="Alpha", overlaying = "y", side = "right"), xaxis_title = "Time", height = 500)
    st.plotly_chart(fig1, use_container_width = True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x = df.index[:len(W_path)], y = W_path, name = "Wealth"))
    fig2.update_layout(title = "Wealth Dynamics (Real Data)", yaxis_title = "Wealth", xaxis_title = "Time", height = 400)
    st.plotly_chart(fig2, use_container_width = True)