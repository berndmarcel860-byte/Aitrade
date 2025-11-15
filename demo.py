"""
Demo script to showcase the bot with favorable market conditions
"""
import pandas as pd
import numpy as np
from indicators import TechnicalIndicators
from strategy import TradingStrategy
from telegram_notifier import TelegramNotifier
import config


def generate_favorable_market_data():
    """Generate sample data that should produce a trading signal"""
    # Create 200 candles with a clear uptrend
    timestamps = list(range(200))
    base_price = 40000
    
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
    # Generate uptrend with some volatility
    for i in range(200):
        # Gradually increase price
        trend = i * 30  # Upward trend
        noise = np.random.randn() * 50
        
        open_price = base_price + trend + noise
        high_price = open_price + abs(np.random.randn()) * 100
        low_price = open_price - abs(np.random.randn()) * 80
        close_price = open_price + np.random.randn() * 60 + 20  # Slight upward bias
        volume = abs(np.random.randn()) * 100
        
        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)
        volumes.append(volume)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })
    
    return df


def main():
    """Demo the trading bot functionality"""
    print("\n" + "="*60)
    print("  🎯 TRADING BOT DEMO - FAVORABLE MARKET CONDITIONS")
    print("="*60 + "\n")
    
    print("📊 Generating sample market data with clear uptrend...\n")
    
    # Generate favorable data
    df = generate_favorable_market_data()
    
    print(f"✅ Generated {len(df)} candles")
    print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"   Current price: ${df['close'].iloc[-1]:.2f}\n")
    
    # Create indicators
    print("📈 Calculating technical indicators...")
    indicators = TechnicalIndicators(df)
    indicator_values = indicators.get_all_indicators()
    
    print(f"   ✓ RSI: {indicator_values['rsi']:.2f}")
    print(f"   ✓ MACD: {indicator_values['macd']['macd']:.2f}")
    print(f"   ✓ ATR: {indicator_values['atr']['atr']:.2f} ({indicator_values['atr']['atr_percentage']:.2f}%)")
    print(f"   ✓ EMA Short: {indicator_values['ema']['short']:.2f}")
    print(f"   ✓ EMA Medium: {indicator_values['ema']['medium']:.2f}")
    print(f"   ✓ EMA Long: {indicator_values['ema']['long']:.2f}\n")
    
    # Create strategy
    print("🎯 Analyzing trading strategy...")
    strategy = TradingStrategy(df)
    
    # Check components
    trend = strategy.check_trend()
    volatility = strategy.check_volatility()
    direction = strategy.check_direction()
    
    print(f"   ✓ Trend: {trend}")
    print(f"   ✓ Volatility: {volatility['status']} ({volatility['atr_percentage']:.2f}%)")
    print(f"   ✓ Direction: {direction}\n")
    
    # Generate signal
    print("🚀 Generating trading signal...")
    signal = strategy.generate_signal()
    
    if signal:
        print("✅ TRADING SIGNAL GENERATED!\n")
        print("="*60)
        
        # Display signal details
        print(f"📊 Symbol: {config.SYMBOL}")
        print(f"🎯 Direction: {signal['direction']}")
        print(f"📈 Trend: {signal['trend']}")
        print(f"💵 Current Price: ${signal['current_price']}")
        print(f"🎯 Entry Range: ${signal['entry_range']}")
        print(f"💰 Take Profit: {signal['take_profit']}")
        print(f"🛡️  Stop Loss: ${signal['stop_loss']}")
        print(f"⚡ Leverage: {signal['leverage']}x")
        print(f"💼 Position Size: ${signal['position_size']} USDT")
        print(f"📊 Risk/Reward: {signal['risk_reward']['rr_ratio']}:1")
        print("\n" + "="*60 + "\n")
        
        # Format Telegram message
        print("📱 TELEGRAM MESSAGE FORMAT:\n")
        print("="*60)
        telegram = TelegramNotifier()
        message = telegram.format_signal_message(signal, config.SYMBOL)
        print(message)
        print("="*60)
        
    else:
        print("⚠️  No signal generated (market conditions not favorable)")
        print("   This is normal - the bot is selective about trades")
    
    print("\n✅ Demo complete!")
    print("\n💡 To run with real market data:")
    print("   1. Add your Binance API keys to .env file")
    print("   2. Add your Telegram bot token to .env file")
    print("   3. Run: python trading_bot.py")


if __name__ == "__main__":
    main()
