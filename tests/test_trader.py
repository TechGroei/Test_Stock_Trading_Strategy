import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.trader import add_position, reduce_position, get_sp500_symbols

def test_add_position_new():
    pf = pd.DataFrame(columns=["symbol", "shares", "avg_price", "value", "last_buy_date", "last_sell_date"])
    pf = add_position(pf, "AAPL", 10, 150.0)
    
    assert len(pf) == 1
    assert pf.iloc[0]["symbol"] == "AAPL"
    assert pf.iloc[0]["shares"] == 10
    assert pf.iloc[0]["avg_price"] == 150.0

def test_add_position_existing():
    pf = pd.DataFrame([{
        "symbol": "AAPL", "shares": 10, "avg_price": 150.0, "value": 1500, 
        "last_buy_date": "2023-01-01", "last_sell_date": ""
    }])
    pf = add_position(pf, "AAPL", 10, 200.0)
    
    assert len(pf) == 1
    assert pf.iloc[0]["shares"] == 20
    assert pf.iloc[0]["avg_price"] == 175.0  # (150*10 + 200*10) / 20

def test_reduce_position_partial():
    pf = pd.DataFrame([{
        "symbol": "AAPL", "shares": 20, "avg_price": 150.0, "value": 3000, 
        "last_buy_date": "2023-01-01", "last_sell_date": ""
    }])
    pf = reduce_position(pf, "AAPL", 10, 200.0)
    
    assert len(pf) == 1
    assert pf.iloc[0]["shares"] == 10

def test_reduce_position_full():
    pf = pd.DataFrame([{
        "symbol": "AAPL", "shares": 10, "avg_price": 150.0, "value": 1500, 
        "last_buy_date": "2023-01-01", "last_sell_date": ""
    }])
    pf = reduce_position(pf, "AAPL", 10, 200.0)
    
    assert len(pf) == 0

@patch('requests.get')
def test_get_sp500_symbols(mock_get):
    mock_resp = MagicMock()
    mock_resp.text = """
    <table>
        <thead><tr><th>Symbol</th><th>Security</th></tr></thead>
        <tbody>
            <tr><td>MMM</td><td>3M</td></tr>
            <tr><td>AOS</td><td>A. O. Smith</td></tr>
        </tbody>
    </table>
    """
    mock_get.return_value = mock_resp
    
    symbols = get_sp500_symbols()
    assert "MMM" in symbols
    assert "AOS" in symbols
