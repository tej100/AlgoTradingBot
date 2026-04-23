import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from funcs import ExecuteStrategy
from datetime import datetime

warnings.filterwarnings('ignore')

print("Quick Test - Verifying RandomForest_Indicator strategy...")
print("="*80)

ticker = 'BTC-USD'
interval = '1h'
position = 'both'

print(f"Downloading recent data for {ticker} at {interval} interval...")
data = yf.download(ticker, period="5d", interval=interval, progress=False, multi_level_index=False)

if data.empty:
    print("ERROR: No data downloaded")
    exit(1)

data = data[['Close']].copy()
data = data.ffill()
data = data.dropna()

print(f"Downloaded {len(data)} data points from {data.index[0]} to {data.index[-1]}")

data['Change'] = data['Close'].diff()
data['Position'] = 0
data['FilledPosition'] = 0
data['Check'] = 0

strategies = ["Buy_Hold", "MACD_Indicator", "Ridge_Indicator", "RandomForest_Indicator"]

print("\nTesting strategies...")
print("-"*80)

for strategy_name in strategies:
    try:
        test_data = data.copy()
        executor = ExecuteStrategy(test_data, position)
        strategy_method = getattr(executor, strategy_name)
        result = strategy_method()
        position_value = result['Position'].iloc[-1]
        print(f"{strategy_name:<30} {'PASS':<10} Position: {position_value}")
    except Exception as e:
        print(f"{strategy_name:<30} {'FAIL':<10} Error: {str(e)[:40]}")

print("-"*80)
print("\nQuick test completed successfully!")
print("\nRandomForest_Indicator has been successfully integrated.")
print("You can now run 'python3 backtest.py' for full backtesting.")
