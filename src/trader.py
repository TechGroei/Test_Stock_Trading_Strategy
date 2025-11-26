"""
trader.py
----------
Paper-trading bot for U.S. stocks (S&P 500).

Strategy:
---------
• Universe: top 500 S&P 500 stocks.
• Buy $5 if a stock fell ≥5% over the last 7 calendar days.
• Sell up to $10 if a stock rose ≥10% over the last 7 calendar days.
• Track portfolio (cash, positions) in a local CSV and Neon DB.

Run once daily, just before market close.
"""

import datetime as dt
import pandas as pd
import yfinance as yf
import requests
from io import StringIO
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import config
from src.logger import logger
from src.database import db

# ------------------------------------------------------------------------------ 
# Utilities
# ------------------------------------------------------------------------------

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_sp500_symbols():
    """Fetch S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        tables = pd.read_html(StringIO(resp.text))
        
        # Find the table with "Symbol" column
        df = None
        for t in tables:
            if "Symbol" in t.columns:
                df = t
                break
                
        if df is None:
            raise ValueError("Could not find S&P 500 table with 'Symbol' column")
            
        symbols = df["Symbol"].head(config.UNIVERSE_SIZE).tolist()
        symbols = [s.replace('.', '-') for s in symbols]
        return symbols
    except Exception as e:
        logger.error(f"Error fetching S&P 500 symbols: {e}")
        raise

def load_portfolio():
    """Load portfolio from CSV (primary) and DB (secondary/verification)."""
    # Load from CSV
    if config.DATA_FILE.exists():
        pf_csv = pd.read_csv(config.DATA_FILE)
    else:
        pf_csv = pd.DataFrame(columns=["symbol", "shares", "avg_price", "value",
                                     "last_buy_date", "last_sell_date"])
    
    # Load from DB for verification (optional logging of diffs could go here)
    try:
        pf_db = db.load_portfolio()
        if not pf_db.empty and not pf_csv.empty:
            logger.info(f"Loaded portfolio. CSV rows: {len(pf_csv)}, DB rows: {len(pf_db)}")
    except Exception as e:
        logger.error(f"Failed to load from DB: {e}")

    return pf_csv

def save_portfolio(pf: pd.DataFrame):
    """Save portfolio to CSV and DB."""
    # Save to CSV
    pf.to_csv(config.DATA_FILE, index=False)
    
    # Save to DB
    db.save_portfolio(pf)

def record_trade(symbol, action, qty, price, cash):
    """Append a trade record to trades_history.csv and DB."""
    trade_data = {
        "date": dt.date.today().isoformat(),
        "symbol": symbol,
        "action": action,
        "quantity": qty,
        "price": price,
        "cash_after": cash
    }
    trade = pd.DataFrame([trade_data])
    
    # Save to CSV
    if config.TRADES_FILE.exists():
        trade.to_csv(config.TRADES_FILE, mode="a", header=False, index=False)
    else:
        trade.to_csv(config.TRADES_FILE, index=False)
        
    # Save to DB
    db.record_trade(symbol, action, qty, price, cash)

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
    """Log daily summary."""
    today = dt.date.today()
    logger.info(f"=== {today} ===")
    if trades:
        for t in trades:
            logger.info(t)
    else:
        logger.info("No trades executed.")
    logger.info(f"Cash balance: ${cash:.2f}")

def save_performance_snapshot(pf, cash):
    """Save a daily/weekly performance snapshot."""
    today = dt.date.today().isoformat()
    total_value = pf["value"].sum() if not pf.empty else 0
    total_equity = cash + total_value
    perf_file = config.PERF_DIR / f"performance_weekly_{today}.csv"
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
    try:
        logger.info("Starting daily run...")
        symbols = get_sp500_symbols()
        logger.info(f"Fetched {len(symbols)} symbols.")

        # Fetch last 7 days of adjusted close prices
        end = dt.datetime.now()
        start = end - dt.timedelta(days=7)
        price_data = {}
        failed_tickers = []

        # Batch download could be more efficient, but keeping per-symbol for robustness as per original design
        # Or we can use yf.download(tickers=symbols) which is much faster.
        # Let's stick to the original loop structure but add retry to the download if possible, 
        # or just keep the try/except block.
        # yfinance has its own retries, but we can wrap it.
        
        for sym in symbols:
            try:
                # yfinance download is not easily wrapped with tenacity per call if we want to catch specific errors
                # inside the loop without stopping the whole loop.
                # We'll keep the try/except but maybe add a small sleep or retry inside.
                data = yf.download(sym, start=start, end=end, progress=False, auto_adjust=False)
                adj_close = data.get("Adj Close")
                if adj_close is None or adj_close.empty:
                    # logger.warning(f"Skipping {sym}: no adjusted close data.")
                    failed_tickers.append(sym)
                    continue
                price_data[sym] = adj_close
            except Exception as e:
                logger.error(f"Failed to get ticker '{sym}' reason: {e}")
                failed_tickers.append(sym)

        if price_data:
            prices = pd.concat(price_data, axis=1)
            if isinstance(prices.columns, pd.MultiIndex):
                prices.columns = prices.columns.get_level_values(0)
        else:
            prices = pd.DataFrame()

        if prices.empty:
            logger.error("No price data downloaded. Exiting.")
            pf = load_portfolio()
            cash = config.START_CAPITAL - pf["value"].sum() if not pf.empty else config.START_CAPITAL
            save_performance_snapshot(pf, cash)
            return

        latest = prices.iloc[-1]
        week_start = prices.iloc[0]
        pct_change = (latest - week_start) / week_start * 100

        pf = load_portfolio()
        cash = config.START_CAPITAL - pf["value"].sum() if not pf.empty else config.START_CAPITAL
        trades = []

        for sym in symbols:
            if sym not in pct_change:
                continue
            change = pct_change[sym]
            price = latest[sym]

            # BUY
            if change <= config.DROP_PCT and cash >= config.BUY_AMOUNT:
                qty = config.BUY_AMOUNT / price
                pf = add_position(pf, sym, qty, price)
                cash -= config.BUY_AMOUNT
                trades.append(f"BUY  {sym} {qty:.4f} @ ${price:.2f}")
                record_trade(sym, "BUY", qty, price, cash)

            # SELL
            elif change >= config.GAIN_PCT and sym in pf["symbol"].values:
                held_qty = pf.loc[pf["symbol"] == sym, "shares"].values[0]
                qty = min(config.SELL_AMOUNT / price, held_qty)
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

        if failed_tickers:
            logger.warning(f"Failed downloads ({len(failed_tickers)}): {failed_tickers}")
            
    except Exception as e:
        logger.critical(f"Critical error in run_day: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    run_day()

