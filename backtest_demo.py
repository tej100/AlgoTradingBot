import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from funcs import ExecuteStrategy
from datetime import datetime

warnings.filterwarnings('ignore')

class WalkForwardBacktester:
    def __init__(self, ticker, interval, position='both', period='60d'):
        self.ticker = ticker
        self.interval = interval
        self.position = position
        self.period = period
        self.data = None
        self.strategies = ["Buy_Hold", "MACD_Indicator", "MACD_RSI_Indicator", 
                          "RSI_Indicator", "ReynerTeosBBands", "Ridge_Indicator", 
                          "RandomForest_Indicator"]
        
    def download_data(self):
        print(f"Downloading data for {self.ticker} at {self.interval} interval...")
        try:
            data = yf.download(self.ticker, period=self.period, interval=self.interval, 
                             progress=False, multi_level_index=False)
            if data.empty:
                raise ValueError(f"No data downloaded for {self.ticker}")
            
            data = data[['Close']].copy()
            data = data.ffill()
            data = data.dropna()
            
            print(f"Downloaded {len(data)} data points from {data.index[0]} to {data.index[-1]}")
            self.data = data
            return data
        except Exception as e:
            print(f"Error downloading data: {e}")
            return None
    
    def calculate_metrics(self, returns, benchmark_returns, strategy_name):
        if len(returns) == 0 or returns.sum() == 0:
            return {
                'strategy': strategy_name,
                'total_return': 0.0,
                'sharpe_ratio': 0.0,
                'sortino_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'alpha': 0.0,
                'beta': 0.0,
                'num_trades': 0
            }
        
        cumulative_returns = (1 + returns).cumprod()
        total_return = (cumulative_returns.iloc[-1] - 1) * 100 if len(cumulative_returns) > 0 else 0
        
        mean_return = returns.mean()
        std_return = returns.std()
        
        periods_per_year = self._get_periods_per_year()
        sharpe_ratio = (mean_return * periods_per_year) / (std_return * np.sqrt(periods_per_year)) if std_return > 0 else 0
        
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()
        sortino_ratio = (mean_return * periods_per_year) / (downside_std * np.sqrt(periods_per_year)) if downside_std > 0 else 0
        
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        winning_trades = (returns > 0).sum()
        total_trades = (returns != 0).sum()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        if len(benchmark_returns) > 0 and benchmark_returns.std() > 0:
            covariance = np.cov(returns, benchmark_returns)[0][1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            alpha = (mean_return - beta * benchmark_returns.mean()) * periods_per_year * 100
        else:
            alpha = 0
            beta = 0
        
        return {
            'strategy': strategy_name,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'alpha': alpha,
            'beta': beta,
            'num_trades': total_trades
        }
    
    def _get_periods_per_year(self):
        interval_map = {
            '1m': 252 * 390,
            '5m': 252 * 78,
            '15m': 252 * 26,
            '30m': 252 * 13,
            '1h': 252 * 6.5,
            '2h': 252 * 3.25,
            '3h': 252 * 2.17,
            '6h': 252 * 1.08,
            '12h': 252 * 0.54,
            '1d': 252,
            '1wk': 52,
            '1mo': 12
        }
        return interval_map.get(self.interval, 252)
    
    def run_walk_forward_backtest(self, strategy_name, min_train_size=100, retrain_frequency=50):
        if self.data is None:
            print("No data available. Please download data first.")
            return None
        
        print(f"\nBacktesting {strategy_name}...", end='', flush=True)
        
        data = self.data.copy()
        data['Change'] = data['Close'].diff()
        data['Position'] = 0
        data['FilledPosition'] = 0
        data['Check'] = 0
        
        positions = []
        
        start_idx = min_train_size
        retrains = 0
        
        for i in range(start_idx, len(data)):
            if i == start_idx or (i - start_idx) % retrain_frequency == 0 or i == len(data) - 1:
                
                if retrains > 0 and retrains % 10 == 0:
                    print('.', end='', flush=True)
                
                train_data = data.iloc[:i+1].copy()
                
                if len(train_data) < min_train_size:
                    positions.append(0)
                    continue
                
                try:
                    executor = ExecuteStrategy(train_data, self.position)
                    strategy_method = getattr(executor, strategy_name)
                    result = strategy_method()
                    position = result['Position'].iloc[-1]
                    positions.append(position)
                    retrains += 1
                except Exception as e:
                    positions.append(0 if i == 0 or len(positions) == 0 else positions[-1])
            else:
                positions.append(positions[-1] if len(positions) > 0 else 0)
        
        padding = [0] * start_idx
        all_positions = padding + positions
        
        data['Position'] = all_positions[:len(data)]
        
        data['Strategy_Returns'] = data['Close'].pct_change() * data['Position'].shift(1)
        data['Buy_Hold_Returns'] = data['Close'].pct_change()
        
        unique_positions = data['Position'].unique()
        print(f" Positions: {unique_positions}", end='', flush=True)
        
        data = data.iloc[start_idx:]
        
        strategy_returns = data['Strategy_Returns'].dropna()
        benchmark_returns = data['Buy_Hold_Returns'].dropna()
        
        metrics = self.calculate_metrics(strategy_returns, benchmark_returns, strategy_name)
        print(f" Done! ({retrains} retrains)")
        
        return metrics, data
    
    def run_all_strategies(self):
        if self.data is None:
            self.download_data()
        
        if self.data is None:
            print("Failed to download data. Exiting.")
            return None
        
        results = []
        all_data = {}
        
        for strategy in self.strategies:
            try:
                metrics, data = self.run_walk_forward_backtest(strategy)
                if metrics:
                    results.append(metrics)
                    all_data[strategy] = data
            except Exception as e:
                print(f"Error running {strategy}: {e}")
                continue
        
        results_df = pd.DataFrame(results)
        
        return results_df, all_data
    
    def print_results(self, results_df):
        print("\n" + "="*100)
        print(f"BACKTESTING RESULTS - {self.ticker} - {self.interval} interval - Position: {self.position}")
        print("="*100)
        
        if results_df is None or len(results_df) == 0:
            print("No results to display.")
            return
        
        print(f"\n{'Strategy':<25} {'Total Return':<15} {'Sharpe':<10} {'Sortino':<10} {'Max DD':<12} {'Win Rate':<12} {'Alpha':<10} {'Beta':<8} {'Trades':<8}")
        print("-"*100)
        
        for _, row in results_df.iterrows():
            print(f"{row['strategy']:<25} {row['total_return']:>13.2f}% {row['sharpe_ratio']:>9.2f} {row['sortino_ratio']:>9.2f} {row['max_drawdown']:>10.2f}% {row['win_rate']:>10.2f}% {row['alpha']:>9.2f} {row['beta']:>7.2f} {int(row['num_trades']):>7}")
        
        print("\n" + "="*100)
        best_strategy = results_df.loc[results_df['total_return'].idxmax(), 'strategy']
        best_return = results_df.loc[results_df['total_return'].idxmax(), 'total_return']
        print(f"Best Strategy: {best_strategy} with {best_return:.2f}% total return")
        print("="*100 + "\n")
        
        results_df.to_csv(f'backtest_results_{self.ticker}_{self.interval}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', index=False)
        print(f"Results saved to CSV file.")


if __name__ == "__main__":
    print("Starting Backtesting Demo (60-day dataset)...")
    print("="*100)
    print("NOTE: For full 'max' period backtest on BTC-USD 5m interval, use backtest.py")
    print("      (Warning: Full backtest may take 30+ minutes due to walk-forward retraining)")
    print("="*100)
    
    backtester = WalkForwardBacktester(
        ticker='BTC-USD',
        interval='1h',
        position='both',
        period='60d'
    )
    
    results_df, all_data = backtester.run_all_strategies()
    
    backtester.print_results(results_df)
    
    print("\nBacktesting demo completed!")
    print("\nKey Features Implemented:")
    print("  ✓ RandomForest_Indicator strategy (following Ridge_Indicator structure)")
    print("  ✓ Walk-forward validation (retrains model on each new window)")
    print("  ✓ Manual performance metrics (Sharpe, Sortino, max drawdown, etc.)")
    print("  ✓ Forward-fill for missing data")
    print("  ✓ Identical date ranges for all strategies")
    print("  ✓ No external backtesting libraries")
