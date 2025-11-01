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
- Tracks weekly performance in weekly_summary.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import yfinance as yf
import glob
import datetime as dt

# === Configuration ============================================================
DATA_FILE = Path("portfolio.csv")           # Created by trader.py
PERF_DIR = Path("performance")              # Folder with daily/weekly snapshots
SUMMARY_FILE = Path("weekly_summary.csv")
START_CAPITAL = 5000                        # Must match trader.py config
# ==============================================================================


# ------------------------------------------------------------------------------
# Portfolio Evaluation
# ------------------------------------------------------------------------------

def evaluate():
    """Evaluate current portfolio performance with detailed metrics."""
    if not DATA_FILE.exists():
        print("No portfolio data yet.")
        return

    pf = pd.read_csv(DATA_FILE)
    if pf.empty:
        print("Portfolio empty.")
        return

    invested = pf["value"].sum()
    cash = START_CAPITAL - invested

    symbols = [s.replace('.', '-') for s in pf["symbol"].tolist()]

    try:
        prices = yf.download(symbols, period="1d", progress=False, auto_adjust=False)["Adj Close"]
    except Exception as e:
        print(f"⚠️ Failed to fetch prices: {e}")
        prices = pd.DataFrame()

    current_values = {}
    unrealized_pl = {}

    for sym in pf["symbol"]:
        yf_sym = sym.replace('.', '-')
        # Default: use stored price if no live data
        current_price = pf.loc[pf["symbol"] == sym, "avg_price"].values[0]

        # Try to get live market price
        if not prices.empty:
            if yf_sym in prices.columns:
                latest_val = prices[yf_sym].iloc[-1]
                if not np.isnan(latest_val):
                    current_price = latest_val

        shares = pf.loc[pf["symbol"] == sym, "shares"].values[0]
        cost = pf.loc[pf["symbol"] == sym, "avg_price"].values[0] * shares
        market_val = current_price * shares
        current_values[sym] = market_val
        unrealized_pl[sym] = market_val - cost

    total_market_value = sum(current_values.values())
    total_unrealized_pl = sum(unrealized_pl.values())
    total_portfolio_value = cash + total_market_value

    # Print performance snapshot
    print("\n=== Portfolio Performance Snapshot ===")
    print(f"Cash available: ${cash:.2f}")
    print(f"Invested (book cost): ${invested:.2f}")
    print(f"Market value of holdings: ${total_market_value:.2f}")
    print(f"Total portfolio value: ${total_portfolio_value:.2f}")
    print(f"Total unrealized P/L: ${total_unrealized_pl:.2f} ({(total_unrealized_pl / invested * 100) if invested > 0 else 0:.2f}%)")
    print(f"Number of positions held: {len(pf)}")

    print("\nIndividual holdings:")
    for sym in pf["symbol"]:
        shares = pf.loc[pf["symbol"] == sym, "shares"].values[0]
        cost = pf.loc[pf["symbol"] == sym, "avg_price"].values[0] * shares
        mval = current_values[sym]
        pl = unrealized_pl[sym]
        print(f" - {sym}: {shares:.4f} shares | Book: ${cost:.2f} | Market: ${mval:.2f} | P/L: ${pl:.2f}")

    winners = [s for s, v in unrealized_pl.items() if v > 0]
    losers = [s for s, v in unrealized_pl.items() if v < 0]
    print(f"\nWinning positions: {len(winners)} | Losing positions: {len(losers)}")

    return {
        "cash": cash,
        "invested": invested,
        "market_value": total_market_value,
        "total_equity": total_portfolio_value
    }


# ------------------------------------------------------------------------------
# Weekly Performance Summary
# ------------------------------------------------------------------------------

def evaluate_weekly():
    """Aggregate weekly performance snapshots and save summary CSV."""
    PERF_DIR.mkdir(exist_ok=True)
    files = sorted(glob.glob(str(PERF_DIR / "performance_weekly_*.csv")))

    if not files:
        print("No weekly snapshots found.")
        return

    weekly_data = []
    for f in files:
        df = pd.read_csv(f)
        if df.empty or "total_equity" not in df.columns:
            continue
        row = df.iloc[-1]
        weekly_data.append({
            "date": pd.to_datetime(row["date"]),
            "total_equity": row["total_equity"]
        })

    weekly_df = pd.DataFrame(weekly_data).sort_values("date").reset_index(drop=True)
    weekly_df["prev_total_equity"] = weekly_df["total_equity"].shift(1)
    weekly_df["weekly_pl"] = weekly_df["total_equity"] - weekly_df["prev_total_equity"]
    weekly_df["week_number"] = weekly_df["date"].dt.isocalendar().week
    weekly_df["year"] = weekly_df["date"].dt.year
    weekly_df["win_loss"] = weekly_df["weekly_pl"].apply(
        lambda x: "WIN" if x > 0 else "LOSS" if x < 0 else "FLAT"
    )

    summary = weekly_df.groupby(["year", "week_number"], as_index=False).agg(
        start_date=("date", "min"),
        end_date=("date", "max"),
        weekly_pl=("weekly_pl", "sum"),
        win_loss=("win_loss", "last")
    )

    print("\n=== Weekly Portfolio Summary ===")
    print(summary[["year", "week_number", "start_date", "end_date", "weekly_pl", "win_loss"]])

    summary.to_csv(SUMMARY_FILE, index=False)
    print(f"\n✅ Weekly summary saved to {SUMMARY_FILE}")


# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    evaluate()
    evaluate_weekly()
