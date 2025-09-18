"""
performance.py
---------------
Enhanced portfolio performance evaluation for the paper-trading bot.

Features:
- Loads the portfolio saved by `trader.py`
- Fetches latest market prices for mark-to-market valuation
- Calculates:
    • Total cash
    • Total invested
    • Total holdings value (book cost vs. market value)
    • Unrealized P/L per stock
    • Overall realized and unrealized P/L
    • Number of positions and total shares held
- Prints a detailed performance snapshot
"""

import pandas as pd
import numpy as np
from pathlib import Path
import yfinance as yf

DATA_FILE = Path("portfolio.csv")   # CSV created by trader.py
START_CAPITAL = 5000                # must match trader.py config


def evaluate():
    """Evaluate portfolio performance with detailed metrics."""
    if not DATA_FILE.exists():
        print("No portfolio data yet.")
        return

    # Load the portfolio
    pf = pd.read_csv(DATA_FILE, index_col=0)
    if pf.empty:
        print("Portfolio empty.")
        return

    # Current cash: assume everything not invested from initial capital
    invested = pf["value"].sum()
    cash = START_CAPITAL - invested

    # Fetch latest market prices
    symbols = [s.replace('.', '-') for s in pf["symbol"].tolist()]  # ensure Yahoo format
    prices = yf.download(symbols, period="1d", progress=False, auto_adjust=False)["Adj Close"]

    # Compute current market value for each holding
    current_values = {}
    unrealized_pl = {}
    for sym in pf["symbol"]:
        yf_sym = sym.replace('.', '-')
        if yf_sym not in prices.columns or np.isnan(prices[yf_sym].iloc[-1]):
            current_price = pf.loc[pf["symbol"] == sym, "avg_price"].values[0]  # fallback to cost
        else:
            current_price = prices[yf_sym].iloc[-1]

        shares = pf.loc[pf["symbol"] == sym, "shares"].values[0]
        cost = pf.loc[pf["symbol"] == sym, "avg_price"].values[0] * shares
        market_val = current_price * shares
        current_values[sym] = market_val
        unrealized_pl[sym] = market_val - cost

    # Aggregate stats
    total_market_value = sum(current_values.values())
    total_unrealized_pl = sum(unrealized_pl.values())
    total_portfolio_value = cash + total_market_value

    # Print summary
    print("\n=== Portfolio Performance Snapshot ===")
    print(f"Cash available: ${cash:.2f}")
    print(f"Invested (book cost): ${invested:.2f}")
    print(f"Market value of holdings: ${total_market_value:.2f}")
    print(f"Total portfolio value: ${total_portfolio_value:.2f}")
    print(f"Total unrealized P/L: ${total_unrealized_pl:.2f} ({total_unrealized_pl / invested * 100:.2f}%)")
    print(f"Number of positions held: {len(pf)}")
    print("\nIndividual holdings:")
    for sym in pf["symbol"]:
        shares = pf.loc[pf["symbol"] == sym, "shares"].values[0]
        cost = pf.loc[pf["symbol"] == sym, "avg_price"].values[0] * shares
        mval = current_values[sym]
        pl = unrealized_pl[sym]
        print(f" - {sym}: {shares:.4f} shares | Book: ${cost:.2f} | Market: ${mval:.2f} | P/L: ${pl:.2f}")

    # Optional: compute simple win/loss stats
    winners = [s for s, v in unrealized_pl.items() if v > 0]
    losers = [s for s, v in unrealized_pl.items() if v < 0]
    print(f"\nWinning positions: {len(winners)} | Losing positions: {len(losers)}")


if __name__ == "__main__":
    evaluate()
