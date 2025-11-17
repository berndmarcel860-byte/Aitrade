"""
Enhanced demo with guaranteed signal generation
"""
import pandas as pd
import numpy as np
from indicators import TechnicalIndicators
from strategy import TradingStrategy
from telegram_notifier import TelegramNotifier
import config


def generate_signal_ready_data(direction='LONG'):
    """
    Generate market data that should produce a clear trading signal
    
    Args:
        direction: 'LONG' or 'SHORT'
    """
    timestamps = list(range(200))
    
    if direction == 'LONG':
        # Create oversold bounce scenario
        base_price = 42000
        
        # First 150 candles: downtrend (creating oversold conditions)
        closes = []
        for i in range(150):
            price = base_price - (i * 15) + np.random.randn() * 30
            closes.append(price)
        
        # Last 50 candles: reversal uptrend
        for i in range(50):
            price = closes[-1] + (i * 25) + np.random.randn() * 40
            closes.append(price)
    else:
        # Create overbought rejection scenario
        base_price = 42000
        
        # First 150 candles: uptrend (creating overbought conditions)
        closes = []
        for i in range(150):
            price = base_price + (i * 15) + np.random.randn() * 30
            closes.append(price)
        
        # Last 50 candles: reversal downtrend
        for i in range(50):
            price = closes[-1] - (i * 25) + np.random.randn() * 40
            closes.append(price)
    
    # Generate OHLV from closes
    opens = []
    highs = []
    lows = []
    volumes = []
    
    for close in closes:
        open_price = close + np.random.randn() * 50
        high_price = max(open_price, close) + abs(np.random.randn()) * 80
        low_price = min(open_price, close) - abs(np.random.randn()) * 80
        volume = abs(np.random.randn()) * 150 + 50
        
        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
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


def demonstrate_signal(direction='LONG'):
    """Demonstrate signal generation for given direction"""
    print(f"\n{'='*60}")
    print(f"  🎯 DEMONSTRATING {direction} SIGNAL")
    print(f"{'='*60}\n")
    
    # Generate data
    print(f"📊 Generating {direction}-favorable market data...")
    df = generate_signal_ready_data(direction)
    
    print(f"✅ Generated {len(df)} candles")
    print(f"   Starting price: ${df['close'].iloc[0]:.2f}")
    print(f"   Current price: ${df['close'].iloc[-1]:.2f}")
    print(f"   Change: {((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100):.2f}%\n")
    
    # Calculate indicators
    print("📈 Calculating technical indicators...")
    indicators = TechnicalIndicators(df)
    indicator_values = indicators.get_all_indicators()
    
    print(f"   ✓ RSI: {indicator_values['rsi']:.2f}")
    print(f"   ✓ MACD: {indicator_values['macd']['macd']:.2f}")
    print(f"   ✓ MACD Signal: {indicator_values['macd']['signal']:.2f}")
    print(f"   ✓ ATR: {indicator_values['atr']['atr']:.2f} ({indicator_values['atr']['atr_percentage']:.2f}%)\n")
    
    # Generate strategy signal
    print("🎯 Generating trading signal...")
    strategy = TradingStrategy(df)
    
    trend = strategy.check_trend()
    volatility = strategy.check_volatility()
    trade_direction = strategy.check_direction()
    
    print(f"   Detected Trend: {trend}")
    print(f"   Volatility: {volatility['status']}")
    print(f"   Trade Direction: {trade_direction}\n")
    
    signal = strategy.generate_signal()
    
    if signal:
        print("✅ ✅ ✅ TRADING SIGNAL GENERATED! ✅ ✅ ✅\n")
        print("="*60)
        print("SIGNAL DETAILS:")
        print("="*60)
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
        print(f"📉 Risk Amount: ${signal['risk_reward']['risk']}")
        print(f"📈 Potential Reward: ${signal['risk_reward']['reward']}")
        print("="*60 + "\n")
        
        # Show Telegram message format
        print("📱 TELEGRAM MESSAGE PREVIEW:")
        print("="*60)
        telegram = TelegramNotifier()
        message = telegram.format_signal_message(signal, config.SYMBOL)
        print(message)
        print("="*60)
        return True
    else:
        print("⚠️  No signal generated")
        print(f"   This can happen if:")
        print(f"   - Volatility is too low ({volatility['atr_percentage']:.2f}% < {config.MIN_VOLATILITY}%)")
        print(f"   - Risk/Reward ratio is too low")
        print(f"   - Conflicting indicator signals")
        return False


def main():
    """Main demo function"""
    print("\n" + "="*60)
    print("  🤖 AI BTC TRADING BOT - SIGNAL DEMONSTRATION")
    print("  📈 Professional Scalping with Multi-Indicators")
    print("="*60)
    
    # Try to generate both LONG and SHORT signals
    print("\n🔍 Attempting to generate trading signals...\n")
    
    success = False
    attempts = 0
    max_attempts = 5
    
    while not success and attempts < max_attempts:
        attempts += 1
        print(f"\n{'='*60}")
        print(f"  Attempt {attempts}/{max_attempts}")
        print(f"{'='*60}")
        
        # Try LONG signal
        print("\n🟢 Trying LONG signal generation...")
        np.random.seed(attempts * 100)  # Different seed each attempt
        success = demonstrate_signal('LONG')
        
        if not success:
            print("\n🔴 Trying SHORT signal generation...")
            np.random.seed(attempts * 100 + 50)
            success = demonstrate_signal('SHORT')
    
    if not success:
        print("\n" + "="*60)
        print("ℹ️  NOTE: Signal generation is intentionally conservative")
        print("   The bot only trades when conditions are highly favorable")
        print("   This protects capital and ensures quality trades")
        print("="*60)
    
    print("\n" + "="*60)
    print("  📚 HOW TO USE THE BOT")
    print("="*60)
    print("""
1. 📝 Setup Environment:
   - Copy .env.example to .env
   - Add your Binance API keys
   - Add your Telegram bot token and chat ID

2. 🚀 Run the Bot:
   python trading_bot.py

3. 🔄 Continuous Monitoring:
   Edit trading_bot.py and enable:
   bot.run_continuous(interval=60)

4. ⚙️  Customize Settings:
   Edit config.py to adjust:
   - Leverage and position size
   - Indicator parameters
   - Risk management rules
   - Signal sensitivity

5. 📊 Monitor Performance:
   - Signals sent to Telegram automatically
   - Review entry/exit points
   - Track risk/reward ratios
""")
    
    print("="*60)
    print("✅ Demo complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
