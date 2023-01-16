# Python Algorithmic Trading Bot

Runs AlgoBot for Trading Different Strategies on Eternal Python Script. Has capabilities of executing live trades through Alpaca API Trading brokerage account. Looking to implement backtesting capabilities in near future.

**Instructions for Starting Streamlit Application Through Your IDE**
---------
- Download the folder where ever you like and keep note of the file path (Ex. `C:/User/Documents/AlgoBot`)
- Open the folder in your preferred IDE and make sure all dependencies in `funcs.py` are available to import</br>
    by using `pip install input_library_name` in your terminal. Ensure that Python 3.10+ is installed with `pip` functionality.
- Once all required dependencies are installed (this can be confirmed by ensuring there are no errors in the project),</br>
    go ahead and open your terminal/command prompt and enter the directory which contains the AlgoBot src code
- Type `streamlit run app.py` while in the appropriate directory and the app should launch after asking for your email (no need to enter it)


**Required Parameters on Information Tab**
---------
- ### **yfSymbol**: *str*</br>
    ticker symbol as shown on yahoo finance
- ### **USmarket**: *bool*</br>
    If the ticker trades on the US market, limit hours of script to US market time period
- ### **crypto**: *bool*</br>
    if ticker is a crypto, timeshift back 4 hours to account for timezone
- ### **placeTrades**: *bool*</br>
    if false, don't place trades but simulate, else must connect to Alpaca Brokerage Account
- ### **AlpacaPaper_KeyID**: *str*</br>
    if connecting to an Alpaca Brokerage Account, input your API Key
- ### **AlpacaPaper_SecretKey**: *str*</br>
    if connecting to an Alpaca Brokerage Account, input your Secret Key
- ### **AlpacaSymbol**: *str*</br>
    if ticker symbol on yahoo finance and Alpaca are different, indicate symbol on Alpaca here for orders

**Required Parameters on Strategy Tab**
---------
- ### **interval**: *str*</br>
    same inputs as yfinance interval parameter; Ex. '5y', '15m', '3mo', '1d'
- ### **algorithm**: *str*</br>
    choose which trading algorithm you would like to trade on
- ### **direction**: *str*</br>
    indicate whether you will be trading 'long', 'short', or 'both'
- ### **qty**: *float*</br>
    number of shares to trade (make sure trading account has enough or orders will not execute)