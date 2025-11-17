# Quick Start Guide - AI BTC Trading Bot

## Installation & Setup (5 minutes)

### Step 1: Clone and Install
```bash
git clone https://github.com/berndmarcel860-byte/Aitrade.git
cd Aitrade
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

Required configuration in `.env`:
```env
# Optional - Leave empty for demo mode
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# Optional - Leave empty to print signals to console
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Trading settings
SYMBOL=BTCUSDT
LEVERAGE=10
POSITION_SIZE_USDT=100
RISK_PERCENTAGE=2
```

### Step 3: Run the Bot

**Option A: Single Analysis (Recommended for first run)**
```bash
python trading_bot.py
```

**Option B: Demo with Examples**
```bash
python example.py
```

**Option C: Continuous Monitoring**
Edit `trading_bot.py`, find the `main()` function and change:
```python
# From:
bot.run_single_analysis()

# To:
bot.run_continuous(interval=60)  # Analyze every 60 seconds
```

Then run:
```bash
python trading_bot.py
```

## Getting API Keys

### Binance API (Optional - for live data)
1. Login to [Binance](https://www.binance.com)
2. Go to Profile → API Management
3. Create New Key
4. Enable "Futures Trading" permission
5. Save API Key and Secret Key
6. Add to `.env` file

### Telegram Bot (Optional - for notifications)
1. Open Telegram, search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions, choose bot name
4. Copy the Bot Token
5. Send a message to [@userinfobot](https://t.me/userinfobot)
6. Copy your Chat ID
7. Add both to `.env` file

## Understanding Signals

The bot generates signals when multiple conditions align:

### Entry Criteria
- ✅ Volatility > 0.5% (ATR percentage)
- ✅ Risk/Reward ratio > 1.5:1
- ✅ 5+ indicator points in same direction
- ✅ Clear trend direction

### Signal Components
- **Direction**: LONG (buy) or SHORT (sell)
- **Entry Range**: Optimal price range to enter
- **Take Profit**: TP1 (50%), TP2 (30%), TP3 (20%)
- **Stop Loss**: Maximum loss level
- **Leverage**: Multiplier for position (default 10x)
- **Position Size**: Amount in USDT to trade

### Example Signal
```
🟢 LONG Signal
Current Price: $43,500
Entry: $43,250 - $43,600
TP1: $44,000 | TP2: $44,500 | TP3: $45,000
Stop Loss: $42,800
Leverage: 10x
Position: $100 USDT
Risk/Reward: 2.1:1
```

## Customization

### Adjust Trading Parameters
Edit `config.py`:
```python
# More conservative (fewer signals)
RSI_OVERSOLD = 25
RSI_OVERBOUGHT = 75
MIN_VOLATILITY = 0.8

# More aggressive (more signals)
RSI_OVERSOLD = 35
RSI_OVERBOUGHT = 65
MIN_VOLATILITY = 0.3
```

### Change Position Size
In `.env`:
```env
POSITION_SIZE_USDT=50    # Smaller position
LEVERAGE=5               # Lower leverage
```

### Adjust Timeframe
In `config.py`:
```python
TIMEFRAME = '15m'  # 15-minute candles
TIMEFRAME = '1h'   # 1-hour candles
```

## Safety Tips

⚠️ **IMPORTANT SAFETY RULES**

1. **Start Small**: Begin with $10-20 positions
2. **Use Demo Mode**: Test without API keys first
3. **Manual Execution**: Review signals before trading
4. **Set Limits**: Never risk more than 1-2% per trade
5. **Use Stop Loss**: Always set stop loss orders
6. **Test Period**: Run for 1-2 weeks before increasing size

## Troubleshooting

### "No signals generated"
- ✅ Normal behavior - bot is selective
- ✅ Wait for better market conditions
- ✅ Check minimum volatility setting

### "Demo mode" message
- ✅ Binance API keys not configured
- ✅ Check `.env` file exists
- ✅ Verify API key format

### "Telegram not sending"
- ✅ Check bot token is correct
- ✅ Ensure you messaged the bot first
- ✅ Verify chat ID is correct

### Import errors
```bash
pip install --upgrade -r requirements.txt
```

## Advanced Usage

### Run on Server (24/7)
```bash
# Using screen
screen -S trading_bot
python trading_bot.py
# Press Ctrl+A, then D to detach

# Reattach later
screen -r trading_bot
```

### Run on VPS
```bash
# Using nohup
nohup python trading_bot.py > bot.log 2>&1 &

# Check logs
tail -f bot.log
```

### Schedule Regular Checks
```bash
# Add to crontab
crontab -e

# Run every hour
0 * * * * cd /path/to/Aitrade && python trading_bot.py >> bot.log 2>&1
```

## Support

- 📖 Full documentation: See `README.md`
- 🐛 Report issues: GitHub Issues
- 💬 Questions: GitHub Discussions

## Disclaimer

This bot is for educational purposes. Cryptocurrency trading is risky. Never invest more than you can afford to lose. Always do your own research.

---
Happy Trading! 🚀📈
