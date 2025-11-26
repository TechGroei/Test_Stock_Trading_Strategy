# 🧠 Automated Paper Trading Bot — S&P 500 Strategy

[![Daily Trader](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/trader.yml/badge.svg)](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/run-trader.yml)
[![Weekly Performance Check](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/portfolio-performance-check.yml/badge.svg)](https://github.com/TechGroei/Test_Stock_Trading_Strategy/actions/workflows/portfolio-performance-check.yml)

A **production-ready** automated paper-trading bot simulating daily and weekly trading of S&P 500 stocks.  
Runs on **GitHub Actions**, maintains a **portfolio** (CSV + PostgreSQL), and **tracks weekly performance** — all automatically.

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
| **Storage**        | Dual persistence: CSV files + Neon DB (PostgreSQL) |
| **Execution**      | Fully automated via GitHub Actions |

</details>

---

<details>
<summary>⚙️ Project Structure</summary>

```
Test_Stock_Trading_Strategy/
├── src/                             # Application code
│   ├── __init__.py
│   ├── trader.py                    # Core trading logic (daily)
│   ├── performance.py               # Weekly performance evaluator
│   ├── config.py                    # Centralized configuration
│   ├── logger.py                    # Structured logging
│   └── database.py                  # Database layer (Neon DB)
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_trader.py
│   └── test_performance.py
├── data/                            # Data files (gitignored)
│   ├── .gitkeep
│   ├── portfolio.csv
│   ├── trades_history.csv
│   └── weekly_summary.csv
├── performance/                     # Performance snapshots (gitignored)
│   ├── .gitkeep
│   └── performance_weekly_*.csv
├── .github/
│   └── workflows/
│       ├── run-trader.yml           # Daily trading pipeline
│       └── portfolio-performance-check.yml  # Weekly performance pipeline
├── .env                             # Environment variables (gitignored)
├── .gitignore
├── requirements.txt                 # Python dependencies
└── README.md
```

</details>

---

<details>
<summary>🧩 Python Components</summary>

### `src/trader.py`
- Fetches and analyzes S&P 500 data using **yfinance**  
- Applies buy/sell rules with **retry logic** for robustness
- Updates:
  - `data/portfolio.csv` (current holdings)  
  - `data/trades_history.csv` (executed trades)
  - **Neon DB** (PostgreSQL) - parallel persistence
- Uses **structured logging** for observability

✅ **Output:** evolving paper portfolio with dual persistence

### `src/performance.py`
- Revalues holdings at market prices  
- Computes cash, invested amount, unrealized P/L, total equity  
- Saves weekly snapshots under `performance/`  
- Updates `data/weekly_summary.csv` summarizing weekly gain/loss
- Integrates with database for consistent data loading

✅ **Output:** weekly performance summaries classified as **WIN**, **LOSS**, or **FLAT**

### `src/config.py`
- Centralized configuration using environment variables
- Manages paths for data and performance directories
- Database connection configuration

### `src/logger.py`
- Structured logging setup
- Replaces print statements for production-grade observability

### `src/database.py`
- SQLAlchemy-based database layer
- Models for Portfolio and Trade entities
- Parallel execution with CSV for verification

</details>

---

<details>
<summary>🤖 GitHub Actions Workflows</summary>

### 🕒 Daily Trading (`run-trader.yml`)
**Purpose:** Automate daily buy/sell operations.

**Trigger:**
```yaml
on:
  schedule:
    - cron: "30 20 * * 1-5"  # Mon–Fri at 20:30 UTC
  workflow_dispatch:
```

**Steps:**

1. Checkout repository
2. Set up Python 3.11
3. Install dependencies from `requirements.txt`
4. Run `python -m src.trader` with `DATABASE_URL` secret
5. Commit updated CSVs in `data/` and `performance/`

✅ Portfolio updates automatically daily (CSV + Database)

### 📅 Weekly Performance (`portfolio-performance-check.yml`)

**Purpose:** Summarize weekly performance.

**Trigger:**

```yaml
on:
  schedule:
    - cron: "0 22 * * 5"  # Every Friday at 22:00 UTC
  workflow_dispatch:
```

**Steps:**

1. Checkout repository
2. Set up Python 3.11
3. Install dependencies from `requirements.txt`
4. Run `python -m src.performance` with `DATABASE_URL` secret
5. Commit generated files:
   * New weekly snapshot: `performance/performance_weekly_<date>.csv`
   * Updated summary: `data/weekly_summary.csv`

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

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/TechGroei/Test_Stock_Trading_Strategy.git
cd Test_Stock_Trading_Strategy
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment** (optional - for database)
```bash
# Create .env file
echo "DATABASE_URL=your_neon_db_connection_string" > .env
```

### Run Scripts

```bash
# 1️⃣ Run daily trading logic
python -m src.trader

# 2️⃣ Evaluate weekly portfolio performance
python -m src.performance

# 3️⃣ Run tests
pytest tests/
```

</details>

---

<details>
<summary>🧾 Requirements</summary>

* Python 3.11+
* Dependencies (see `requirements.txt`):
  - pandas
  - yfinance
  - lxml
  - requests
  - sqlalchemy
  - psycopg2-binary
  - tenacity
  - python-dotenv
  - pytest

Install all at once:
```bash
pip install -r requirements.txt
```

</details>

---

<details>
<summary>🏗️ Production Features</summary>

### Reliability
- ✅ **Retry logic** for network requests (Wikipedia, Yahoo Finance)
- ✅ **Global exception handling** to prevent crashes
- ✅ **Robust error logging** for debugging

### Data Persistence
- ✅ **Dual storage**: CSV files + Neon DB (PostgreSQL)
- ✅ **Parallel execution** for verification (1-month validation period)
- ✅ **ACID compliance** via database transactions

### Observability
- ✅ **Structured logging** (replaces print statements)
- ✅ **Detailed trade history** tracking
- ✅ **Performance snapshots** for analysis

### Configuration
- ✅ **Environment variables** for secrets (DATABASE_URL)
- ✅ **Centralized config** in `src/config.py`
- ✅ **Secure credential management** via GitHub Secrets

### Testing
- ✅ **Unit tests** for position management
- ✅ **Integration tests** with mocked APIs
- ✅ **Automated test suite** via pytest

</details>

---

<details>
<summary>🧠 Notes</summary>

* Paper trading only — **no real trades executed**
* Demonstrates **production-grade quantitative strategy automation** via GitHub Actions
* Ideal for learning:
  * GitHub CI/CD for finance automation
  * Python-based data pipelines with database integration
  * Portfolio performance analytics
  * Production-ready Python project structure
  * Test-driven development for financial applications

</details>

---

## ✨ Author

**Tech Groei**  
Data & Cloud Engineering • AI & Automation  
📧 [techgroei@gmail.com](mailto:techgroei@gmail.com)  
🌐 [https://github.com/TechGroei](https://github.com/TechGroei)