import yfinance as yf
import streamlit as st
import datetime as dt
import pandas as pd
import pandas_ta as ta
# import numpy as np
import time
import json
import requests
import warnings
import plotly.express as px
# from sklearn.linear_model import RidgeCV
# from sklearn.model_selection import RepeatedKFold
import subprocess
import sys

folder = "AlgoBot/"

# Edit display options
pd.options.display.show_dimensions = False
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')


def interactive_plot(df: pd.DataFrame, title: str):
    """Uses Plotly.Express to chart a line graph of numeric data from each column of a dataframe"""
    fig = px.line(title=title)
    fig.update_layout(autosize=True, xaxis_title="Datetime", yaxis_title="Profit/Loss in Dollars")
    for k in df.columns:
        fig.add_scatter(x=df.index, y=df[k], name=k)
    fig.update_traces(showlegend=True)
    return fig


class ExecuteStrategy:
    def __init__(self, df: pd.DataFrame, type: str = "long"):
        """
        Calls an algo trading strategy to run on price data and
        outputs a dataframe with appended indicators and 'Position'
        Currently only parameterized for 15-minute intraday chart

        :param pd.DataFrame df: A dataframe with index of datetime and at least one column labeled 'Price'
        For strategies that require OHLC data, df must have those columns appended as well
        :param str type: A string indicating either a 'long', 'short', or 'both' strategy
        :param str strategy: The name of the strategy in this class to run
        """
        self.df = df
        if type == 'long':
            self.PosUp = 1
            self.PosDown = 0
        if type == 'short':
            self.PosUp = 0
            self.PosDown = -1
        if type == 'both':
            self.PosUp = 1
            self.PosDown = -1

    def Buy_Hold(self) -> pd.DataFrame:
        """
        Buy and hold, passive return
        """
        df = self.df.copy()
        df.Position[-1] = self.PosUp
        return df


    def MACD_Indicator(self) -> pd.DataFrame:
        """
        Strategy that uses MACD for 15-minute chart to create
        buy and sell signals. outputs dataframe with 'Position'
        and appended MACD and Signal lines
        """
        df = self.df.copy()
        # MACD (12, 26, 9) quick sell signal, more transactions
        ema_fast = df['Adj Close'].ewm(span=12, adjust=False, min_periods=12).mean()
        ema_slow = df['Adj Close'].ewm(span=26, adjust=False, min_periods=26).mean()
        df['MACD'] = ema_fast - ema_slow
        df['Signal'] = df.MACD.ewm(span=9, adjust=False, min_periods=9).mean()

        if df.MACD[-1:].values > df.Signal[-1:].values:
            df.Position[-1] = self.PosUp
        else:
            df.Position[-1] = self.PosDown
        return df

    def MACD_RSI_Indicator(self, length=14) -> pd.DataFrame:
        """
        Uses MACD(12,26,9) and RSI(14) on an M15 chart to create buy
        and sell signals with less false positives. Outputs a dataframe
        with the appended indicators and the appropriate 'Position' to take

        :param int length: amount of days to look back for RSI
        """
        df = self.df.copy()
        # Calculating MACD
        df['MACD_diff'] = ta.macd(df['Adj Close'], fast=12, slow=26, signal=9).iloc[:, 1]
        # Calculating RSI
        df['RSI'] = ta.rsi(df['Adj Close'], length)

        # If previous RSI is less than 30 and current RSI greater than previous, buy
        # Or if MACD crosses over signal line AND RSI is less than 50, buy
        if (df.RSI[-2:-1].values <= 28 and df.RSI[-1:].values > df.RSI[-2:-1].values) or \
                (df.MACD_diff[-1:].values > df.MACD_diff[-4:-1].values.mean() and df.RSI[-1:].values <= 50):
            df.Position[-1] = self.PosUp
        # If previous RSI is greater than 70 and current RSI less than previous, sell
        # Or if Signal line crosses over MACD and RSI greater than 50, sell
        elif (df.RSI[-2:-1].values >= 72 and df.RSI[-1:].values < df.RSI[-2:-1].values) or \
                (df.MACD_diff[-1:].values < df.MACD_diff[-4:-1].values.mean() and df.RSI[-1:].values > 50):
            df.Position[-1] = self.PosDown
        # keep previous position if otherwise
        else:
            df.Position.iloc[-1] = df.Position[-2:-1].values
        return df

    def RSI_Indicator(self, length=14) -> pd.DataFrame:
        """
        Strategy that uses RSI to create buy and sell signals
        outputs dataframe with 'Position' and 'RSI' indicator

        :param int length: How many periods of data it looks back to calculate RSI
        """
        df = self.df.copy()
        df.ta.rsi(close='Adj Close', length=length, append=True)
        df.columns.values[-1] = 'RSI'

        # If previous RSI is less than 30 and current RSI greater than previous, buy
        if df.RSI[-2:-1].values <= 30 and df.RSI[-1:].values > df.RSI[-2:-1].values:
            df.Position[-1] = self.PosUp
        # If previous RSI is greater than 70 and current RSI less than previous, sell
        elif df.RSI[-2:-1].values >= 70 and df.RSI[-1:].values < df.RSI[-2:-1].values:
            df.Position[-1] = self.PosDown
        # keep previous position if otherwise
        else:
            df.Position[-1] = df.Position[-2:-1].values
        return df

    def SuperTrend_MACD_Indicator(self) -> pd.DataFrame:
        """
        Strategy that uses signals from both, 15-minute MACD and
        SuperTrend indicators to create buy or sell signals.
        Outputs dataframe with appended indicators and 'Position'
        """
        df = self.df.copy()
        # Calculating MACD
        df['MACD_diff'] = ta.macd(df.Close, fast=12, slow=26, signal=9).iloc[:, 1]
        # Calculating SUPERTREND
        df['SupertrendDirection'] = ta.supertrend(df.High, df.Low, df.Close, length=10, multiplier=3).iloc[:, 1]

        # If the MACD is greater than the average MACD_diff is positive and Supertrend direction is 1, buy signal
        if df.MACD_diff[-1:].values >= 0 and df.SupertrendDirection[-1:].values > 0:  # both need to be true
            df.Position[-1] = self.PosUp
        else:  # If opposite, sell signal
            df.Position[-1] = self.PosDown
        return df

    def ReynerTeosBBands(self) -> pd.DataFrame:
        df = self.df.copy()
        # Calculating SMA for trend
        df['SMA200'] = ta.sma(df['Adj Close'], 200)
        # Calculating BBands for pullback
        df['LowerBand'] = ta.bbands(df['Adj Close'], 20, 2.5).iloc[:, 0]
        # Calculating RSI for exit
        df['RSI'] = ta.rsi(df['Adj Close'], 2)

        # Write Strategy3

        # Entry Conditions
        if df['FilledPosition'][-2:-1].values == 0 and \
        df['Adj Close'][-1:].values > df['SMA200'][-1:].values and \
        df['Adj Close'][-1:].values < df['LowerBand'][-1:].values:
            df.Position[-1] = self.PosUp
        # Define exit conditions if already position
        elif df['FilledPosition'][-2:-1].values == 1 and \
        (df['RSI'][-1:].values >= 50 or sum(df['FilledPosition'][-11:-1]) == 10):
            df.Position[-1] = self.PosDown
        # If neither entry or exit conditions are met, maintain current position
        else:
            df.Position[-1] = df.Position[-2:-1].values
        return df


    # def Ridge_Indicator(self, window_size : int =7) -> pd.DataFrame:
    #     """
    #     Strategy that uses a ridge regression model to predict
    #     the returns of the next time period to determine if a
    #     position should be active or not. Outputs dataframe with
    #     predicted returns and position
    #     """
    #     stock = self.df.copy()
    #     df = self.df.copy()
    #     stock['LogReturns'] = np.log1p(stock['Adj Close'].pct_change())
    #     stock = stock.loc[:, ['LogReturns']][1:]

    #     # Create n rows for machine to process window size
    #     def create_targets(stock_data, n=window_size):
    #         target_df = stock_data.copy().drop(columns='LogReturns')
    #         for j in range(n, -1, -1):
    #             target_df[f'Target-{j}'] = stock_data['LogReturns'].shift(j)
    #         target_df.rename(columns={'Target-0': 'Target'}, inplace=True)
    #         target_df = target_df[n:]
    #         return target_df

    #     stock_windows = create_targets(stock)

    #     # Preprocessing: Scale data for Ridge Regression modeling
    #     minscaler = float(stock_windows.min()[window_size])
    #     maxscaler = float(stock_windows.max()[window_size])
    #     stock_windows = (stock_windows - minscaler) / (maxscaler - minscaler)

    #     # Convert target pandas df to array
    #     def dfToArray(df):
    #         df_np = df.to_numpy()
    #         X = df_np[:, :-1]
    #         y = df_np[:, -1]
    #         return X, y

    #     # Create splits for Train 70%, Val 30%
    #     split = int(len(stock_windows) * 0.7)
    #     train = stock_windows[:split]
    #     test = stock_windows[split:]

    #     # Split our data accordingly
    #     X_train, y_train = dfToArray(train)
    #     X_test, _ = dfToArray(test)

    #     # define ridge regression model evaluation method
    #     cv = RepeatedKFold(n_splits=10, n_repeats=5, random_state=20005933)
    #     # create model
    #     reg_model = RidgeCV(alphas=np.arange(0, 2+0.01, 0.01), cv=cv, scoring='neg_mean_absolute_error')
    #     # train model
    #     reg_model.fit(X_train, y_train)

    #     # Generate predictions for n days in the future by recursively feeding new predictions
    #     pred_list = []
    #     batch = X_test[-window_size:, -1].reshape(1, window_size)
    #     pred_list.append(reg_model.predict(batch)[0])
    #     predictions = [float((i * (maxscaler - minscaler)) + minscaler) for i in pred_list]
    #     if predictions[0] >= 0:
    #         predictions = [1]
    #     else:
    #         predictions = [-1]

    #     df['RidgeRegD'] = 0
    #     df['RidgeRegD'][-1:] = predictions

    #     # Strategy: Buy/sell at start of day based on if today's returns are predicted to be positive or negative, 1 stock at a time
    #     # Opted to use a Long only strategy because it has lower std and drawdowns than long + short strategy
    #     # If my predicted daily returns for today is higher than the n-day SMA of my predicted daily returns
    #     if df['RidgeRegD'][-1:].values >= 0:
    #         df.Position[-1] = self.PosUp
    #     else:  # If opposite, sell signal
    #         df.Position[-1] = self.PosDown
    #     self.df = df


class AlpacaPaper:
    def __init__(self, AlpacaPaper_KeyID, AlpacaPaper_SecretKey):
        """
        After setting up your Alpaca Brokerage Account, get your
        api key and secret key to connect to your account. Then,
        start trading as you wish
        """
        self.BASE_URL = "https://paper-api.alpaca.markets"
        self.ACCOUNT_URL = f"{self.BASE_URL}/v2/account"
        self.ORDERS_URL = f"{self.BASE_URL}/v2/orders"
        self.POSITIONS_URL = f"{self.BASE_URL}/v2/positions"
        self.PORTFOLIO_URL = f"{self.ACCOUNT_URL}/portfolio/history"
        self.HEADERS = {'APCA-API-KEY-ID': AlpacaPaper_KeyID, 'APCA-API-SECRET-KEY': AlpacaPaper_SecretKey}

    def GetAccount(self):
        r = requests.get(self.ACCOUNT_URL, headers=self.HEADERS)
        return json.loads(r.content)

    def CreateOrder(self, symbol, qty, side, *, type='market', time_in_force='gtc', limit_price=0, trail_percent=0):
        """
        Create an order to trade on Alpaca Paper Trading Account

        :param str symbol: ticker symbol of stock to order
        :param float qty: number of shares to order
        :param str side: 'buy' or 'sell'
        :param str type: 'market', 'limit', 'trailing_stop'
        :param str time_in_force: 'day', 'gtc'
        :param float limit_price: price that you want the order to execute at
        :param float trail_percent: percentage
        """
        limit_price = str(limit_price)
        trail_percent = str(trail_percent)
        type = type.lower()
        time_in_force = time_in_force.lower()

        if type == 'limit':
            data = {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": 'limit',
                "time_in_force": time_in_force,
                "limit_price": limit_price,
            }
        elif type == 'trailing_stop':
            data = {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": 'trailing_stop',
                "time_in_force": time_in_force,
                "trail_percent": trail_percent
            }
        else:  # If type is default, market
            data = {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": 'market',
                "time_in_force": time_in_force,
            }
        r = requests.post(self.ORDERS_URL, json=data, headers=self.HEADERS)
        return json.loads(r.content)

    def GetOrders(self, status="open", symbols=""):
        data = {
            "status": status,
            "symbols": symbols
        }
        r = requests.get(self.ORDERS_URL, params=data, headers=self.HEADERS)
        return json.loads(r.content)

    def CurrentPositions(self, symbol='') -> bool:
        """
        Outputs True or False based on if there is a
        current open position of the input symbol
        :param str symbol: default is all positions, otherwise indicate ticker
        """
        positions_url = f"{self.POSITIONS_URL}/{symbol}"
        r = requests.get(positions_url, headers=self.HEADERS)
        positions_dict = json.loads(r.content)
        if 'symbol' in positions_dict:
            return True
        else:
            return False

    def ClosePosition(self, symbol):
        """
        Closes an existing position or all positions

        Parameters
        ---
        symbol: str
            indicate '' to delete all positions, otherwise indicate ticker symbol
        """
        positions_url = f"{self.POSITIONS_URL}/{symbol}"
        r = requests.delete(positions_url, headers=self.HEADERS)
        return json.loads(r.content)

    def PortfolioHistory(self, *, period='1M', timeframe='1D', to_csv=False) -> pd.DataFrame:
        """
        Return portolio history data in pandas dataframe (earliest start is start of portfolio)
        """
        data = {
            "period": period,
            "timeframe": timeframe
        }
        r = requests.get(self.PORTFOLIO_URL, params=data, headers=self.HEADERS)
        port_hist = pd.DataFrame(json.loads(r.content))
        port_hist['timestamp'] = pd.to_datetime(port_hist['timestamp'], unit='s')
        port_hist.set_index('timestamp', inplace=True)
        port_hist = port_hist[port_hist['equity'] != 0]

        if to_csv:
            port_hist.to_csv(path_or_buf="LiveDataCSV/Alpaca_Portfolio_History.csv", mode='w', header=True)

        return port_hist