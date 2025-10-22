"""Small change to test CICD"""


"""
trader.py
----------
Paper-trading bot for U.S. stocks (S&P 500).

Strategy:
---------
• Universe: top 500 S&P 500 stocks.
• Buy $5 if a stock fell ≥5% over the last 7 calendar days.
• Sell up to $10 if a stock rose ≥10% over the last 7 calendar days.
• Track portfolio (cash, positions) in a local CSV.

Run once daily, just before market close.
"""

import datetime as dt
import pandas as pd
import yfinance as yf
from pathlib import Path
import requests
from io import StringIO


# ==== CONFIGURATION ===========================================================
START_CAPITAL = 5000
UNIVERSE_SIZE = 500
BUY_AMOUNT = 5
SELL_AMOUNT = 10
DROP_PCT = -5
GAIN_PCT = 10
DATA_FILE = Path("portfolio.csv")  # persist portfolio state
# ==============================================================================


# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------

def get_sp500_symbols():
    """
    Fetch S&P500 tickers from Wikipedia, fix tickers with dots for Yahoo Finance.

    Returns
    -------
    list[str] : tickers ready for yfinance
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    # Wrap HTML to avoid FutureWarning
    tables = pd.read_html(StringIO(resp.text))
    symbols = tables[0]["Symbol"].head(UNIVERSE_SIZE).tolist()

    # Fix tickers for Yahoo Finance: replace "." with "-"
    symbols = [s.replace('.', '-') for s in symbols]
    return symbols


def load_portfolio():
    """
    Load existing portfolio from CSV or create empty DataFrame.
    """
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE, index_col=0)
    return pd.DataFrame(columns=["symbol", "shares", "avg_price", "value"])


def save_portfolio(pf: pd.DataFrame) -> None:
    """Save portfolio to disk."""
    pf.to_csv(DATA_FILE)


def add_position(pf: pd.DataFrame, sym: str, qty: float, price: float) -> pd.DataFrame:
    """
    Add or increase a position. Weighted-average cost if already exists.
    """
    if sym in pf["symbol"].values:
        row = pf.loc[pf["symbol"] == sym]
        new_qty = row["shares"].values[0] + qty
        new_avg = (row["shares"].values[0] * row["avg_price"].values[0] + qty * price) / new_qty
        pf.loc[pf["symbol"] == sym, ["shares", "avg_price"]] = [new_qty, new_avg]
    else:
        new_row = pd.DataFrame([[sym, qty, price, qty * price]],
                               columns=["symbol", "shares", "avg_price", "value"])
        pf = pd.concat([pf, new_row], ignore_index=True)
    return pf


def reduce_position(pf: pd.DataFrame, sym: str, qty: float, price: float) -> pd.DataFrame:
    """
    Reduce or close a position. Remove row if shares reach zero.
    """
    idx = pf.index[pf["symbol"] == sym][0]
    pf.at[idx, "shares"] -= qty
    if pf.at[idx, "shares"] <= 0:
        pf.drop(idx, inplace=True)
    return pf


def log_day(trades: list[str], cash: float) -> None:
    """Print summary of today's trades and cash balance."""
    today = dt.date.today()
    print(f"\n=== {today} ===")
    if trades:
        for t in trades:
            print(t)
    else:
        print("No trades executed.")
    print(f"Cash balance: ${cash:.2f}")


# ------------------------------------------------------------------------------
# Core daily routine
# ------------------------------------------------------------------------------

def run_day() -> None:
    """Run one day of the trading simulation."""
    symbols = get_sp500_symbols()

    # Fetch last 7 days of adjusted close prices
    end = dt.datetime.now()
    start = end - dt.timedelta(days=7)
    prices = yf.download(symbols, start=start, end=end, progress=False, auto_adjust=False)["Adj Close"]

    if prices.empty:
        print("No price data downloaded. Exiting.")
        return

    latest = prices.iloc[-1]
    week_start = prices.iloc[0]
    pct_change = (latest - week_start) / week_start * 100

    # Load portfolio & compute available cash
    pf = load_portfolio()
    cash = START_CAPITAL - pf["value"].sum() if not pf.empty else START_CAPITAL
    trades = []

    # Evaluate each symbol
    for sym in symbols:
        if sym not in pct_change:
            continue
        change = pct_change[sym]
        price = latest[sym]

        # BUY: drop ≥5%
        if change <= DROP_PCT and cash >= BUY_AMOUNT:
            qty = BUY_AMOUNT / price
            pf = add_position(pf, sym, qty, price)
            cash -= BUY_AMOUNT
            trades.append(f"BUY  {sym}  {qty:.4f} @ ${price:.2f}")

        # SELL: rise ≥10%
        elif change >= GAIN_PCT and sym in pf["symbol"].values:
            held_qty = pf.loc[pf["symbol"] == sym, "shares"].values[0]
            qty = min(SELL_AMOUNT / price, held_qty)
            pf = reduce_position(pf, sym, qty, price)
            cash += qty * price
            trades.append(f"SELL {sym} {qty:.4f} @ ${price:.2f}")

    # Update portfolio market value
    if not pf.empty:
        pf["value"] = pf["shares"] * pf["avg_price"]

    save_portfolio(pf)
    log_day(trades, cash)


# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    run_day()
