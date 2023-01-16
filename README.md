# Python Algorithmic Trading Bot

Runs AlgoBot for Trading Different Strategies on Eternal Python Script. Has capabilities of executing live trades through Alpaca API Trading brokerage account. Looking to implement backtesting capabilities in near future.

**Required Parameters**
---------
- ### **yfSymbol**: *str*</br>
    ticker symbol as shown on yahoo finance
- ### **interval**: *str*</br>
    same inputs as yfinance interval parameter; Ex. '5y', '15m', '3mo', '1d'
- ### **qty**: *float*</br>
    number of shares to trade (make sure trading account has enough or orders will not execute)
- ### **AlpacaSymbol**: *str*</br>
    if ticker symbol on yahoo finance and Alpaca are different, indicate symbol on Alpaca here for orders
- ### **USmarket**: *bool*</br>
    If the ticker trades on the US market, limit hours of script to US market time period
- ### **crypto**: *bool*</br>
    if ticker is a crypto, timeshift back 4 hours to account for timezone
- ### **placeTrades**: *bool*</br>
    if false, don't place trades but simulate