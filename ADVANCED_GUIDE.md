# Advanced Features Guide

## 🚀 Overview

This guide covers all the advanced features added to the AI BTC Trading Bot, including backtesting, position management, multiple strategies, database logging, and performance analytics.

## 📋 Table of Contents

1. [Backtesting](#backtesting)
2. [Position Management](#position-management)
3. [Advanced Strategies](#advanced-strategies)
4. [Multi-Asset Trading](#multi-asset-trading)
5. [Database Logging](#database-logging)
6. [Performance Analytics](#performance-analytics)
7. [Advanced Bot Integration](#advanced-bot-integration)

---

## 1. Backtesting

Test your trading strategies on historical data before risking real capital.

### Features:
- Load historical data from Binance or use generated data
- Test any strategy (default or advanced)
- Calculate comprehensive metrics:
  - Win rate, profit factor
  - Sharpe ratio, max drawdown
  - Average win/loss amounts
  - Total return percentage

### Usage:

```python
from backtesting import Backtester
from advanced_strategies import ScalpingStrategy

# Initialize backtester
backtester = Backtester(strategy_class=ScalpingStrategy)

# Fetch historical data
df = backtester.fetch_historical_data(
    symbol='BTCUSDT',
    interval='5m',
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# Run backtest
results = backtester.run_backtest(
    df, 
    initial_capital=10000,
    position_size_pct=0.1
)

# Print results
backtester.print_results(results)
```

### Run directly:
```bash
python backtesting.py
```

---

## 2. Position Management

Automatically track and manage open positions with trailing stops and partial exits.

### Features:
- Open/close positions
- Automatic trailing stop loss
- Partial exits at TP1 (50%), TP2 (30%), TP3 (20%)
- Real-time P&L calculations
- Position history tracking
- Trading statistics

### Usage:

```python
from position_manager import PositionManager

# Initialize
pm = PositionManager()

# Open position
signal = {
    'direction': 'LONG',
    'current_price': 43500,
    'stop_loss': 42800,
    'take_profit': 'TP1: 44000 | TP2: 44500 | TP3: 45000',
    'leverage': 10
}
pm.open_position('BTCUSDT', signal)

# Update trailing stop
pm.update_trailing_stop('BTCUSDT', 43800)

# Check exit conditions
should_exit, reason, pct = pm.check_exit_conditions('BTCUSDT', 44000)
if should_exit:
    pm.close_position('BTCUSDT', 44000, reason, pct)

# Get statistics
stats = pm.get_statistics()
print(f"Win Rate: {stats['win_rate']:.2f}%")
```

---

## 3. Advanced Strategies

Four professional trading strategies for different market conditions.

### Scalping Strategy
- **Focus**: Quick profits, short holding periods
- **Targets**: 1-2x ATR
- **Stop Loss**: 1x ATR (tight)
- **Best for**: High volatility, 1m-5m timeframes

```python
from advanced_strategies import ScalpingStrategy

strategy = ScalpingStrategy(df)
signal = strategy.generate_signal()
```

### Swing Trading Strategy
- **Focus**: Medium-term positions (days)
- **Targets**: 3-7x ATR
- **Stop Loss**: 2.5x ATR
- **Best for**: Strong trends, 1h-4h timeframes

```python
from advanced_strategies import SwingStrategy

strategy = SwingStrategy(df)
signal = strategy.generate_signal()
```

### Breakout Strategy
- **Focus**: Trade price breakouts
- **Targets**: 2.5-6x ATR
- **Stop Loss**: 1.5x ATR
- **Best for**: Consolidation breakouts

```python
from advanced_strategies import BreakoutStrategy

strategy = BreakoutStrategy(df)
signal = strategy.generate_signal()
```

### Mean Reversion Strategy
- **Focus**: Profit from price extremes
- **Targets**: Reversion to mean (BB middle)
- **Stop Loss**: Beyond BB bands
- **Best for**: Ranging markets

```python
from advanced_strategies import MeanReversionStrategy

strategy = MeanReversionStrategy(df)
signal = strategy.generate_signal()
```

---

## 4. Multi-Asset Trading

Trade multiple cryptocurrencies across different timeframes simultaneously.

### Supported Assets:
- BTC, ETH, BNB, ADA, DOGE
- XRP, SOL, DOT, MATIC, LTC

### Supported Timeframes:
- 1m, 3m, 5m, 15m, 30m
- 1h, 2h, 4h, 1d

### Usage:

```python
from multi_asset_trader import MultiAssetTrader

# Initialize
trader = MultiAssetTrader(
    symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
    timeframes=['5m', '15m', '1h']
)

# Market overview
trader.print_market_overview()

# Scan for opportunities
opportunities = trader.analyze_best_opportunities()

# Send best signals to Telegram
trader.send_best_signals(limit=3)

# Run directly
python multi_asset_trader.py
```

---

## 5. Database Logging

SQLite database for persistent storage of signals and trades.

### Features:
- Log all signals with indicators
- Track open and closed trades
- Daily performance calculations
- Export to CSV
- Query historical data

### Usage:

```python
from database_logger import DatabaseLogger

# Initialize
db = DatabaseLogger('trading_data.db')

# Log signal
signal_id = db.log_signal(signal, 'BTCUSDT')

# Log trade opening
trade_id = db.log_trade_open(
    signal_id, 'BTCUSDT', 'LONG', 43500, 0.002, 10
)

# Log trade closing
db.log_trade_close(
    trade_id, 44000, 'Take Profit 1', 115, 2.65
)

# Get recent signals
recent = db.get_recent_signals(limit=10)

# Export to CSV
db.export_to_csv('signals', 'signals_export.csv')

# Print statistics
db.print_statistics()
```

---

## 6. Performance Analytics

Comprehensive analysis of trading performance with detailed reports.

### Metrics Calculated:
- Total trades, win rate
- Total P&L, average win/loss
- Profit factor, expectancy
- Max drawdown, Sharpe ratio
- Consecutive wins/losses
- Performance by direction (LONG/SHORT)
- Strategy comparison

### Usage:

```python
from performance_analytics import PerformanceAnalytics

# Initialize
analytics = PerformanceAnalytics('trading_data.db')

# Print 30-day report
analytics.print_performance_report(days=30)

# Daily summary
analytics.print_daily_summary(days=7)

# Strategy comparison
analytics.analyze_strategy_performance()

# Export report
analytics.export_report('report.txt', days=30)

# Run directly
python performance_analytics.py
```

### Performance Grading:
- **A+ (85-100)**: Excellent
- **A (75-84)**: Very Good
- **B (65-74)**: Good
- **C (55-64)**: Average
- **D (45-54)**: Below Average
- **F (<45)**: Poor

---

## 7. Advanced Bot Integration

Combines all features into one comprehensive trading system.

### Features:
- Multiple strategies running simultaneously
- Multi-asset scanning
- Automatic position management
- Database logging
- Performance reporting
- Signal scoring and ranking

### Running Modes:

**Mode 1: Single Analysis**
```bash
python advanced_bot.py
# Select: 1
```
- Scan all markets with all strategies
- Rank opportunities
- Send top 3 signals to Telegram
- One-time execution

**Mode 2: Continuous Trading**
```bash
python advanced_bot.py
# Select: 2
```
- Run analysis every 5 minutes
- Manage open positions
- Generate reports every 10 cycles
- Press Ctrl+C to stop

**Mode 3: Backtest All Strategies**
```bash
python advanced_bot.py
# Select: 3
```
- Test all 4 strategies
- Compare performance
- Find best strategy

**Mode 4: Performance Report**
```bash
python advanced_bot.py
# Select: 4
```
- Generate comprehensive report
- Display statistics
- Export to file

### Programmatic Usage:

```python
from advanced_bot import AdvancedTradingBot

# Initialize
bot = AdvancedTradingBot(
    symbols=['BTCUSDT', 'ETHUSDT'],
    strategies={
        'Scalping': ScalpingStrategy,
        'Swing': SwingStrategy
    }
)

# Single analysis
signals = bot.run_complete_analysis()

# Manage positions
bot.monitor_and_manage_positions()

# Generate report
bot.generate_performance_report()

# Continuous mode
bot.run_continuous_mode(interval=300)

# Backtest all
bot.run_backtest_all_strategies(days=30)
```

---

## 🎯 Best Practices

### 1. Start with Backtesting
Always backtest strategies before using them live:
```bash
python advanced_bot.py
# Select mode 3 (Backtest)
```

### 2. Use Database Logging
Enable database logging for all live trading:
```python
from database_logger import DatabaseLogger
db = DatabaseLogger('trading_data.db')
```

### 3. Monitor Positions
Always use position manager for live trades:
```python
from position_manager import PositionManager
pm = PositionManager()
```

### 4. Regular Performance Reviews
Review performance weekly:
```python
from performance_analytics import PerformanceAnalytics
analytics = PerformanceAnalytics()
analytics.print_performance_report(days=7)
```

### 5. Diversify Strategies
Use multiple strategies across different timeframes:
```python
trader = MultiAssetTrader(
    symbols=['BTCUSDT', 'ETHUSDT'],
    timeframes=['5m', '15m', '1h']
)
```

---

## 📊 Example Workflow

### Complete Trading Session:

```python
from advanced_bot import AdvancedTradingBot
from advanced_strategies import *

# 1. Initialize bot
bot = AdvancedTradingBot(
    symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
    strategies={
        'Scalping': ScalpingStrategy,
        'Swing': SwingStrategy,
        'Breakout': BreakoutStrategy,
        'Mean Reversion': MeanReversionStrategy
    }
)

# 2. Run analysis
signals = bot.run_complete_analysis()

# 3. Manage positions
bot.monitor_and_manage_positions()

# 4. Generate report (optional)
if len(bot.position_manager.position_history) > 10:
    bot.generate_performance_report()
```

### Or simply run:
```bash
python advanced_bot.py
```

---

## 🆘 Troubleshooting

### Database locked error
```python
# Close database before opening again
db.close()
```

### No signals found
- Market conditions may not be suitable
- Try different timeframes
- Adjust strategy parameters

### Position not closing
- Check price feed is updating
- Verify exit conditions are correct
- Use manual close if needed:
```python
pm.close_position(symbol, price, 'Manual Close', 100)
```

---

## 📚 Additional Resources

- See `README.md` for core features
- See `QUICKSTART.md` for setup
- See `FEATURES.md` for detailed feature list
- See `SAMPLE_OUTPUT.md` for example outputs

---

**Happy Trading! 🚀📈**
