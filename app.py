from funcs import *

st.set_page_config(page_title="Python Algorithmic Trading Bot", page_icon=":robot_face:", layout="wide", initial_sidebar_state="expanded")
remove_top = """
    <style>
        div.block-container{padding-top:2rem;}
    </style>
"""
st.markdown(remove_top, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        """
        ## About the Creator
        __Tejas Appana__ is a passionate university student, studying at Stevens Institute of Technology.
        Currently pursuing a bachelors in Quantitative Finance, Tejas has always been passionate about
        applying mathematial techniques to real world scenarios, and given his creative problem solving
        skills, took it upon himself to self-teach the nuances of computer science and advanced programming
        techniques. Now, Tejas enjoys challenging his capabilities to the highest extent and continues to
        broaden his scope in financial modeling, forecasting, data science, machine learning, time series
        analysis, and even development as of this current project.

        ## Get in Touch
        Explore some of Tejas's other projects and accomplishments.
        - [Email](mailto:tejuppana@gmail.com)
        - [Linkedin](https://linkedin.com/in/tejas-appana)
        - [Github](https://github.com/tej100)
        - [Instagram](https://instagram.com/tejasappana/)
        """
    )

def terminate():
    st.warning("You have chosen to terminate the AlgoBot")
    st.stop()

def disable():
    st.session_state.disabled = True

# Initialize disabled for form_submit_button to False
if "disabled" not in st.session_state:
    st.session_state.disabled = False

leftcol, rightcol = st.columns((7,4))

with leftcol:

    st.markdown(
        """
        # Python Algorithmic Trading Bot

        Runs AlgoBot for Trading Different Strategies on Eternal Python Script.
        Has capabilities of executing live trades through Alpaca API Trading brokerage account.
        Looking to implement backtesting capabilities in near future.
        """
    )

    info, strategy = st.tabs(["Information", "Strategy"])
    with info:
        st.write("### Ticker Info")
        yfSymbol = (st.text_input("Which Ticker would you like to trade?", "SPY", disabled=st.session_state.disabled)).upper()
        if yfSymbol:
            try:
                yf.Ticker(yfSymbol)
            except KeyError or IndexError:
                st.info("Please Input a Valid Ticker Symbol")

        USmarket = st.checkbox("Does this security trade on the US market?", True, disabled=st.session_state.disabled)
        crypto = st.checkbox("Is this security a Cryptocurrency", False, disabled=st.session_state.disabled)
        
        st.write("### Alpaca Info")
        placeTrades = st.checkbox("Would you like to connect your trades to an Alpaca brokerage account?",
                    False, disabled=st.session_state.disabled)
        if placeTrades:
            text_input_container = st.empty()
            AlpacaPaper_KeyID = text_input_container.text_input("What is your Alpaca Paper Key ID?")
            if AlpacaPaper_KeyID != "":
                text_input_container.empty()
                st.info("KeyID: " + "X" * 3*(len(AlpacaPaper_KeyID)//4) + AlpacaPaper_KeyID[-len(AlpacaPaper_KeyID)//4:])
            
            text_input_container = st.empty()
            AlpacaPaper_SecretKey = text_input_container.text_input("What is your Alpaca Paper Secret Key?")
            if AlpacaPaper_SecretKey != "":
                text_input_container.empty()
                st.info("SecretKey: " + "X" * 3*(len(AlpacaPaper_SecretKey)//4) + AlpacaPaper_SecretKey[-len(AlpacaPaper_SecretKey)//4:])

            AlpacaSymbol = st.text_input("If the ticker symbol is different on Alpaca Brokerage \
                (Ex. BTC USD vs BTC-USD), please indicate the symbol as read by Alpaca", disabled=st.session_state.disabled)

    with strategy:
        st.write("### Strategy")
        st.write("""Please select the desired trading interval
        (how often the algorithm will attempt to execute a trade)""")
        interval_end = st.radio("What time interval", ['Second', 'Minute', 'Hour'], 1, disabled=st.session_state.disabled)
        INTerval = st.number_input(f"How many {interval_end}s in between each trade?", 0, 60, 15, disabled=st.session_state.disabled)
        algorithm = st.selectbox(f"Which trading algorithm would you like to test on {yfSymbol}?",
            ["Buy_Hold", "MACD_Indicator", "MACD_RSI_Indicator", "RSI_Indicator", "SuperTrend_MACD_Indicator","Ridge_Indicator"],
            2, disabled=st.session_state.disabled)
        direction = st.selectbox("What is your intended position on this security",
            ["long", "short", "both"], 0, disabled=st.session_state.disabled)
        qty = st.slider(f"How many shares of {yfSymbol} would you like to trade?", 0, 100, 20, disabled=st.session_state.disabled)

with rightcol:
    pass

st.write("-------")

# Submit Button to Execute Program
submit = st.button("Submit Parameters", on_click=disable, disabled=st.session_state.disabled)

if submit:

    # Variables.py
    # ========================================================================================

    # Optional Parameters
    if 'placeTrades' not in locals(): placeTrades = False
    if 'qty' not in locals(): qty = 1
    if 'AlpacaPaper_KeyID' not in locals(): AlpacaPaper_KeyID = ""
    if 'AlpacaPaper_SecretKey' not in locals(): AlpacaPaper_SecretKey = ""
    if 'AlpacaSymbol' not in locals(): AlpacaSymbol = yfSymbol


    current_data = pd.DataFrame(
        data=[],
        columns=['Adj Close', 'Position', 'FilledPosition', 'Check'],
        index=pd.to_datetime([])
        )

    interval_ends = {
        "Second": 's',
        "Minute": 'm',
        "Hour": 'h'
        }
    interval_end = interval_ends[interval_end]

    INTerval = int(INTerval)
    interval = str(INTerval)+interval_end
    period = str(INTerval*2)+interval_end

    try:
        histdata = round(yf.download(
                yfSymbol, 
                period="60d", 
                interval=interval, 
                progress=False)[['Adj Close']],2)
    except OverflowError or Exception:
        raise ConnectionError("Could not download data from yahoo finance")

    def cleanFrame(histdata):
        df = histdata.copy()
        # Adjust Datetime Index to appropriate format
        df.reset_index(inplace=True)
        pd.to_datetime(df['Datetime'])
        if crypto:
            df['Datetime'] = df['Datetime'] - pd.Timedelta(hours=5)
        df['Datetime'] = df["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df.set_index('Datetime', inplace=True)

        df['Change'], df['Position'], df['FilledPosition'], df['Check'] = 0, 0, 0, 0
        df['Passive Returns'], df[f'{algorithm} Returns'] = 0, 0
        df = df[['Adj Close', 'Change', 'Position', 'FilledPosition',
            'Check', 'Passive Returns', f'{algorithm} Returns']]
        return df

    all_data = cleanFrame(histdata)

    ndata = len(all_data)-1

    if placeTrades: TradingAccount = \
            AlpacaPaper(AlpacaPaper_KeyID, AlpacaPaper_SecretKey)

    def placetrade(TradingAccount, all_data):
        # Execute Order on Alpaca Paper Trading Account
        # If Position is Long and there is no Open Position, Open it
        if all_data.Position.tail(1).values == 1 and not TradingAccount.CurrentPositions(AlpacaSymbol):
            TradingAccount.CreateOrder(AlpacaSymbol, qty, 'buy', type='market', time_in_force='gtc')

        # If Position is None and there is an Open Position, Close it
        if all_data.Position.tail(1).values == 0 and TradingAccount.CurrentPositions(AlpacaSymbol):
            TradingAccount.ClosePosition(AlpacaSymbol)

    def checkstrat(execute: ExecuteStrategy, all_data: pd.DataFrame):
        # Check if Strategy is working (1 means Good Trade, 0 means None, -1 means Bad Trade)

        # If previous position was long and change in price from previous to current call is positive, Good!
        # If current position is none and change in price from current to previous call is negative, Good!
        if (all_data.Change[-1:].values >= 0 and all_data.Position[-2:-1].values == execute.PosUp) or \
                (all_data.Change[-1:].values < 0 and all_data.Position[-2:-1].values == execute.PosDown):
            all_data.Check[-1] = 1
        # If current position is long and change in price from current to previous call is negative, Bad!
        # If current position is short and change in price from current to previous call is positive, Bad!
        elif (all_data.Change[-1:].values < 0 and all_data.Position[-2:-1].values == execute.PosUp) or \
            (all_data.Change[-1:].values >= 0 and all_data.Position[-2:-1].values == execute.PosDown):
            all_data.Check[-1] = -1
        # For all other cases, Neutral!
        else: all_data.Check[-1] = 0
        return all_data

    if USmarket:
        market_open = '0930'
        market_close = '1600'
        market_day = range(5)
    else:
        market_open = '0000'
        market_close = '2359'
        market_day = range(7)

    time_interval = {'s': 'second', 'm': 'minute', 'h': 'hour'}
    time_interval = time_interval[interval_end]
    
    # LiveData.py
    # ============================================================================================

    placeholder = st.empty()

    df = all_data[ndata:]
    
    with placeholder.container():
        col1, col2, col3 = st.columns((5, 5, 5), gap='large')

        with col1:
            st.header(f"Current {yfSymbol} Price")
            st.metric(
                '**And Change Since Last Query**',
                f"${df['Adj Close'].iloc[-1:].values[0]:.2f}",
                f"{df['Change'].iloc[-1:].values[0]:.2f}"
            )

        with col2:
            st.header("Live Data")
            st.write(f"Charts and graphs will be updated every {INTerval} {time_interval}s")
            st.dataframe(df[['Adj Close', 'Change', 'Position', 'Check']])

        with col3:
            st.header("Key Performance Indicators")
            st.metric("**Profitable/Losing Positions**",
                f"{0}",
                delta=None
            )
            # st.metric("**Percentage of Bad Positions**",
            #     f"{0}%",
            #     delta=None
            # )
            st.metric(f"**{algorithm} Returns Compared to Passive Returns**",
                f"${0}",
                delta=0
            )

        with st.container():
            returnsChart = interactive_plot(
                df[['Passive Returns', f'{algorithm} Returns']],
                f'Passive Returns vs {algorithm} Returns')
            st.plotly_chart(returnsChart)
 
    st.button("Terminate Bot", on_click=terminate)

    while True:

        currDT = dt.datetime.now()
        dow = currDT.weekday()
        now = currDT.strftime("%H%M")
        time_stamp = currDT.strftime("%Y-%m-%d %H:%M:%S")
        time_attr = getattr(currDT, time_interval)

        if time_attr % INTerval == 0 and \
            currDT.second == 0 and \
            market_open <= now <= market_close and \
            dow in market_day:

            # Get current data
            try:
                price = yf.download(yfSymbol, interval = interval, period = period, progress=False)['Adj Close'][-1:].values[0]
            except OverflowError or Exception or ConnectionError:
                st.info(f"Error: Data Missing")
                continue
            else: pass

            current_data.loc[time_stamp] = pd.Series([price], ['Adj Close'])

            # Append historical data to current data and run through strategy
            all_data = pd.concat([all_data, current_data.tail(1)])
            all_data['Change'][-1] = price - all_data['Adj Close'][-2]
            execute = ExecuteStrategy(all_data, direction)
            all_data = getattr(execute, algorithm)()

            all_data = checkstrat(execute, all_data)
            if placeTrades: placetrade(TradingAccount, all_data)

            df = all_data[ndata:]

            # Key Metrics
            curr_price = df['Adj Close'].iloc[-1:].values[0]
            curr_change = df['Change'].iloc[-1:].values[0]
            perc_prof = len(df[df["Check"] >= 0]) / len(df) * 100
            perc_loss = len(df[df["Check"] == -1]) / len(df) * 100
            df[f'{algorithm} Returns'] = (df['Change'] * df['Position']).cumsum() * qty
            df['Passive Returns'] = df['Change'].cumsum() * qty
            total_strat_ret = df[f'{algorithm} Returns'].iloc[-1:].values[0] * qty
            diff_from_passive_ret = total_strat_ret - df['Passive Returns'].iloc[-1:].values[0] * qty
            
            
            # Refresh Website with new data
            with placeholder.container():
                col1, col2, col3 = st.columns((5, 5, 5), gap='large')

                with col1:
                    st.header(f"Current {yfSymbol} Price")
                    st.metric(
                        '**And Change Since Last Query**',
                        f"${curr_price:.2f}",
                        f"{curr_change:.2f}"
                    )

                with col2:
                    st.header("Live Data")
                    st.write(f"Charts and graphs will be updated every {INTerval} {time_interval}s")
                    # df_sel = df.query("Position == @position_translation & Check == @check_translation")
                    st.dataframe(df[['Adj Close', 'Change', 'Position', 'Check']])

                with col3:
                    st.header("Key Performance Indicators")
                    st.metric("**Profitable/Losing Positions**",
                        f"{perc_prof/perc_loss:.2f}%",
                        delta=None)
                    # st.metric("**Percentage of Bad Positions**",
                    #     f"{perc_loss:.2f}%",
                    #     delta=None
                    # )
                    st.metric(f"**{algorithm} Returns Compared to Passive Returns**",
                        f"${total_strat_ret:.2f}",
                        delta=f"{diff_from_passive_ret:.2f}"
                    )

                with st.container():
                    returnsChart = interactive_plot(
                        df[['Passive Returns', f'{algorithm} Returns']],
                        f'Passive Returns vs {algorithm} Returns')
                    st.plotly_chart(returnsChart)

            time.sleep(15)