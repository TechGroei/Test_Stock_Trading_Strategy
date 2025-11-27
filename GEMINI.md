# Repository Summary: Automated Paper Trading Bot

This repository contains an automated paper-trading bot that simulates daily and weekly trading of S&P 500 stocks. It's designed for production-readiness, utilizing GitHub Actions for automation, maintaining a portfolio, and tracking weekly performance.

## Key Features:
- **Automated Trading:** Daily buy/sell operations based on a defined strategy.
- **S&P 500 Strategy:** Buys if a stock dropped ≥ 5% in the last 7 days, sells if it rose ≥ 10% in the last 7 days.
- **Portfolio Management:** Maintains a portfolio using CSV files and a PostgreSQL database (Neon DB).
- **Performance Tracking:** Weekly performance evaluation with snapshots and summaries.
- **CI/CD:** Automated workflows via GitHub Actions for daily trading and weekly performance checks.
- **Robustness:** Includes retry logic for network requests, global exception handling, and structured logging.
- **Dual Persistence:** Data stored in both CSV and PostgreSQL for verification.

## Project Structure Highlights:
- `src/trader.py`: Core logic for daily trading, data fetching, and portfolio updates.
- `src/performance.py`: Logic for weekly performance evaluation, revaluing holdings, and generating summaries.
- `src/config.py`: Centralized configuration management.
- `src/database.py`: SQLAlchemy-based database layer for Portfolio and Trade entities.
- `.github/workflows/`: Contains GitHub Actions for `run-trader.yml` (daily trading) and `portfolio-performance-check.yml` (weekly performance).
- `data/`: Stores `portfolio.csv`, `trades_history.csv`, and `weekly_summary.csv`.
- `performance/`: Stores weekly performance snapshots.
- `tests/`: Unit and integration tests.

## Technologies Used:
- **Python 3.11+**
- **Libraries:** pandas, yfinance, lxml, requests, sqlalchemy, psycopg2-binary, tenacity, python-dotenv, pytest.
- **Database:** PostgreSQL (Neon DB).
- **CI/CD:** GitHub Actions.

## Setup for Local Run:
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. (Optional) Configure `.env` for database connection: `echo "DATABASE_URL=your_neon_db_connection_string" > .env`.
4. Run daily trading: `python -m src.trader`.
5. Run weekly performance: `python -m src.performance`.
6. Run tests: `pytest tests/`.
