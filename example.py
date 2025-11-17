"""
Simple working example showing successful signal generation
"""
import pandas as pd
import numpy as np
from strategy import TradingStrategy
from telegram_notifier import TelegramNotifier
import config


def create_realistic_uptrend():
    """Create realistic market data with moderate uptrend"""
    np.random.seed(42)
    
    timestamps = list(range(200))
    base_price = 43000
    
    closes = [base_price]
    
    # Create gradual uptrend with volatility
    for i in range(1, 200):
        # Moderate uptrend
        trend = 0.0008  # 0.08% per candle
        volatility = np.random.randn() * 0.003  # 0.3% random movement
        
        new_price = closes[-1] * (1 + trend + volatility)
        closes.append(new_price)
    
    # Generate OHLV
    data = {
        'timestamp': timestamps,
        'open': [],
        'high': [],
        'low': [],
        'close': closes,
        'volume': []
    }
    
    for close in closes:
        open_price = close * (1 + np.random.randn() * 0.002)
        high_price = max(open_price, close) * (1 + abs(np.random.randn()) * 0.003)
        low_price = min(open_price, close) * (1 - abs(np.random.randn()) * 0.003)
        volume = abs(np.random.randn()) * 100 + 50
        
        data['open'].append(open_price)
        data['high'].append(high_price)
        data['low'].append(low_price)
        data['volume'].append(volume)
    
    return pd.DataFrame(data)


def main():
    """Demonstrate successful signal generation"""
    print("\n" + "="*70)
    print("  🤖 AI BTC TRADING BOT - SUCCESSFUL SIGNAL EXAMPLE")
    print("="*70 + "\n")
    
    # Create realistic data
    print("📊 Creating realistic market data with moderate uptrend...")
    df = create_realistic_uptrend()
    
    print(f"\n✅ Market Data Summary:")
    print(f"   • Candles: {len(df)}")
    print(f"   • Starting Price: ${df['close'].iloc[0]:.2f}")
    print(f"   • Current Price: ${df['close'].iloc[-1]:.2f}")
    print(f"   • Price Change: {((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100):.2f}%")
    
    # Generate signal
    print("\n🎯 Analyzing market and generating signal...")
    strategy = TradingStrategy(df)
    
    # Show analysis details
    trend = strategy.check_trend()
    volatility = strategy.check_volatility()
    direction = strategy.check_direction()
    
    print(f"\n📈 Market Analysis:")
    print(f"   • Trend: {trend}")
    print(f"   • Volatility: {volatility['status']} ({volatility['atr_percentage']:.2f}%)")
    print(f"   • Direction: {direction}")
    
    # Get indicator values
    ind = strategy.indicator_values
    print(f"\n📊 Technical Indicators:")
    print(f"   • RSI: {ind['rsi']:.2f}")
    print(f"   • MACD: {ind['macd']['macd']:.2f}")
    print(f"   • MACD Signal: {ind['macd']['signal']:.2f}")
    print(f"   • MACD Histogram: {ind['macd']['diff']:.2f}")
    print(f"   • EMA 9: ${ind['ema']['short']:.2f}")
    print(f"   • EMA 21: ${ind['ema']['medium']:.2f}")
    print(f"   • EMA 50: ${ind['ema']['long']:.2f}")
    
    signal = strategy.generate_signal()
    
    if signal:
        print("\n" + "="*70)
        print("✅ ✅ ✅  TRADING SIGNAL SUCCESSFULLY GENERATED!  ✅ ✅ ✅")
        print("="*70 + "\n")
        
        print("📋 SIGNAL DETAILS:")
        print("-"*70)
        print(f"📊 Symbol:          {config.SYMBOL}")
        print(f"🎯 Direction:       {signal['direction']}")
        print(f"📈 Trend:           {signal['trend']}")
        print(f"💵 Current Price:   ${signal['current_price']}")
        print(f"🎯 Entry Range:     ${signal['entry_range']}")
        print(f"💰 Take Profit:     {signal['take_profit']}")
        print(f"🛡️  Stop Loss:       ${signal['stop_loss']}")
        print(f"⚡ Leverage:        {signal['leverage']}x")
        print(f"💼 Position Size:   ${signal['position_size']} USDT")
        print(f"📊 Risk/Reward:     {signal['risk_reward']['rr_ratio']}:1")
        print(f"💸 Risk Amount:     ${signal['risk_reward']['risk']}")
        print(f"💰 Reward Potential: ${signal['risk_reward']['reward']}")
        print("-"*70 + "\n")
        
        # Show formatted Telegram message
        print("="*70)
        print("📱 PROFESSIONAL TELEGRAM SIGNAL FORMAT:")
        print("="*70)
        
        telegram = TelegramNotifier()
        message = telegram.format_signal_message(signal, config.SYMBOL)
        print(message)
        
        print("="*70 + "\n")
        
        print("✅ This signal would be automatically sent to your Telegram channel!")
        print("   when you configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID\n")
        
    else:
        print("\n⚠️  No signal generated with this data")
        print("   The bot requires specific conditions to be met:")
        print(f"   • Minimum volatility: {config.MIN_VOLATILITY}%")
        print(f"   • Minimum R:R ratio: 1.5:1")
        print(f"   • Strong indicator alignment")
    
    # Show usage instructions
    print("\n" + "="*70)
    print("📚 NEXT STEPS:")
    print("="*70)
    print("""
1. 🔧 Configure Your Bot:
   • Copy .env.example to .env
   • Add your Binance API keys (or leave empty for demo mode)
   • Add your Telegram bot token and chat ID

2. 🚀 Run the Bot:
   • Single analysis: python trading_bot.py
   • Continuous mode: Edit trading_bot.py, enable run_continuous()

3. ⚙️  Customize (Optional):
   • Edit config.py to adjust trading parameters
   • Modify indicator settings, leverage, position size
   • Change risk management rules

4. 📊 Monitor:
   • Signals automatically sent to Telegram
   • Review and execute trades manually on Binance
   • Track performance and adjust parameters

⚠️  IMPORTANT: Always test with small amounts first!
""")
    
    print("="*70)
    print("✅ Demo Complete! Happy Trading! 🚀📈")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
