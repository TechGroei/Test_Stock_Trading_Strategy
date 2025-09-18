import pandas as pd
import requests

url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# Pretend to be a browser so we don’t get 403
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
resp.raise_for_status()   # raise an error if status != 200

tables = pd.read_html(resp.text)
sp500 = tables[0]    # first table = S&P 500 constituents
print(sp500.head())
