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

# def terminate():
#     st.warning("You have chosen to terminate the AlgoBot")
#     st.experimental_rerun()

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
                (Ex. BTC USD vs BTC-USD), please indicate the symbol as read by Alpaca", disabled=st.session_state.disabled).upper()

    with strategy:
        st.write("### Strategy")
        st.write("""Please select the desired trading interval (how often the algorithm will attempt to execute a trade)""")
        interval = st.selectbox("What trading interval would you like to trade on?", ['5m', '15m', '30m', '1h', '2h', '3h', '6h', '12h'],
            2, disabled=st.session_state.disabled)
        #interval_end = st.radio("What time interval", ['Minute', 'Hour'], 0, disabled=st.session_state.disabled)
        #INTerval = st.number_input(f"How many {interval_end}s in between each trade?", 0, 60, 15, disabled=st.session_state.disabled)
        algorithm = st.selectbox(f"Which trading algorithm would you like to test on {yfSymbol}?",
            ["Buy_Hold", "MACD_Indicator", "MACD_RSI_Indicator", "RSI_Indicator", "ReynerTeosBBands", "Ridge_Indicator"],
            2, disabled=st.session_state.disabled)
        direction = st.selectbox("What is your intended position on this security",
            ["long", "short", "both"], 0, disabled=st.session_state.disabled)
        qty = st.number_input(f"How many shares of {yfSymbol} would you like to trade?", 0, 100, 20, disabled=st.session_state.disabled)

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

    interval_end = interval[-1]
    INTerval = int(interval[:-1])
    period = str(INTerval*2)+interval_end

    try:
        histdata = round(yf.download(
                yfSymbol, 
                period="60d", 
                interval=interval, 
                progress=False)[['Adj Close']],2)
    except OverflowError or Exception:
        raise ConnectionError("Could not download data from yahoo finance")

    all_data = cleanFrame(histdata, algorithm, crypto)
    ndata = len(all_data)-1

    if placeTrades: TradingAccount = \
            AlpacaPaper(AlpacaPaper_KeyID, AlpacaPaper_SecretKey)

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
        col1, col2, col3 = st.columns((4, 4, 6), gap='medium')

        with col1:
            st.header("Key Performance Indicators")
            st.metric(
                f'**Current {yfSymbol} Price\nAnd Change Since Last Query**',
                f"${df['Adj Close'].iloc[-1:].values[0]:.2f}",
                f"{df['Change'].iloc[-1:].values[0]:.2f}"
            )
            st.metric(
                "**Percentage of Profitable Positions**",
                f"{0}%",
                delta=None
            )
            st.metric(
                "**Percentage of Loss-Incurring Positions**",
                f"{0}%",
                delta=None
            )
            st.metric(
                f"**{algorithm} Returns Compared to Passive Returns**",
                f"{0} USD",
                delta=0
            )

        with col2:
            st.header("Live Data")
            st.write(f"Charts and graphs will be updated every {INTerval} {time_interval}s")
            st.dataframe(df[['Adj Close', 'Change', 'Position', 'Check']])
            st.write("To terminate the bot, simply close the tab!")

        with col3:
            st.header(f'{algorithm} Returns, {interval_end.upper()}{INTerval} Chart')
            returnsChart = interactive_plot(df[['Passive Returns', f'{algorithm} Returns']])
            st.plotly_chart(returnsChart)

    # st.button("Terminate Bot", on_click=terminate)

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

            all_data = checkstrat(all_data, execute)
            if placeTrades: placetrade(all_data, TradingAccount, AlpacaSymbol, qty)

            df = all_data[ndata:]

            # Key Metrics
            curr_price = df['Adj Close'].iloc[-1:].values[0]
            curr_change = df['Change'].iloc[-1:].values[0]
            perc_prof = len(df[df["Check"] == 1]) / (len(df) - 1) * 100
            perc_loss = len(df[df["Check"] == -1]) / (len(df) - 1) * 100
            df[f'{algorithm} Returns'] = (df['Change'].shift(1) * df['Position']).cumsum() * qty
            df['Passive Returns'] = df['Change'].cumsum() * qty
            total_strat_ret = df[f'{algorithm} Returns'].iloc[-1:].values[0]
            diff_from_passive_ret = total_strat_ret - df['Passive Returns'].iloc[-1:].values[0]
            
            # Refresh Website with new data
            with placeholder.container():
                col1, col2, col3 = st.columns((4, 4, 6), gap='medium')

                with col1:
                    st.header("Key Performance Indicators")
                    st.metric(
                        f'**Current {yfSymbol} Price\nAnd Change Since Last Query**',
                        f"${curr_price:.2f}",
                        f"{curr_change:.2f}"
                    )
                    st.metric(
                        "**Percentage of Profitable Positions**",
                        f"{perc_prof:.2f}%",
                        delta=None
                    )
                    st.metric("**Percentage of Loss-Incurring Positions**",
                        f"{perc_loss:.2f}%",
                        delta=None
                    )
                    st.metric(
                        f"**{algorithm} Returns Compared to Passive Returns**",
                        f"{total_strat_ret:.2f} USD",
                        delta=f"{diff_from_passive_ret:.2f}"
                    )

                with col2:
                    st.header("Live Data")
                    st.write(f"Website will refresh and update graphs/charts every {INTerval} {time_interval}s")
                    # df_sel = df.query("Position == @position_translation & Check == @check_translation")
                    st.dataframe(df[['Adj Close', 'Change', 'Position', 'Check']])
                    st.write("To terminate the bot, simply close the tab!")
                    
                with col3:
                    st.header(f'{algorithm} Returns, {interval_end.upper()}{INTerval} Chart')
                    returnsChart = interactive_plot(df[['Passive Returns', f'{algorithm} Returns']])
                    st.plotly_chart(returnsChart)

            time.sleep(15)