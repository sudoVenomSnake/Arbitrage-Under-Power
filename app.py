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