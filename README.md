# 🧠 Automated Paper Trading Bot — S&P 500 Strategy

[![Daily Trader](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/trader.yml/badge.svg)](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/trader.yml)
[![Weekly Performance Check](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/portfolio-performance-check.yml/badge.svg)](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/portfolio-performance-check.yml)

A fully automated **paper-trading bot** simulating daily and weekly trading of S&P 500 stocks.  
Runs on **GitHub Actions**, maintains a **portfolio**, and **tracks weekly performance** — all automatically.

---

<details>
<summary>📈 Strategy Overview</summary>

| Aspect             | Description |
|-------------------|-------------|
| **Universe**       | S&P 500 constituents (dynamic from Wikipedia) |
| **Buy Rule**       | Buy **\$5** if stock **dropped ≥ 5%** in last 7 days |
| **Sell Rule**      | Sell up to **\$10** if stock **rose ≥ 10%** in last 7 days |
| **Initial Capital**| \$5,000 paper balance |
| **Frequency**      | Daily trades (Mon–Fri) • Weekly performance evaluation |
| **Storage**        | All portfolio, trades, and snapshots saved as CSV |
| **Execution**      | Fully automated via GitHub Actions |

</details>

---

<details>
<summary>⚙️ Project Structure</summary>

```

Test_Stock_Trading_Strategy/
├── trader.py                        # Core trading logic (daily)
├── performance.py                   # Weekly performance evaluator
├── portfolio.csv                    # Current holdings
├── trades_history.csv               # Trade history
├── performance/
│   ├── performance_weekly_2025-W44.csv
│   ├── performance_weekly_2025-W45.csv
│   └── ...
├── weekly_summary.csv               # Aggregated week-by-week results
└── .github/
└── workflows/
├── trader.yml               # Daily trading pipeline
└── portfolio-performance-check.yml  # Weekly performance pipeline

````

</details>

---

<details>
<summary>🧩 Python Components</summary>

### `trader.py`
- Fetches and analyzes S&P 500 data using **yfinance**  
- Applies buy/sell rules  
- Updates:
  - `portfolio.csv` (current holdings)  
  - `trades_history.csv` (executed trades)  
- Logs cash, invested capital, and daily portfolio value  

✅ **Output:** evolving paper portfolio

### `performance.py`
- Revalues holdings at market prices  
- Computes cash, invested amount, unrealized P/L, total equity  
- Saves weekly snapshots under `performance/`  
- Updates `weekly_summary.csv` summarizing weekly gain/loss  

✅ **Output:** weekly performance summaries classified as **WIN**, **LOSS**, or **FLAT**

</details>

---

<details>
<summary>🤖 GitHub Actions Workflows</summary>

### 🕒 Daily Trading (`trader.yml`)
**Purpose:** Automate daily buy/sell operations.

**Trigger:**
```yaml
on:
  schedule:
    - cron: "30 20 * * 1-5"  # Mon–Fri at 20:30 UTC
  workflow_dispatch:
````

**Steps:**

1. Checkout repository
2. Set up Python 3.11
3. Install dependencies: `pandas`, `yfinance`, `lxml`, `requests`, `numpy`
4. Run `trader.py`
5. Commit updated CSVs

✅ Portfolio updates automatically daily

### 📅 Weekly Performance (`portfolio-performance-check.yml`)

**Purpose:** Summarize weekly performance.

**Trigger:**

```yaml
on:
  schedule:
    - cron: "0 21 * * 5"  # Every Friday at 21:00 UTC
  workflow_dispatch:
```

**Steps:**

1. Checkout repository
2. Set up Python 3.11
3. Install dependencies
4. Run:

```bash
python performance.py
```

5. Commit generated files:

   * New weekly snapshot: `performance/performance_weekly_<date>.csv`
   * Updated summary: `weekly_summary.csv`

✅ Full weekly performance history automatically maintained

</details>

---

<details>
<summary>📊 Example Output (Weekly Summary)</summary>

```
=== Weekly Portfolio Summary ===
   year  week_number  start_date  end_date  weekly_pl  win_loss
0  2025           44  2025-10-28  2025-11-01   +32.17     WIN
1  2025           45  2025-11-04  2025-11-08   -14.05     LOSS
```

</details>

---

<details>
<summary>🚀 Running Locally</summary>

```bash
# 1️⃣ Run daily trading logic
python trader.py

# 2️⃣ Evaluate weekly portfolio performance
python performance.py
```

</details>

---

<details>
<summary>🧾 Requirements</summary>

* Python 3.11+
* Install dependencies:

```bash
pip install pandas yfinance lxml requests numpy
```

</details>

---

<details>
<summary>🧠 Notes</summary>

* Paper trading only — **no real trades executed**
* Demonstrates **quantitative strategy automation** via GitHub Actions
* Ideal for learning:

  * GitHub CI/CD for finance automation
  * Python-based data pipelines
  * Portfolio performance analytics

</details>

---

## ✨ Author

**Tech Groei**
Data & Cloud Engineering • AI & Automation
📧 [techgroei@gmail.com](mailto:techgroei@gmail.com)
🌐 [https://github.com/TechGroei](https://github.com/TechGroei)

```