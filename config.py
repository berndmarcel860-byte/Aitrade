"""
Configuration settings for the AI BTC Trading Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Binance API Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Trading Configuration
SYMBOL = os.getenv('SYMBOL', 'BTCUSDT')
LEVERAGE = int(os.getenv('LEVERAGE', '10'))
POSITION_SIZE_USDT = float(os.getenv('POSITION_SIZE_USDT', '100'))
RISK_PERCENTAGE = float(os.getenv('RISK_PERCENTAGE', '2'))

# Technical Indicator Parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD = 2

EMA_SHORT = 9
EMA_MEDIUM = 21
EMA_LONG = 50

ATR_PERIOD = 14

# Trading Parameters
TIMEFRAME = '5m'  # 5-minute candles for scalping
CANDLE_LIMIT = 200  # Number of historical candles to fetch

# Signal Thresholds
MIN_VOLATILITY = 0.5  # Minimum ATR percentage for trade entry
MAX_SPREAD_PERCENTAGE = 0.1  # Maximum spread percentage allowed
