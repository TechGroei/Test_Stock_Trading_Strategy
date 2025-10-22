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

Changes:
---------
• Track buy/sell dates in portfolio.csv
• Log all trades to trades_history.csv
• Save daily performance snapshot to performance_weekly_<YYYY-MM-DD>.csv
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
DATA_FILE = Path("portfolio.csv")
TRADES_FILE = Path("trades_history.csv")
PERF_DIR = Path("performance")
PERF_DIR.mkdir(exist_ok=True)
# ==============================================================================


# ------------------------------------------------------------------------------ 
# Utilities
# ------------------------------------------------------------------------------

def get_sp500_symbols():
    """Fetch S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    tables = pd.read_html(StringIO(resp.text))
    symbols = tables[0]["Symbol"].head(UNIVERSE_SIZE).tolist()
    symbols = [s.replace('.', '-') for s in symbols]
    return symbols


def load_portfolio():
    """Load portfolio or create an empty one."""
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["symbol", "shares", "avg_price", "value",
                                 "last_buy_date", "last_sell_date"])


def save_portfolio(pf: pd.DataFrame):
    pf.to_csv(DATA_FILE, index=False)


def record_trade(symbol, action, qty, price, cash):
    """Append a trade record to trades_history.csv."""
    trade = pd.DataFrame([{
        "date": dt.date.today(),
        "symbol": symbol,
        "action": action,
        "quantity": qty,
        "price": price,
        "cash_after": cash
    }])
    if TRADES_FILE.exists():
        trade.to_csv(TRADES_FILE, mode="a", header=False, index=False)
    else:
        trade.to_csv(TRADES_FILE, index=False)


def add_position(pf, sym, qty, price):
    """Add or increase a position, updating last_buy_date."""
    today = dt.date.today().isoformat()
    if sym in pf["symbol"].values:
        row = pf.loc[pf["symbol"] == sym]
        new_qty = row["shares"].values[0] + qty
        new_avg = (row["shares"].values[0] * row["avg_price"].values[0] + qty * price) / new_qty
        pf.loc[pf["symbol"] == sym, ["shares", "avg_price", "last_buy_date"]] = [new_qty, new_avg, today]
    else:
        new_row = pd.DataFrame([[sym, qty, price, qty * price, today, ""]],
                               columns=["symbol", "shares", "avg_price", "value",
                                        "last_buy_date", "last_sell_date"])
        pf = pd.concat([pf, new_row], ignore_index=True)
    return pf


def reduce_position(pf, sym, qty, price):
    """Reduce or close a position, updating last_sell_date."""
    today = dt.date.today().isoformat()
    idx = pf.index[pf["symbol"] == sym][0]
    pf.at[idx, "shares"] -= qty
    pf.at[idx, "last_sell_date"] = today
    if pf.at[idx, "shares"] <= 0:
        pf.drop(idx, inplace=True)
    return pf


def log_day(trades, cash):
    """Print daily summary."""
    today = dt.date.today()
    print(f"\n=== {today} ===")
    if trades:
        for t in trades:
            print(t)
    else:
        print("No trades executed.")
    print(f"Cash balance: ${cash:.2f}")


def save_performance_snapshot(pf, cash):
    """Save a daily/weekly performance snapshot."""
    today = dt.date.today().isoformat()
    total_value = pf["value"].sum() if not pf.empty else 0
    total_equity = cash + total_value
    perf_file = PERF_DIR / f"performance_weekly_{today}.csv"
    data = pd.DataFrame([{
        "date": today,
        "cash": cash,
        "portfolio_value": total_value,
        "total_equity": total_equity
    }])
    data.to_csv(perf_file, index=False)


# ------------------------------------------------------------------------------ 
# Core logic
# ------------------------------------------------------------------------------

def run_day():
    """Run one trading day simulation."""
    symbols = get_sp500_symbols()

    end = dt.datetime.now()
    start = end - dt.timedelta(days=7)
    prices = yf.download(symbols, start=start, end=end, progress=False, auto_adjust=False)["Adj Close"]

    if prices.empty:
        print("No price data downloaded. Exiting.")
        return

    latest = prices.iloc[-1]
    week_start = prices.iloc[0]
    pct_change = (latest - week_start) / week_start * 100

    pf = load_portfolio()
    cash = START_CAPITAL - pf["value"].sum() if not pf.empty else START_CAPITAL
    trades = []

    for sym in symbols:
        if sym not in pct_change:
            continue
        change = pct_change[sym]
        price = latest[sym]

        # BUY
        if change <= DROP_PCT and cash >= BUY_AMOUNT:
            qty = BUY_AMOUNT / price
            pf = add_position(pf, sym, qty, price)
            cash -= BUY_AMOUNT
            trades.append(f"BUY  {sym} {qty:.4f} @ ${price:.2f}")
            record_trade(sym, "BUY", qty, price, cash)

        # SELL
        elif change >= GAIN_PCT and sym in pf["symbol"].values:
            held_qty = pf.loc[pf["symbol"] == sym, "shares"].values[0]
            qty = min(SELL_AMOUNT / price, held_qty)
            pf = reduce_position(pf, sym, qty, price)
            cash += qty * price
            trades.append(f"SELL {sym} {qty:.4f} @ ${price:.2f}")
            record_trade(sym, "SELL", qty, price, cash)

    # Update portfolio market value
    if not pf.empty:
        pf["value"] = pf["shares"] * pf["avg_price"]

    save_portfolio(pf)
    save_performance_snapshot(pf, cash)
    log_day(trades, cash)


# ------------------------------------------------------------------------------ 
# Entrypoint
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    run_day()
