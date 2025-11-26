import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Trading Configuration
    START_CAPITAL = 5000
    UNIVERSE_SIZE = 500
    BUY_AMOUNT = 5
    SELL_AMOUNT = 10
    DROP_PCT = -5
    GAIN_PCT = 10
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent  # Project root (one level up from src/)
    DATA_DIR = BASE_DIR / "data"
    DATA_FILE = DATA_DIR / "portfolio.csv"
    TRADES_FILE = DATA_DIR / "trades_history.csv"
    PERF_DIR = BASE_DIR / "performance"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PERF_DIR.mkdir(parents=True, exist_ok=True)

config = Config()
