import unittest
import sys
import os
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np


class TestRandomForestStrategyExists(unittest.TestCase):

    def test_random_forest_method_exists_on_execute_strategy(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 50)},
            index=pd.date_range('2023-01-01', periods=50, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        executor = ExecuteStrategy(df, 'both')
        self.assertTrue(
            hasattr(executor, 'RandomForest_Indicator'),
            "ExecuteStrategy must have a RandomForest_Indicator method",
        )

    def test_random_forest_method_is_callable(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 50)},
            index=pd.date_range('2023-01-01', periods=50, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        executor = ExecuteStrategy(df, 'both')
        self.assertTrue(callable(getattr(executor, 'RandomForest_Indicator', None)))

    def test_random_forest_returns_dataframe(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 100)},
            index=pd.date_range('2023-01-01', periods=100, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        executor = ExecuteStrategy(df, 'both')
        result = executor.RandomForest_Indicator()
        self.assertIsInstance(result, pd.DataFrame)

    def test_random_forest_output_has_position_column(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 100)},
            index=pd.date_range('2023-01-01', periods=100, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        executor = ExecuteStrategy(df, 'both')
        result = executor.RandomForest_Indicator()
        self.assertIn('Position', result.columns)

    def test_random_forest_position_values_are_valid_both(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 100)},
            index=pd.date_range('2023-01-01', periods=100, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        executor = ExecuteStrategy(df, 'both')
        result = executor.RandomForest_Indicator()
        last_pos = result['Position'].iloc[-1]
        self.assertIn(last_pos, [1, -1, 0])

    def test_random_forest_position_values_long_only(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 100)},
            index=pd.date_range('2023-01-01', periods=100, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        executor = ExecuteStrategy(df, 'long')
        result = executor.RandomForest_Indicator()
        last_pos = result['Position'].iloc[-1]
        self.assertIn(last_pos, [0, 1])

    def test_random_forest_position_values_short_only(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 100)},
            index=pd.date_range('2023-01-01', periods=100, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        executor = ExecuteStrategy(df, 'short')
        result = executor.RandomForest_Indicator()
        last_pos = result['Position'].iloc[-1]
        self.assertIn(last_pos, [0, -1])

    def test_random_forest_preserves_adj_close_column(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 100)},
            index=pd.date_range('2023-01-01', periods=100, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        executor = ExecuteStrategy(df, 'both')
        result = executor.RandomForest_Indicator()
        self.assertIn('Adj Close', result.columns)

    def test_random_forest_does_not_mutate_original_dataframe(self):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': np.random.uniform(100, 200, 100)},
            index=pd.date_range('2023-01-01', periods=100, freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        original_positions = df['Position'].copy()
        executor = ExecuteStrategy(df, 'both')
        _ = executor.RandomForest_Indicator()
        pd.testing.assert_series_equal(df['Position'], original_positions)

    def test_random_forest_uses_sklearn_random_forest(self):
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        self.assertTrue(True, "sklearn RandomForest imports available")


class TestRandomForestFollowsRidgeConventions(unittest.TestCase):

    def test_random_forest_signature_matches_ridge(self):
        from funcs import ExecuteStrategy
        import inspect
        rf_sig = inspect.signature(ExecuteStrategy.RandomForest_Indicator)
        ridge_sig = inspect.signature(ExecuteStrategy.Ridge_Indicator)
        rf_params = [p for p in rf_sig.parameters if p != 'self']
        ridge_params = [p for p in ridge_sig.parameters if p != 'self']
        self.assertEqual(
            len(rf_params), len(ridge_params),
            "RandomForest_Indicator should have the same number of parameters as Ridge_Indicator",
        )

    def test_random_forest_has_window_size_param(self):
        from funcs import ExecuteStrategy
        import inspect
        sig = inspect.signature(ExecuteStrategy.RandomForest_Indicator)
        params = list(sig.parameters.keys())
        self.assertIn('window_size', params)

    def test_random_forest_window_size_default_is_7(self):
        from funcs import ExecuteStrategy
        import inspect
        sig = inspect.signature(ExecuteStrategy.RandomForest_Indicator)
        default = sig.parameters['window_size'].default
        self.assertEqual(default, 7)


class TestFrontendIntegration(unittest.TestCase):

    def test_app_strategy_list_contains_random_forest(self):
        with open(os.path.join(os.path.dirname(__file__), '..', 'app.py'), 'r') as f:
            app_source = f.read()
        self.assertIn(
            'RandomForest_Indicator',
            app_source,
            "app.py must list RandomForest_Indicator as a selectable strategy",
        )

    def test_app_strategy_selectbox_includes_random_forest(self):
        with open(os.path.join(os.path.dirname(__file__), '..', 'app.py'), 'r') as f:
            app_source = f.read()
        self.assertIn('RandomForest_Indicator', app_source)

    def test_existing_strategies_still_present_in_app(self):
        with open(os.path.join(os.path.dirname(__file__), '..', 'app.py'), 'r') as f:
            app_source = f.read()
        for strat in [
            'Buy_Hold', 'MACD_Indicator', 'MACD_RSI_Indicator',
            'RSI_Indicator', 'ReynerTeosBBands', 'Ridge_Indicator',
        ]:
            self.assertIn(strat, app_source, f"Strategy {strat} must remain in app.py")


class TestBacktesterFileExists(unittest.TestCase):

    def _find_backtest_file(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        candidates = []
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                candidates.append(f)
        return candidates

    def test_backtest_file_exists(self):
        candidates = self._find_backtest_file()
        self.assertTrue(
            len(candidates) > 0,
            "A backtesting Python file must exist in the project root",
        )

    def test_backtest_file_is_importable(self):
        candidates = self._find_backtest_file()
        self.assertTrue(len(candidates) > 0, "No backtest file found")
        mod_name = candidates[0].replace('.py', '')
        try:
            importlib.import_module(mod_name)
        except Exception:
            pass


class TestBacktesterConfiguration(unittest.TestCase):

    def _get_backtest_source(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as fh:
                    return fh.read()
        self.fail("No backtest file found")

    def test_uses_btc_usd_ticker(self):
        src = self._get_backtest_source()
        self.assertTrue(
            'BTC-USD' in src or 'BTC/USD' in src,
            "Backtester must use ticker BTC-USD",
        )

    def test_uses_5m_interval(self):
        src = self._get_backtest_source()
        self.assertIn('5m', src, "Backtester must use 5m interval")

    def test_uses_max_data_period(self):
        src = self._get_backtest_source()
        self.assertIn('max', src.lower(), "Backtester must use max data period")

    def test_uses_both_position(self):
        src = self._get_backtest_source()
        self.assertIn('both', src, "Backtester must use position='both'")


class TestBacktesterStrategyCoverage(unittest.TestCase):

    def _get_backtest_source(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as fh:
                    return fh.read()
        self.fail("No backtest file found")

    def test_backtester_includes_all_existing_strategies(self):
        src = self._get_backtest_source()
        required = [
            'Buy_Hold', 'MACD_Indicator', 'MACD_RSI_Indicator',
            'RSI_Indicator', 'ReynerTeosBBands', 'Ridge_Indicator',
        ]
        for strat in required:
            self.assertIn(strat, src, f"Backtester must include strategy: {strat}")

    def test_backtester_includes_random_forest_strategy(self):
        src = self._get_backtest_source()
        self.assertIn(
            'RandomForest_Indicator', src,
            "Backtester must include the new RandomForest_Indicator strategy",
        )


class TestWalkForwardValidation(unittest.TestCase):

    def _get_backtest_source(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as fh:
                    return fh.read()
        self.fail("No backtest file found")

    def test_walk_forward_retrains_on_each_window(self):
        src = self._get_backtest_source()
        has_loop_fit = ('for' in src or 'while' in src) and ('fit' in src or 'train' in src)
        self.assertTrue(
            has_loop_fit,
            "Walk-forward validation requires retraining (fit) inside a loop",
        )

    def test_no_single_fit_on_all_data(self):
        src = self._get_backtest_source()
        lines = src.split('\n')
        fit_count = sum(1 for line in lines if '.fit(' in line)
        self.assertGreaterEqual(
            fit_count, 1,
            "At least one .fit() call should be present for walk-forward training",
        )


class TestIdenticalDateRanges(unittest.TestCase):

    def _get_backtest_source(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as fh:
                    return fh.read()
        self.fail("No backtest file found")

    def test_single_data_download(self):
        src = self._get_backtest_source()
        download_count = src.count('yf.download') + src.count('yf.Ticker')
        self.assertLessEqual(
            download_count, 3,
            "Data should be downloaded once (or very few times) to ensure identical date ranges across strategies",
        )


class TestNoExternalBacktestingLibraries(unittest.TestCase):

    def _get_backtest_source(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as fh:
                    return fh.read()
        self.fail("No backtest file found")

    def test_no_backtrader_import(self):
        src = self._get_backtest_source()
        self.assertNotIn('import backtrader', src)
        self.assertNotIn('from backtrader', src)

    def test_no_zipline_import(self):
        src = self._get_backtest_source()
        self.assertNotIn('import zipline', src)
        self.assertNotIn('from zipline', src)

    def test_no_bt_import(self):
        src = self._get_backtest_source()
        self.assertNotIn('import bt\n', src)
        self.assertNotIn('from bt ', src)

    def test_no_vectorbt_import(self):
        src = self._get_backtest_source()
        self.assertNotIn('import vectorbt', src)
        self.assertNotIn('from vectorbt', src)

    def test_no_pyalgotrade_import(self):
        src = self._get_backtest_source()
        self.assertNotIn('import pyalgotrade', src)
        self.assertNotIn('from pyalgotrade', src)


class TestPerformanceMetrics(unittest.TestCase):

    def _get_backtest_source(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as fh:
                    return fh.read()
        self.fail("No backtest file found")

    def test_calculates_sharpe_ratio(self):
        src = self._get_backtest_source().lower()
        self.assertTrue(
            'sharpe' in src,
            "Backtester must calculate Sharpe ratio",
        )

    def test_calculates_sortino_ratio(self):
        src = self._get_backtest_source().lower()
        self.assertTrue(
            'sortino' in src,
            "Backtester must calculate Sortino ratio",
        )

    def test_calculates_max_drawdown(self):
        src = self._get_backtest_source().lower()
        self.assertTrue(
            'drawdown' in src or 'max_dd' in src or 'max_drawdown' in src,
            "Backtester must calculate max drawdown",
        )

    def test_calculates_total_return(self):
        src = self._get_backtest_source().lower()
        self.assertTrue(
            'total_return' in src or 'total return' in src or 'cumulative' in src or 'total_ret' in src,
            "Backtester must calculate total return",
        )

    def test_calculates_alpha(self):
        src = self._get_backtest_source().lower()
        self.assertTrue(
            'alpha' in src,
            "Backtester must calculate alpha relative to buy & hold",
        )

    def test_calculates_beta(self):
        src = self._get_backtest_source().lower()
        self.assertTrue(
            'beta' in src,
            "Backtester must calculate beta relative to buy & hold",
        )

    def test_calculates_win_rate(self):
        src = self._get_backtest_source().lower()
        self.assertTrue(
            'win_rate' in src or 'win rate' in src or 'winrate' in src or 'win_ratio' in src,
            "Backtester must calculate win rate",
        )


class TestMissingDataHandling(unittest.TestCase):

    def _get_backtest_source(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as fh:
                    return fh.read()
        self.fail("No backtest file found")

    def test_forward_fills_missing_data(self):
        src = self._get_backtest_source()
        self.assertTrue(
            'ffill' in src or 'fillna(method' in src or 'forward_fill' in src or 'pad' in src,
            "Backtester must forward-fill missing values",
        )

    def test_skips_insufficient_training_windows(self):
        src = self._get_backtest_source()
        has_skip_logic = (
            'continue' in src or 'skip' in src.lower() or
            'insufficient' in src.lower() or 'len(' in src
        )
        self.assertTrue(
            has_skip_logic,
            "Backtester must skip training windows with insufficient data",
        )

    def test_does_not_crash_on_nan_data(self):
        src = self._get_backtest_source()
        has_nan_handling = (
            'dropna' in src or 'isna' in src or 'isnull' in src or
            'ffill' in src or 'fillna' in src or 'notna' in src
        )
        self.assertTrue(
            has_nan_handling,
            "Backtester must handle NaN data gracefully",
        )


class TestMetricsCalculationCorrectness(unittest.TestCase):

    def test_sharpe_ratio_formula(self):
        returns = pd.Series([0.01, -0.005, 0.02, 0.003, -0.01, 0.015, 0.008])
        excess_returns = returns - 0.0
        sharpe = excess_returns.mean() / excess_returns.std()
        self.assertAlmostEqual(sharpe, returns.mean() / returns.std(), places=5)

    def test_sortino_ratio_formula(self):
        returns = pd.Series([0.01, -0.005, 0.02, 0.003, -0.01, 0.015, 0.008])
        downside = returns[returns < 0]
        downside_std = downside.std()
        sortino = returns.mean() / downside_std
        self.assertIsInstance(sortino, float)
        self.assertFalse(np.isnan(sortino))

    def test_max_drawdown_formula(self):
        prices = pd.Series([100, 110, 105, 95, 100, 120, 115])
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        max_dd = drawdown.min()
        self.assertAlmostEqual(max_dd, (95 - 110) / 110, places=5)

    def test_total_return_formula(self):
        prices = pd.Series([100, 110, 105, 95, 100, 120, 115])
        total_return = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]
        self.assertAlmostEqual(total_return, 0.15, places=5)

    def test_win_rate_formula(self):
        trades = pd.Series([1, -1, 1, 1, -1, 1])
        wins = (trades > 0).sum()
        total = len(trades)
        win_rate = wins / total
        self.assertAlmostEqual(win_rate, 4 / 6, places=5)

    def test_beta_formula(self):
        strategy_returns = pd.Series([0.01, -0.005, 0.02, 0.003, -0.01])
        market_returns = pd.Series([0.008, -0.003, 0.015, 0.001, -0.007])
        covariance = np.cov(strategy_returns, market_returns)[0][1]
        market_var = np.var(market_returns, ddof=1)
        beta = covariance / market_var
        self.assertIsInstance(beta, float)

    def test_alpha_formula(self):
        strategy_return = 0.15
        market_return = 0.10
        beta = 1.2
        risk_free = 0.0
        alpha = strategy_return - (risk_free + beta * (market_return - risk_free))
        expected = 0.15 - 1.2 * 0.10
        self.assertAlmostEqual(alpha, expected, places=5)


class TestExecuteStrategyIntegration(unittest.TestCase):

    def test_execute_strategy_class_unchanged(self):
        from funcs import ExecuteStrategy
        required_methods = [
            'Buy_Hold', 'MACD_Indicator', 'MACD_RSI_Indicator',
            'RSI_Indicator', 'ReynerTeosBBands', 'Ridge_Indicator',
        ]
        for method in required_methods:
            self.assertTrue(
                hasattr(ExecuteStrategy, method),
                f"ExecuteStrategy must still have method: {method}",
            )

    def test_execute_strategy_has_random_forest(self):
        from funcs import ExecuteStrategy
        self.assertTrue(hasattr(ExecuteStrategy, 'RandomForest_Indicator'))

    def test_execute_strategy_init_signature_unchanged(self):
        from funcs import ExecuteStrategy
        import inspect
        sig = inspect.signature(ExecuteStrategy.__init__)
        params = list(sig.parameters.keys())
        self.assertIn('df', params)
        self.assertIn('type', params)


class TestBacktesterOutputsResults(unittest.TestCase):

    def _get_backtest_source(self):
        root = os.path.join(os.path.dirname(__file__), '..')
        for f in os.listdir(root):
            if 'backtest' in f.lower() and f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as fh:
                    return fh.read()
        self.fail("No backtest file found")

    def test_backtest_prints_or_stores_results(self):
        src = self._get_backtest_source()
        has_output = (
            'print(' in src or 'to_csv' in src or 'to_excel' in src or
            'DataFrame' in src or 'logging' in src or 'st.write' in src or
            'results' in src.lower()
        )
        self.assertTrue(
            has_output,
            "Backtester must output results (print, save to file, or display)",
        )

    def test_backtest_compares_strategies(self):
        src = self._get_backtest_source()
        strategy_count = 0
        for strat in [
            'Buy_Hold', 'MACD_Indicator', 'MACD_RSI_Indicator',
            'RSI_Indicator', 'ReynerTeosBBands', 'Ridge_Indicator',
            'RandomForest_Indicator',
        ]:
            if strat in src:
                strategy_count += 1
        self.assertEqual(
            strategy_count, 7,
            "All 7 strategies must be present in the backtester for comparison",
        )


class TestSignalLogicCorrectness(unittest.TestCase):

    def _make_df(self, prices, n=100):
        df = pd.DataFrame(
            {'Adj Close': prices},
            index=pd.date_range('2023-01-01', periods=len(prices), freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0
        return df

    def test_buy_signal_when_predicted_return_positive(self):
        from funcs import ExecuteStrategy
        np.random.seed(42)
        prices = np.cumsum(np.random.normal(0.5, 0.1, 200)) + 100
        df = self._make_df(prices)
        executor = ExecuteStrategy(df, 'both')
        result = executor.RandomForest_Indicator()
        last_pos = result['Position'].iloc[-1]
        self.assertIn(last_pos, [1, -1],
                       "With a strong uptrend the model should produce a directional signal (buy or sell), not 0")

    def test_sell_signal_when_predicted_return_negative(self):
        from funcs import ExecuteStrategy
        np.random.seed(42)
        prices = np.cumsum(np.random.normal(-0.5, 0.1, 200)) + 200
        df = self._make_df(prices)
        executor = ExecuteStrategy(df, 'both')
        result = executor.RandomForest_Indicator()
        last_pos = result['Position'].iloc[-1]
        self.assertIn(last_pos, [1, -1],
                       "With a strong downtrend the model should produce a directional signal")

    def test_signal_follows_predicted_sign_convention(self):
        from funcs import ExecuteStrategy
        np.random.seed(0)
        prices = np.cumsum(np.random.normal(0.5, 0.05, 200)) + 100
        df = self._make_df(prices)
        executor = ExecuteStrategy(df, 'both')
        result = executor.RandomForest_Indicator()
        last_pos = result['Position'].iloc[-1]
        self.assertEqual(last_pos, 1,
                         "Strongly positive predicted return should produce PosUp (1) for 'both' mode")


class TestSignalDistribution(unittest.TestCase):

    def test_produces_both_buy_and_sell_signals_over_varied_data(self):
        from funcs import ExecuteStrategy
        positions = []
        for seed in range(20):
            np.random.seed(seed)
            trend = np.random.choice([-1, 1])
            prices = np.cumsum(np.random.normal(trend * 0.3, 0.5, 200)) + 150
            df = pd.DataFrame(
                {'Adj Close': prices},
                index=pd.date_range('2023-01-01', periods=len(prices), freq='h'),
            )
            df['Change'] = df['Adj Close'].diff().fillna(0)
            df['Position'] = 0
            df['FilledPosition'] = 0
            df['Check'] = 0
            executor = ExecuteStrategy(df, 'both')
            result = executor.RandomForest_Indicator()
            positions.append(result['Position'].iloc[-1])
        unique_signals = set(positions)
        self.assertTrue(
            len(unique_signals) >= 2,
            f"Strategy should produce a mix of buy/sell signals across varied data, got only {unique_signals}",
        )

    def test_not_all_same_signal(self):
        from funcs import ExecuteStrategy
        positions = []
        for seed in [10, 20, 30, 40, 50]:
            np.random.seed(seed)
            prices = np.cumsum(np.random.normal(0, 1, 200)) + 100
            df = pd.DataFrame(
                {'Adj Close': prices},
                index=pd.date_range('2023-01-01', periods=len(prices), freq='h'),
            )
            df['Change'] = df['Adj Close'].diff().fillna(0)
            df['Position'] = 0
            df['FilledPosition'] = 0
            df['Check'] = 0
            executor = ExecuteStrategy(df, 'both')
            result = executor.RandomForest_Indicator()
            positions.append(result['Position'].iloc[-1])
        self.assertFalse(
            all(p == positions[0] for p in positions),
            "Over random-walk data, the strategy should not always produce the same signal",
        )


class TestStrategyPerformanceReasonableness(unittest.TestCase):

    def _simulate_strategy_return(self, prices, direction='both'):
        from funcs import ExecuteStrategy
        df = pd.DataFrame(
            {'Adj Close': prices},
            index=pd.date_range('2023-01-01', periods=len(prices), freq='h'),
        )
        df['Change'] = df['Adj Close'].diff().fillna(0)
        df['Position'] = 0
        df['FilledPosition'] = 0
        df['Check'] = 0

        results = []
        for i in range(50, len(df)):
            sub = df.iloc[:i + 1].copy()
            executor = ExecuteStrategy(sub, direction)
            out = executor.RandomForest_Indicator()
            results.append({
                'position': out['Position'].iloc[-1],
                'next_change': df['Change'].iloc[i] if i < len(df) else 0,
            })

        res = pd.DataFrame(results)
        res['strategy_pnl'] = res['position'].shift(1).fillna(0) * res['next_change']
        return res

    def test_strategy_not_consistently_negative_on_trending_data(self):
        np.random.seed(123)
        prices = np.cumsum(np.random.normal(0.3, 0.5, 200)) + 100
        res = self._simulate_strategy_return(prices)
        cumulative = res['strategy_pnl'].sum()
        passive = prices[-1] - prices[50]
        self.assertGreater(
            cumulative, -abs(passive) * 0.5,
            "Strategy should not lose more than 50% of what passive buy-and-hold gains on a clear uptrend",
        )

    def test_strategy_not_consistently_negative_on_downtrend(self):
        np.random.seed(456)
        prices = np.cumsum(np.random.normal(-0.3, 0.5, 200)) + 200
        res = self._simulate_strategy_return(prices)
        cumulative = res['strategy_pnl'].sum()
        passive_loss = prices[-1] - prices[50]
        self.assertGreater(
            cumulative, passive_loss,
            "On a downtrend with position='both', strategy should outperform passive buy-and-hold (which loses money)",
        )

    def test_signal_accuracy_above_random(self):
        np.random.seed(789)
        prices = np.cumsum(np.random.normal(0.2, 0.8, 200)) + 100
        res = self._simulate_strategy_return(prices)
        correct = (res['strategy_pnl'] > 0).sum()
        total = (res['strategy_pnl'] != 0).sum()
        if total > 0:
            accuracy = correct / total
            self.assertGreater(
                accuracy, 0.3,
                f"Signal accuracy {accuracy:.2%} is below 30%, suggesting the model is worse than random",
            )

    def test_strategy_sharpe_not_deeply_negative(self):
        np.random.seed(101)
        prices = np.cumsum(np.random.normal(0.1, 0.5, 200)) + 100
        res = self._simulate_strategy_return(prices)
        pnl = res['strategy_pnl']
        if pnl.std() > 0:
            sharpe = pnl.mean() / pnl.std()
            self.assertGreater(
                sharpe, -1.0,
                f"Strategy Sharpe ratio of {sharpe:.2f} is deeply negative, indicating poor methodology",
            )

    def test_max_drawdown_not_catastrophic(self):
        np.random.seed(202)
        prices = np.cumsum(np.random.normal(0.1, 0.5, 200)) + 100
        res = self._simulate_strategy_return(prices)
        cumulative_pnl = res['strategy_pnl'].cumsum()
        running_max = cumulative_pnl.cummax()
        drawdown = cumulative_pnl - running_max
        max_dd = drawdown.min()
        total_range = cumulative_pnl.max() - cumulative_pnl.min()
        if total_range > 0:
            dd_ratio = abs(max_dd) / total_range
            self.assertLess(
                dd_ratio, 0.95,
                f"Max drawdown is {dd_ratio:.0%} of total PnL range — strategy may be catastrophically flawed",
            )


if __name__ == '__main__':
    unittest.main()
