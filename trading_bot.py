"""
AI BTC Trading Bot for Binance Futures - Main Module
Professional scalping bot with multiple indicators and Telegram notifications
"""
import time
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import config
from indicators import TechnicalIndicators
from strategy import TradingStrategy
from telegram_notifier import TelegramNotifier


class BTCTradingBot:
    """Main trading bot class for Binance Futures scalping"""
    
    def __init__(self):
        """Initialize the trading bot"""
        print("🤖 Initializing AI BTC Trading Bot...")
        
        # Initialize Binance client
        if config.BINANCE_API_KEY and config.BINANCE_API_SECRET:
            try:
                self.client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
                # Test connection
                self.client.ping()
                print("✅ Connected to Binance API successfully!")
            except BinanceAPIException as e:
                print(f"❌ Binance API Error: {e}")
                self.client = None
        else:
            print("⚠️  Binance API credentials not found. Running in demo mode.")
            self.client = None
        
        # Initialize Telegram notifier
        self.telegram = TelegramNotifier()
        
        # Trading state
        self.last_signal_time = 0
        self.signal_cooldown = 300  # 5 minutes between signals
        
        print(f"📊 Trading Symbol: {config.SYMBOL}")
        print(f"⚡ Leverage: {config.LEVERAGE}x")
        print(f"💰 Position Size: ${config.POSITION_SIZE_USDT} USDT")
        print(f"⏱️  Timeframe: {config.TIMEFRAME}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def get_historical_data(self, symbol=None, interval=None, limit=None):
        """
        Fetch historical kline/candlestick data from Binance
        
        Args:
            symbol: Trading pair (default from config)
            interval: Timeframe (default from config)
            limit: Number of candles (default from config)
            
        Returns:
            DataFrame: OHLCV data
        """
        symbol = symbol or config.SYMBOL
        interval = interval or config.TIMEFRAME
        limit = limit or config.CANDLE_LIMIT
        
        try:
            if self.client:
                # Fetch from Binance API
                klines = self.client.futures_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
            else:
                # Demo mode - generate sample data
                print("⚠️  Demo mode: Using sample data")
                return self._generate_sample_data(limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to numeric types
            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            # Keep only necessary columns
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except BinanceAPIException as e:
            print(f"❌ Error fetching data from Binance: {e}")
            self.telegram.send_error_alert(f"Failed to fetch market data: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def _generate_sample_data(self, limit):
        """Generate sample OHLCV data for demo mode"""
        import numpy as np
        from datetime import datetime, timedelta
        
        base_price = 43000
        timestamps = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        current_time = int(time.time() * 1000)
        interval_ms = 5 * 60 * 1000  # 5 minutes in milliseconds
        
        for i in range(limit):
            timestamp = current_time - (limit - i) * interval_ms
            timestamps.append(timestamp)
            
            # Simulate price movement
            open_price = base_price + np.random.randn() * 200
            high_price = open_price + abs(np.random.randn()) * 150
            low_price = open_price - abs(np.random.randn()) * 150
            close_price = open_price + np.random.randn() * 100
            volume = abs(np.random.randn()) * 100
            
            opens.append(open_price)
            highs.append(high_price)
            lows.append(low_price)
            closes.append(close_price)
            volumes.append(volume)
            
            base_price = close_price
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes
        })
        
        return df
    
    def analyze_market(self):
        """
        Analyze current market conditions and generate signal
        
        Returns:
            dict: Trading signal or None
        """
        print("\n🔍 Analyzing market conditions...")
        
        # Fetch historical data
        df = self.get_historical_data()
        
        if df is None or len(df) < 50:
            print("❌ Insufficient data for analysis")
            return None
        
        # Create strategy instance and generate signal
        strategy = TradingStrategy(df)
        signal = strategy.generate_signal()
        
        if signal:
            print("✅ Trading signal generated!")
            print(f"   Direction: {signal['direction']}")
            print(f"   Trend: {signal['trend']}")
            print(f"   Current Price: ${signal['current_price']}")
            print(f"   Entry Range: ${signal['entry_range']}")
            print(f"   Stop Loss: ${signal['stop_loss']}")
            print(f"   Risk/Reward: {signal['risk_reward']['rr_ratio']}:1")
        else:
            print("⚠️  No valid trading signal at this time")
            print("   Waiting for better market conditions...")
        
        return signal
    
    def check_signal_cooldown(self):
        """
        Check if enough time has passed since last signal
        
        Returns:
            bool: True if can send signal, False otherwise
        """
        current_time = time.time()
        time_since_last = current_time - self.last_signal_time
        
        if time_since_last < self.signal_cooldown:
            remaining = int(self.signal_cooldown - time_since_last)
            print(f"⏳ Signal cooldown active. {remaining}s remaining...")
            return False
        
        return True
    
    def run_single_analysis(self):
        """Run a single market analysis and send signal if found"""
        print("\n" + "="*50)
        print(f"🔄 Running market analysis at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # Analyze market
        signal = self.analyze_market()
        
        if signal:
            # Check cooldown
            if not self.check_signal_cooldown():
                return
            
            # Send to Telegram
            print("\n📤 Sending signal to Telegram...")
            success = self.telegram.send_signal(signal, config.SYMBOL)
            
            if success or not self.telegram.bot:
                self.last_signal_time = time.time()
                print("✅ Signal processed successfully!")
        
        print("\n" + "="*50)
    
    def run_continuous(self, interval=60):
        """
        Run bot continuously with specified interval
        
        Args:
            interval: Time between analyses in seconds (default 60)
        """
        print(f"\n🚀 Starting continuous monitoring mode (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_single_analysis()
                print(f"⏰ Next analysis in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self.telegram.send_error_alert(f"Bot stopped due to error: {e}")


def main():
    """Main entry point"""
    print("\n" + "="*50)
    print("  🤖 AI BTC TRADING BOT - BINANCE FUTURES")
    print("  📈 Professional Scalping with Multi-Indicators")
    print("="*50 + "\n")
    
    # Create bot instance
    bot = BTCTradingBot()
    
    # Run single analysis (change to run_continuous for continuous mode)
    print("\n📊 Running single market analysis...")
    bot.run_single_analysis()
    
    print("\n💡 Tip: To run continuously, uncomment the line below in main()")
    print("   and comment out run_single_analysis()")
    print("\n   # bot.run_continuous(interval=60)  # Analyze every 60 seconds")
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
