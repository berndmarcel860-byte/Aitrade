# 🤖 AI BTC Trading Bot - Binance Futures Scalping

A professional, AI-powered Bitcoin trading bot for Binance Futures with multiple technical indicators, trend analysis, and automated Telegram notifications.

## 🌟 Features

### Multi-Indicator Analysis
- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)**: Detects momentum and trend changes
- **Bollinger Bands**: Measures market volatility and price extremes
- **EMA (Exponential Moving Averages)**: Confirms trend direction with 9/21/50 periods
- **ATR (Average True Range)**: Calculates optimal position sizing based on volatility

### Intelligent Trading Decisions
- ✅ **Trend Detection**: Identifies UPTREND, DOWNTREND, or SIDEWAYS markets
- ✅ **Volatility Analysis**: Ensures suitable market conditions before trading
- ✅ **Long/Short Signals**: Multi-factor analysis for directional bias
- ✅ **Price Range Calculation**: Dynamic entry zones based on market conditions
- ✅ **Risk Management**: Automatic stop loss and multiple take profit targets
- ✅ **Risk/Reward Optimization**: Only trades with >1.5:1 risk-reward ratio

### Professional Signal Output
Sends beautifully formatted trading signals to Telegram including:
- 📊 Symbol name (BTC/USDT)
- 🎯 Direction (LONG/SHORT)
- ⚡ Leverage and margin information
- 💰 Entry price range
- 🎯 Multiple profit targets (TP1, TP2, TP3)
- 🛡️ Stop loss level
- 💵 Current market price
- 📈 Technical indicators (RSI, MACD, Volatility)
- 📊 Risk/Reward ratio

## 📋 Prerequisites

- Python 3.8 or higher
- Binance Futures account (for live trading)
- Telegram Bot Token (for notifications)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/berndmarcel860-byte/Aitrade.git
cd Aitrade
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Trading Configuration
SYMBOL=BTCUSDT
LEVERAGE=10
POSITION_SIZE_USDT=100
RISK_PERCENTAGE=2
```

### 4. Run the Bot

**Single Analysis Mode** (recommended for testing):
```bash
python trading_bot.py
```

**Continuous Monitoring Mode**:
Edit `trading_bot.py` and uncomment the continuous mode line:
```python
# In the main() function, replace:
bot.run_single_analysis()

# With:
bot.run_continuous(interval=60)  # Analyze every 60 seconds
```

## 📁 Project Structure

```
Aitrade/
├── trading_bot.py          # Main bot orchestrator
├── indicators.py           # Technical indicators calculations
├── strategy.py             # Trading strategy and signal generation
├── telegram_notifier.py    # Telegram message formatting and sending
├── config.py              # Configuration and parameters
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## ⚙️ Configuration

### Trading Parameters (in `config.py`)

```python
# Technical Indicators
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

EMA_SHORT = 9
EMA_MEDIUM = 21
EMA_LONG = 50

# Risk Management
MIN_VOLATILITY = 0.5  # Minimum ATR percentage for trading
```

## 🔐 Security Best Practices

1. **Never commit your `.env` file** - it contains sensitive API keys
2. **Use API keys with restricted permissions** - only enable Futures trading
3. **Enable IP whitelist** on Binance for additional security
4. **Start with small position sizes** to test the bot
5. **Use testnet first** before deploying to production

## 📊 Getting Binance API Keys

1. Log in to [Binance](https://www.binance.com)
2. Go to Profile → API Management
3. Create a new API key
4. Enable "Futures" permissions
5. Restrict to your IP address (recommended)
6. Save the API Key and Secret Key

## 🤖 Setting Up Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Save the Bot Token
5. Start a chat with your bot
6. Get your Chat ID:
   - Send a message to [@userinfobot](https://t.me/userinfobot)
   - Copy your Chat ID

## 📈 Trading Strategy Explained

### Signal Generation Logic

The bot uses a multi-factor scoring system:

1. **RSI Analysis**:
   - RSI < 30: Strong LONG signal (+2 points)
   - RSI < 45: Weak LONG signal (+1 point)
   - RSI > 70: Strong SHORT signal (+2 points)
   - RSI > 55: Weak SHORT signal (+1 point)

2. **MACD Analysis**:
   - Bullish crossover: LONG signal (+2 points)
   - Bearish crossover: SHORT signal (+2 points)

3. **Bollinger Bands**:
   - Price at lower band: LONG signal (+1 point)
   - Price at upper band: SHORT signal (+1 point)

4. **Trend Confirmation**:
   - UPTREND: LONG signal (+2 points)
   - DOWNTREND: SHORT signal (+2 points)

**Minimum 5 points required** for signal generation.

### Risk Management

- **Entry Range**: ±0.3-0.5 ATR from current price
- **Stop Loss**: 1.5 ATR from entry
- **Take Profit**: Multiple targets at 2x, 3x, and 4x ATR
- **Minimum R:R**: 1.5:1 ratio required

## 🛡️ Risk Disclaimer

**IMPORTANT**: This bot is for educational purposes only.

- Cryptocurrency trading involves substantial risk of loss
- Past performance does not guarantee future results
- Never invest more than you can afford to lose
- Always test with small amounts first
- The developers are not responsible for any financial losses
- Use at your own risk

## 🔧 Troubleshooting

### Bot shows "Demo Mode"
- Check that your `.env` file exists and has valid API keys
- Ensure API keys have Futures trading permissions

### No signals generated
- Market conditions may not meet criteria (low volatility, unclear trend)
- Adjust parameters in `config.py` if needed
- Wait for better market conditions

### Telegram messages not sending
- Verify your bot token is correct
- Ensure you've started a conversation with your bot
- Check that chat ID is correct

## 📝 Advanced Features (NEW!)

### ✅ Backtesting Module
- Evaluate strategies on historical data
- Calculate win rate, profit factor, Sharpe ratio
- Test multiple timeframes and symbols
- Usage: `python backtesting.py`

### ✅ Position Management
- Automatic position tracking
- Trailing stop loss functionality
- Partial exits at multiple TP levels
- Real-time P&L calculations
- Usage: See `position_manager.py`

### ✅ Advanced Trading Strategies
- **Scalping Strategy**: Quick profits with tight stops
- **Swing Trading**: Medium-term positions
- **Breakout Strategy**: Trade price breakouts
- **Mean Reversion**: Profit from price extremes
- Usage: Import from `advanced_strategies.py`

### ✅ Multi-Asset Trading
- Support for 10+ cryptocurrencies (BTC, ETH, BNB, ADA, DOGE, XRP, SOL, DOT, MATIC, LTC)
- Multiple timeframe analysis (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 1d)
- Scan all markets simultaneously
- Rank opportunities by score
- Usage: `python multi_asset_trader.py`

### ✅ Database Logging
- SQLite database for all signals and trades
- Track performance over time
- Export data to CSV
- Query historical data
- Usage: See `database_logger.py`

### ✅ Performance Analytics
- Comprehensive performance reports
- Daily/weekly/monthly summaries
- Strategy comparison analysis
- Risk metrics (drawdown, Sharpe ratio)
- Win rate by direction (LONG/SHORT)
- Performance grading (A-F)
- Usage: `python performance_analytics.py`

## 🚀 Advanced Usage

### Run Backtesting
```python
from backtesting import Backtester
from advanced_strategies import ScalpingStrategy

backtester = Backtester(strategy_class=ScalpingStrategy)
df = backtester.fetch_historical_data('BTCUSDT', '5m', '2024-01-01')
results = backtester.run_backtest(df, initial_capital=10000)
backtester.print_results(results)
```

### Manage Positions
```python
from position_manager import PositionManager

pm = PositionManager()
pm.open_position('BTCUSDT', signal)
pm.update_trailing_stop('BTCUSDT', current_price)
pm.close_position('BTCUSDT', exit_price, 'Take Profit 1', 50)
```

### Multi-Asset Scanning
```python
from multi_asset_trader import MultiAssetTrader

trader = MultiAssetTrader(
    symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
    timeframes=['5m', '15m', '1h']
)
opportunities = trader.analyze_best_opportunities()
trader.send_best_signals(limit=3)
```

### Analyze Performance
```python
from performance_analytics import PerformanceAnalytics

analytics = PerformanceAnalytics('trading_data.db')
analytics.print_performance_report(days=30)
analytics.print_daily_summary(days=7)
analytics.analyze_strategy_performance()
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 💬 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Happy Trading! 🚀📈**

*Remember: Always do your own research and never invest more than you can afford to lose.*