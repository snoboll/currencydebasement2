import yfinance as yf
import requests
import json
from datetime import datetime, timedelta
import os

def fetch_gold_prices():
    gold = yf.Ticker("GC=F")
    data = gold.history(start="1973-01-01", end=datetime.now().strftime("%Y-%m-%d"))
    
    gold_prices = {}
    for date, row in data.iterrows():
        year = str(date.year)
        if year not in gold_prices:
            gold_prices[year] = round(row['Close'], 2)
    
    return gold_prices

def fetch_currency_data():
    base_url = "https://api.exchangerate.host/timeseries"
    end_date = datetime.now()
    start_date = datetime(1999, 1, 1)  # API limitation: data available from 1999
    
    currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY', 'INR', 'BRL', 'RUB', 'MXN', 'ZAR', 'SEK', 'NOK']
    
    currency_data = {}
    
    while start_date <= end_date:
        year = start_date.year
        params = {
            'base': 'USD',
            'start_date': f'{year}-12-31',
            'end_date': f'{year}-12-31',
            'symbols': ','.join(currencies)
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data['success']:
            rates = data['rates'][f'{year}-12-31']
            currency_data[str(year)] = {'USD': 0}
            for currency, rate in rates.items():
                currency_data[str(year)][currency] = round((1/rate - 1) * 100, 2)
        
        start_date = datetime(year + 1, 1, 1)
    
    return currency_data

def save_json(data, filename):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Create the full file path
    filepath = os.path.join(script_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filepath}")

if __name__ == "__main__":
    print("Fetching gold prices...")
    gold_prices = fetch_gold_prices()
    save_json(gold_prices, 'goldPrices.json')
    print("Gold prices saved.")
    
    print("Fetching currency data...")
    currency_data = fetch_currency_data()
    if currency_data:
        save_json(currency_data, 'currencyData.json')
        print("Currency data saved.")
    else:
        print("Failed to fetch currency data.")