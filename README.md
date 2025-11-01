# 🧠 Automated Paper Trading Bot — S&P 500 Strategy

[![Daily Trader](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/trader.yml/badge.svg)](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/trader.yml)
[![Weekly Performance Check](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/portfolio-performance-check.yml/badge.svg)](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/portfolio-performance-check.yml)

A fully automated **paper-trading bot** that simulates daily and weekly trading of S&P 500 stocks using a simple buy/sell strategy.  
It runs on **GitHub Actions**, maintains its **own portfolio**, and **tracks weekly performance** over time — all without manual work.

---

## 📈 Strategy Overview

| Aspect | Description |
|--------|--------------|
| **Universe** | S&P 500 constituents (fetched dynamically from Wikipedia) |
| **Buy Rule** | Buy **\$5** of any stock that **dropped ≥ 5%** in the last 7 days |
| **Sell Rule** | Sell up to **\$10** of any stock that **rose ≥ 10%** in the last 7 days |
| **Initial Capital** | \$5,000 paper balance |
| **Frequency** | Trades daily (Mon–Fri) • Evaluates performance weekly |
| **Storage** | All portfolio, trade, and performance data saved as CSV files |
| **Execution** | Automated via GitHub Actions (no manual execution needed) |

---

## ⚙️ Project Structure

Test_Stock_Trading_Strategy/
├── trader.py # Core trading logic (runs daily)
├── performance.py # Weekly performance evaluator
├── portfolio.csv # Active holdings
├── trades_history.csv # Trade history
├── performance/
│ ├── performance_weekly_2025-W44.csv
│ ├── performance_weekly_2025-W45.csv
│ └── ...
├── weekly_summary.csv # Aggregated week-by-week results
└── .github/
└── workflows/
├── trader.yml # Daily trading pipeline
└── portfolio-performance-check.yml # Weekly performance pipeline


---

## 🧩 Python Components

### `trader.py`
Runs daily to:
- Fetch and analyze S&P 500 stock data using **yfinance**
- Apply buy/sell rules
- Update:
  - `portfolio.csv` (current holdings)
  - `trades_history.csv` (executed transactions)
- Log cash, invested capital, and daily portfolio value

Output:  
✅ Maintains a **realistic evolving paper portfolio**

---

### `performance.py`
Runs weekly to:
- Revalue holdings at current market prices  
- Compute cash, invested amount, unrealized P/L, and total equity  
- Save weekly snapshots under `performance/`  
- Update `weekly_summary.csv` summarizing each week’s gain/loss

Output:  
✅ Provides **weekly performance summaries** and classifies each week as **WIN**, **LOSS**, or **FLAT**

---

## 🤖 GitHub Actions Workflows

### 🕒 1️⃣ Daily Trading Pipeline (`.github/workflows/trader.yml`)
**Purpose:** Automate daily buy/sell operations and update the simulated portfolio.

**Trigger:**  
```yaml
on:
  schedule:
    - cron: "30 20 * * 1-5"  # Runs Mon–Fri at 20:30 UTC
  workflow_dispatch:          # Allow manual run


Main steps:

Checkout repository

Set up Python 3.11

Install dependencies

Run trader.py

Commit and push updated CSVs (portfolio.csv, trades_history.csv)

✅ Result: Your portfolio stays updated every day automatically.

📅 2️⃣ Weekly Performance Check Pipeline (.github/workflows/portfolio-performance-check.yml)

Purpose: Review and summarize portfolio performance weekly.

Trigger:

on:
  schedule:
    - cron: "0 21 * * 5"  # Every Friday at 21:00 UTC
  workflow_dispatch:


Steps:

Checkout the repository

Set up Python 3.11

Install dependencies:

pip install pandas yfinance lxml requests numpy


Run:

python performance.py


Commit generated files:

New weekly snapshot: performance/performance_weekly_<date>.csv

Updated summary: weekly_summary.csv

✅ Result: A full history of your weekly portfolio performance, visible directly in GitHub.

📊 Example Output (Weekly Summary)
=== Weekly Portfolio Summary ===
   year  week_number  start_date  end_date  weekly_pl  win_loss
0  2025           44  2025-10-28  2025-11-01   +32.17     WIN
1  2025           45  2025-11-04  2025-11-08   -14.05     LOSS

🚀 Running Locally

You can test it locally before letting GitHub Actions handle automation:

# 1️⃣ Run daily trading logic
python trader.py

# 2️⃣ Evaluate weekly portfolio performance
python performance.py

🧠 Notes

This is paper trading only — no real trades are executed.

The project demonstrates quantitative strategy automation using GitHub Actions.

Ideal for learning or experimenting with:

GitHub CI/CD for finance automation

Python-based data pipelines

Portfolio performance analytics

🧾 Requirements

Python 3.11+

Install dependencies:

pip install pandas yfinance lxml requests numpy

✨ Author

Tech Groei
Data & Cloud Engineering • AI & Automation
📧 techgroei@gmail.com

🌐 https://github.com/TechGroei