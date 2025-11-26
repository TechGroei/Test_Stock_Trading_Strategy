import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.performance import evaluate, fetch_current_prices
from src.config import config

@patch('src.performance.load_portfolio')
@patch('src.performance.fetch_current_prices')
def test_evaluate_success(mock_fetch, mock_load):
    # Mock Portfolio
    mock_load.return_value = pd.DataFrame([{
        "symbol": "AAPL", "shares": 10, "avg_price": 150.0, "value": 1500,
        "last_buy_date": "2023-01-01", "last_sell_date": ""
    }])
    
    # Mock Prices
    mock_prices = pd.DataFrame({
        "AAPL": [160.0]
    })
    mock_fetch.return_value = mock_prices
    
    # Mock Config Paths (to avoid writing to real files)
    with patch('pathlib.Path.mkdir'):
        with patch('pandas.DataFrame.to_csv'):
            snapshot_file = evaluate()
            assert snapshot_file is not None

@patch('src.performance.load_portfolio')
def test_evaluate_empty_portfolio(mock_load):
    mock_load.return_value = pd.DataFrame()
    result = evaluate()
    assert result is None

@patch('yfinance.download')
def test_fetch_current_prices(mock_download):
    mock_download.return_value = pd.DataFrame({"Adj Close": [100.0]})
    prices = fetch_current_prices(["AAPL"])
    assert not prices.empty
