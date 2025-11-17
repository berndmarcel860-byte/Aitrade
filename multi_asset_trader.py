"""
Multi-Asset Trading Module
Support for multiple cryptocurrencies and timeframes
"""
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import config
from strategy import TradingStrategy
from advanced_strategies import ScalpingStrategy, SwingStrategy
from telegram_notifier import TelegramNotifier


class MultiAssetTrader:
    """Trade multiple cryptocurrencies across different timeframes"""
    
    # Supported cryptocurrencies
    SUPPORTED_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT',
        'XRPUSDT', 'SOLUSDT', 'DOTUSDT', 'MATICUSDT', 'LTCUSDT'
    ]
    
    # Supported timeframes
    SUPPORTED_TIMEFRAMES = {
        '1m': '1 minute',
        '3m': '3 minutes',
        '5m': '5 minutes',
        '15m': '15 minutes',
        '30m': '30 minutes',
        '1h': '1 hour',
        '2h': '2 hours',
        '4h': '4 hours',
        '1d': '1 day'
    }
    
    def __init__(self, symbols=None, timeframes=None):
        """
        Initialize multi-asset trader
        
        Args:
            symbols: List of symbols to trade (default: BTC, ETH, BNB)
            timeframes: List of timeframes (default: 5m, 15m)
        """
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        self.timeframes = timeframes or ['5m', '15m']
        self.telegram = TelegramNotifier()
        
        # Validate symbols
        for symbol in self.symbols:
            if symbol not in self.SUPPORTED_SYMBOLS:
                print(f"⚠️  Warning: {symbol} not in supported list")
        
        # Validate timeframes
        for tf in self.timeframes:
            if tf not in self.SUPPORTED_TIMEFRAMES:
                print(f"⚠️  Warning: {tf} not in supported timeframes")
        
        # Initialize Binance client
        self.client = None
        if config.BINANCE_API_KEY and config.BINANCE_API_SECRET:
            try:
                self.client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
                self.client.ping()
                print("✅ Connected to Binance API")
            except BinanceAPIException as e:
                print(f"❌ Binance API Error: {e}")
        
        print(f"\n📊 Multi-Asset Trader Initialized")
        print(f"   Symbols: {', '.join(self.symbols)}")
        print(f"   Timeframes: {', '.join(self.timeframes)}")
    
    def fetch_data(self, symbol, timeframe, limit=200):
        """
        Fetch historical data for symbol and timeframe
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            limit: Number of candles
            
        Returns:
            DataFrame: OHLCV data
        """
        if not self.client:
            return self._generate_sample_data(limit)
        
        try:
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
        except BinanceAPIException as e:
            print(f"❌ Error fetching {symbol} {timeframe}: {e}")
            return None
    
    def _generate_sample_data(self, periods):
        """Generate sample data"""
        import numpy as np
        
        base_price = 43000
        closes = [base_price]
        for i in range(1, periods):
            closes.append(closes[-1] * (1 + np.random.randn() * 0.003))
        
        data = {
            'timestamp': list(range(periods)),
            'open': [c * (1 + np.random.randn() * 0.001) for c in closes],
            'close': closes,
            'volume': [abs(np.random.randn()) * 100 + 50 for _ in closes]
        }
        data['high'] = [max(o, c) * (1 + abs(np.random.randn()) * 0.002) 
                        for o, c in zip(data['open'], closes)]
        data['low'] = [min(o, c) * (1 - abs(np.random.randn()) * 0.002) 
                       for o, c in zip(data['open'], closes)]
        
        return pd.DataFrame(data)
    
    def scan_all_markets(self, strategy_class=TradingStrategy):
        """
        Scan all symbols and timeframes for signals
        
        Args:
            strategy_class: Strategy class to use
            
        Returns:
            list: List of signals found
        """
        signals = []
        
        print("\n🔍 Scanning markets...")
        print("="*70)
        
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                print(f"\n📊 Analyzing {symbol} on {timeframe} timeframe...")
                
                # Fetch data
                df = self.fetch_data(symbol, timeframe)
                
                if df is None or len(df) < 50:
                    print(f"   ⚠️  Insufficient data")
                    continue
                
                # Generate signal
                strategy = strategy_class(df)
                signal = strategy.generate_signal()
                
                if signal:
                    signal['symbol'] = symbol
                    signal['timeframe'] = timeframe
                    signals.append(signal)
                    
                    print(f"   ✅ Signal found!")
                    print(f"      Direction: {signal['direction']}")
                    print(f"      Strategy: {signal.get('strategy', 'Default')}")
                    print(f"      Current Price: ${signal['current_price']}")
                else:
                    print(f"   ⚠️  No signal")
        
        print("\n="*70)
        print(f"✅ Scan complete. Found {len(signals)} signal(s)")
        
        return signals
    
    def analyze_best_opportunities(self):
        """
        Scan and rank best trading opportunities
        
        Returns:
            list: Ranked list of opportunities
        """
        opportunities = []
        
        # Scan with different strategies
        strategies = {
            'Scalping': ScalpingStrategy,
            'Swing': SwingStrategy,
            'Default': TradingStrategy
        }
        
        for strategy_name, strategy_class in strategies.items():
            signals = self.scan_all_markets(strategy_class)
            
            for signal in signals:
                # Calculate opportunity score
                score = self._calculate_opportunity_score(signal)
                signal['opportunity_score'] = score
                signal['strategy_type'] = strategy_name
                opportunities.append(signal)
        
        # Rank by score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return opportunities
    
    def _calculate_opportunity_score(self, signal):
        """
        Calculate opportunity score for ranking
        
        Args:
            signal: Trading signal
            
        Returns:
            float: Opportunity score (0-100)
        """
        score = 50  # Base score
        
        # RSI contribution
        rsi = signal.get('rsi', 50)
        if signal['direction'] == 'LONG':
            if rsi < 35:
                score += 15
            elif rsi < 45:
                score += 10
        else:
            if rsi > 65:
                score += 15
            elif rsi > 55:
                score += 10
        
        # Trend contribution
        trend = signal.get('trend', 'SIDEWAYS')
        if signal['direction'] == 'LONG' and 'UPTREND' in trend:
            score += 15
        elif signal['direction'] == 'SHORT' and 'DOWNTREND' in trend:
            score += 15
        
        # Volatility contribution
        volatility = signal.get('volatility', {})
        if volatility.get('status') == 'HIGH':
            score += 10
        elif volatility.get('status') == 'MEDIUM':
            score += 5
        
        # Risk/Reward contribution
        rr = signal.get('risk_reward', {}).get('rr_ratio', 0)
        if rr >= 3:
            score += 15
        elif rr >= 2:
            score += 10
        elif rr >= 1.5:
            score += 5
        
        return min(100, max(0, score))
    
    def send_best_signals(self, limit=3):
        """
        Find and send best trading signals to Telegram
        
        Args:
            limit: Number of top signals to send
        """
        opportunities = self.analyze_best_opportunities()
        
        if not opportunities:
            print("⚠️  No trading opportunities found")
            return
        
        print(f"\n📤 Sending top {min(limit, len(opportunities))} signal(s) to Telegram...")
        
        for i, signal in enumerate(opportunities[:limit], 1):
            print(f"\n{i}. {signal['symbol']} ({signal['timeframe']}) - Score: {signal['opportunity_score']:.0f}/100")
            
            # Add ranking info to signal
            message_prefix = f"🏆 #{i} Trading Opportunity (Score: {signal['opportunity_score']:.0f}/100)\n"
            
            self.telegram.send_signal(signal, signal['symbol'])
    
    def get_market_overview(self):
        """Get overview of all markets"""
        overview = []
        
        for symbol in self.symbols:
            df = self.fetch_data(symbol, '1h', limit=24)
            
            if df is None or len(df) < 2:
                continue
            
            current_price = df['close'].iloc[-1]
            price_24h_ago = df['close'].iloc[0]
            change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            overview.append({
                'symbol': symbol,
                'price': current_price,
                'change_24h': change_24h
            })
        
        # Sort by absolute change
        overview.sort(key=lambda x: abs(x['change_24h']), reverse=True)
        
        return overview
    
    def print_market_overview(self):
        """Print market overview"""
        overview = self.get_market_overview()
        
        print("\n" + "="*70)
        print("  📊 MARKET OVERVIEW (24h)")
        print("="*70)
        
        for item in overview:
            emoji = "📈" if item['change_24h'] > 0 else "📉"
            print(f"{emoji} {item['symbol']:12} ${item['price']:>10,.2f}   {item['change_24h']:>+6.2f}%")
        
        print("="*70 + "\n")


def main():
    """Example usage"""
    print("\n🚀 Multi-Asset Trader Demo")
    
    # Initialize trader with multiple assets
    trader = MultiAssetTrader(
        symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
        timeframes=['5m', '15m']
    )
    
    # Print market overview
    trader.print_market_overview()
    
    # Scan for opportunities
    print("\n🔍 Scanning for trading opportunities...")
    opportunities = trader.analyze_best_opportunities()
    
    if opportunities:
        print(f"\n✅ Found {len(opportunities)} opportunities")
        print("\nTop 3 Opportunities:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"{i}. {opp['symbol']} ({opp['timeframe']}) - {opp['direction']} - Score: {opp['opportunity_score']:.0f}/100")
    else:
        print("\n⚠️  No opportunities found at this time")


if __name__ == "__main__":
    main()
