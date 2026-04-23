import yfinance as yf
import pandas as pd
from funcs import ExecuteStrategy

print("Testing strategy position assignment...")
print("="*80)

data = yf.download('BTC-USD', period="5d", interval="1h", progress=False, multi_level_index=False)
data = data[['Close']].copy()
data['Change'] = data['Close'].diff()
data['Position'] = 0
data['FilledPosition'] = 0
data['Check'] = 0

print(f"Data shape: {data.shape}")
print(f"Initial positions: {data['Position'].unique()}")

executor = ExecuteStrategy(data, 'both')
print(f"PosUp: {executor.PosUp}, PosDown: {executor.PosDown}")

result = executor.Buy_Hold()
print(f"\nBuy_Hold:")
print(f"  Last position value: {result['Position'].iloc[-1]}")
print(f"  Position column type: {type(result['Position'].iloc[-1])}")
print(f"  All positions: {result['Position'].unique()}")

result2 = executor.MACD_Indicator()
print(f"\nMACD_Indicator:")
print(f"  Last position value: {result2['Position'].iloc[-1]}")
print(f"  All positions: {result2['Position'].unique()}")

result3 = executor.Ridge_Indicator()
print(f"\nRidge_Indicator:")
print(f"  Last position value: {result3['Position'].iloc[-1]}")
print(f"  All positions: {result3['Position'].unique()}")

result4 = executor.RandomForest_Indicator()
print(f"\nRandomForest_Indicator:")
print(f"  Last position value: {result4['Position'].iloc[-1]}")
print(f"  All positions: {result4['Position'].unique()}")

print("\n" + "="*80)
print("Strategy position test completed!")
