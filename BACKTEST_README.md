# Backtesting System Documentation

## Overview

This backtesting system implements walk-forward validation to test multiple trading strategies on historical cryptocurrency data. All performance metrics are calculated manually without using external backtesting libraries.

## Features

✓ **RandomForest_Indicator Strategy**: Machine learning-based strategy using Random Forest regression to predict price movements  
✓ **Walk-Forward Validation**: Models are retrained on expanding windows rather than fitting once on all historical data  
✓ **Manual Performance Metrics**: Sharpe ratio, Sortino ratio, max drawdown, total return, alpha/beta, and win rate calculated from scratch  
✓ **Data Handling**: Forward-fill for missing values, graceful handling of insufficient data windows  
✓ **Fair Comparison**: All strategies tested on identical date ranges  
✓ **No External Libraries**: No backtesting frameworks used - all calculations done manually  

## Files

- `backtest.py` - Full backtesting script for maximum historical data (can be slow)
- `backtest_demo.py` - Demo script using 60-day data for faster testing
- `backtest_quick_test.py` - Quick verification that all strategies work correctly
- `funcs.py` - Strategy implementations and helper functions

## Strategies Tested

1. **Buy_Hold** - Passive buy and hold strategy
2. **MACD_Indicator** - Moving Average Convergence Divergence indicator
3. **MACD_RSI_Indicator** - Combined MACD and RSI indicator
4. **RSI_Indicator** - Relative Strength Index indicator
5. **ReynerTeosBBands** - Bollinger Bands with trend filter
6. **Ridge_Indicator** - Ridge regression model for price prediction
7. **RandomForest_Indicator** - Random Forest model for price prediction (NEW)

## Usage

### Quick Test (5 seconds)
```bash
python3 backtest_quick_test.py
```
Verifies all strategies work correctly on recent data.

### Demo Backtest (2-3 minutes)
```bash
python3 backtest_demo.py
```
Runs full backtesting on 60 days of BTC-USD data at 1h interval.

### Full Backtest (30+ minutes)
```bash
python3 backtest.py
```
Runs backtesting on maximum available BTC-USD data at 5m interval as specified in problem.txt.

## Performance Metrics

### Total Return
Cumulative percentage return over the testing period.

### Sharpe Ratio
Risk-adjusted return measure: (mean return × periods per year) / (std return × √periods per year)

### Sortino Ratio
Similar to Sharpe but only penalizes downside volatility.

### Maximum Drawdown
Largest peak-to-trough decline in cumulative returns.

### Win Rate
Percentage of trades that were profitable.

### Alpha
Excess return relative to buy-and-hold strategy.

### Beta
Correlation to buy-and-hold strategy returns.

## Walk-Forward Validation

The backtesting system uses walk-forward validation to prevent look-ahead bias:

1. Start with minimum training window (e.g., 100 data points)
2. Train model on all data up to current point
3. Generate prediction for next period
4. Move forward in time
5. Retrain model every N periods (retrain_frequency)
6. Repeat until end of data

This ensures the model only uses information that would have been available at each point in time.

## RandomForest_Indicator Strategy

The RandomForest_Indicator follows the same structure as Ridge_Indicator:

- Uses log returns as features
- Creates window-based features (default: 7 periods)
- Trains a Random Forest regression model (50 estimators, max depth 8)
- Predicts next period's returns
- Takes long position if predicted return is positive
- Takes short position if predicted return is negative

### Model Parameters
- `n_estimators`: 50 (reduced from 100 for faster training)
- `max_depth`: 8 (prevents overfitting)
- `max_samples`: 0.8 (uses 80% of training data per tree)
- `n_jobs`: -1 (parallel processing)

## Integration with Frontend

The RandomForest_Indicator has been added to the Streamlit frontend (`app.py`) and is now selectable alongside existing strategies in the dropdown menu.

## Sample Output

```
====================================================================================================
BACKTESTING RESULTS - BTC-USD - 1h interval - Position: both
====================================================================================================

Strategy                  Total Return    Sharpe     Sortino    Max DD       Win Rate     Alpha      Beta     Trades  
----------------------------------------------------------------------------------------------------
Buy_Hold                          14.93%      0.95      1.39     -13.25%      49.36%     -0.21    1.00    1319
MACD_Indicator                    11.17%      0.75      1.11     -16.94%      50.57%     13.36    0.09    1319
MACD_RSI_Indicator                19.86%      1.58      1.62      -9.62%      53.19%     27.00   -0.17     769
RSI_Indicator                      0.46%      0.13      0.05      -3.21%      48.00%      0.10    0.03     100
ReynerTeosBBands                   0.00%      0.00      0.00       0.00%       0.00%      0.00    0.00       0
Ridge_Indicator                   27.40%      1.59      2.21     -10.51%      51.48%     20.68    0.58    1319
RandomForest_Indicator            -7.13%     -0.35     -0.50     -17.95%      49.13%     -7.70    0.03    1319

====================================================================================================
Best Strategy: Ridge_Indicator with 27.40% total return
====================================================================================================
```

Results are automatically saved to a CSV file with timestamp.

## Notes

- The full backtest on BTC-USD 5m interval with max data may take 30+ minutes due to frequent model retraining
- Machine learning strategies (Ridge, RandomForest) are slower than technical indicator strategies
- Model hyperparameters have been optimized for reasonable training time while maintaining performance
- All strategies handle missing data via forward-fill
- Insufficient data windows are skipped rather than causing crashes

## Troubleshooting

**Issue**: Strategies show 0% returns  
**Solution**: This was fixed by updating pandas indexing from `df.Position[-1]` to `df.loc[df.index[-1], 'Position']` to work with copy-on-write mode.

**Issue**: Backtest takes too long  
**Solution**: Use `backtest_demo.py` instead of `backtest.py`, or adjust `retrain_frequency` parameter to retrain less often.

**Issue**: Out of memory  
**Solution**: Reduce the data period or increase `retrain_frequency` to reduce memory usage.
