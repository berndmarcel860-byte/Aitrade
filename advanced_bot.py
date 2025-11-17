"""
Advanced Trading Bot Integration
Combines all advanced features: backtesting, position management, 
multiple strategies, database logging, and performance analytics
"""
import time
from datetime import datetime
import config
from trading_bot import BTCTradingBot
from advanced_strategies import ScalpingStrategy, SwingStrategy, BreakoutStrategy, MeanReversionStrategy
from position_manager import PositionManager
from database_logger import DatabaseLogger
from performance_analytics import PerformanceAnalytics
from multi_asset_trader import MultiAssetTrader
from telegram_notifier import TelegramNotifier


class AdvancedTradingBot:
    """Enhanced trading bot with advanced features"""
    
    def __init__(self, symbols=None, strategies=None):
        """
        Initialize advanced trading bot
        
        Args:
            symbols: List of symbols to trade
            strategies: Dictionary of strategy names to classes
        """
        print("\n" + "="*70)
        print("  🚀 ADVANCED AI TRADING BOT")
        print("  Professional Multi-Strategy, Multi-Asset Trading System")
        print("="*70 + "\n")
        
        # Initialize components
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        self.strategies = strategies or {
            'Scalping': ScalpingStrategy,
            'Swing': SwingStrategy,
            'Breakout': BreakoutStrategy,
            'Mean Reversion': MeanReversionStrategy
        }
        
        self.position_manager = PositionManager()
        self.database = DatabaseLogger('trading_data.db')
        self.telegram = TelegramNotifier()
        self.multi_asset = MultiAssetTrader(symbols=self.symbols, timeframes=['5m', '15m'])
        
        print("✅ Position Manager initialized")
        print("✅ Database logging enabled")
        print("✅ Multi-asset scanner ready")
        print(f"✅ {len(self.strategies)} trading strategies loaded")
        print(f"✅ Monitoring {len(self.symbols)} symbols")
        print()
    
    def run_complete_analysis(self):
        """Run comprehensive market analysis with all strategies"""
        print("\n" + "="*70)
        print(f"  🔍 COMPLETE MARKET ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        all_signals = []
        
        # 1. Market Overview
        print("📊 Market Overview:")
        self.multi_asset.print_market_overview()
        
        # 2. Scan with all strategies
        print("\n🔍 Scanning with all strategies...")
        
        for strategy_name, strategy_class in self.strategies.items():
            print(f"\n   Testing {strategy_name} strategy...")
            signals = self.multi_asset.scan_all_markets(strategy_class)
            
            for signal in signals:
                signal['strategy'] = strategy_name
                all_signals.append(signal)
                
                # Log to database
                self.database.log_signal(signal, signal['symbol'])
            
            print(f"   Found {len(signals)} signal(s)")
        
        # 3. Rank and display best opportunities
        if all_signals:
            print(f"\n✅ Total signals found: {len(all_signals)}")
            
            # Calculate scores and sort
            for signal in all_signals:
                signal['score'] = self._calculate_signal_score(signal)
            
            all_signals.sort(key=lambda x: x['score'], reverse=True)
            
            # Display top opportunities
            print("\n🏆 Top 5 Trading Opportunities:")
            print("-"*70)
            
            for i, signal in enumerate(all_signals[:5], 1):
                print(f"\n{i}. {signal['symbol']} - {signal['strategy']} ({signal['timeframe']})")
                print(f"   Score: {signal['score']:.0f}/100")
                print(f"   Direction: {signal['direction']}")
                print(f"   Current Price: ${signal['current_price']}")
                print(f"   Entry: {signal['entry_range']}")
                
                # Send top 3 to Telegram
                if i <= 3:
                    self.telegram.send_signal(signal, signal['symbol'])
        
        else:
            print("\n⚠️  No trading signals found at this time")
            print("   Market conditions may not be favorable")
        
        print("\n" + "="*70)
        
        return all_signals
    
    def _calculate_signal_score(self, signal):
        """Calculate comprehensive signal score"""
        score = 50  # Base score
        
        # RSI contribution
        rsi = signal.get('rsi', 50)
        if signal['direction'] == 'LONG' and rsi < 35:
            score += 15
        elif signal['direction'] == 'SHORT' and rsi > 65:
            score += 15
        elif signal['direction'] == 'LONG' and rsi < 50:
            score += 10
        elif signal['direction'] == 'SHORT' and rsi > 50:
            score += 10
        
        # Trend alignment
        trend = signal.get('trend', 'SIDEWAYS')
        if (signal['direction'] == 'LONG' and 'UPTREND' in trend) or \
           (signal['direction'] == 'SHORT' and 'DOWNTREND' in trend):
            score += 15
        
        # Volatility bonus
        volatility = signal.get('volatility', {})
        if volatility.get('status') in ['HIGH', 'MEDIUM']:
            score += 10
        
        # Strategy-specific bonuses
        if signal.get('strategy') == 'Breakout':
            score += 10  # Breakouts are often strong signals
        elif signal.get('strategy') == 'Mean Reversion':
            deviation = signal.get('deviation', 0)
            if deviation > 2:
                score += 15
        
        return min(100, max(0, score))
    
    def monitor_and_manage_positions(self):
        """Monitor open positions and manage them"""
        print("\n📊 Position Management:")
        
        positions = self.position_manager.get_all_positions()
        
        if not positions:
            print("   No open positions")
            return
        
        print(f"   Currently managing {len(positions)} position(s)")
        
        # Get current prices
        price_feed = {}
        for pos in positions:
            symbol = pos['symbol']
            # In real implementation, fetch from Binance
            # For now, use entry price + random movement
            import numpy as np
            price_feed[symbol] = pos['entry_price'] * (1 + np.random.randn() * 0.01)
        
        # Monitor positions
        self.position_manager.monitor_positions(price_feed)
        
        # Update statistics
        stats = self.position_manager.get_statistics()
        if stats['total_trades'] > 0:
            print(f"\n   📈 Session Statistics:")
            print(f"      Closed Trades: {stats['total_trades']}")
            print(f"      Win Rate: {stats['win_rate']:.2f}%")
            print(f"      Total P&L: ${stats['total_pnl']:.2f}")
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "="*70)
        print("  📊 GENERATING PERFORMANCE REPORT")
        print("="*70)
        
        analytics = PerformanceAnalytics('trading_data.db')
        
        # Print reports
        analytics.print_performance_report(days=30)
        analytics.print_daily_summary(days=7)
        analytics.analyze_strategy_performance()
        
        # Export report
        analytics.export_report('performance_report.txt', days=30)
        
        print("✅ Reports generated successfully")
    
    def run_continuous_mode(self, interval=300):
        """
        Run bot in continuous mode
        
        Args:
            interval: Seconds between analysis cycles (default: 300 = 5 minutes)
        """
        print("\n🚀 Starting Continuous Trading Mode")
        print(f"   Analysis interval: {interval} seconds")
        print("   Press Ctrl+C to stop\n")
        
        cycle = 0
        
        try:
            while True:
                cycle += 1
                print(f"\n{'='*70}")
                print(f"  🔄 CYCLE {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*70}")
                
                # Run analysis
                signals = self.run_complete_analysis()
                
                # Manage positions
                self.monitor_and_manage_positions()
                
                # Generate report every 10 cycles
                if cycle % 10 == 0:
                    self.generate_performance_report()
                
                print(f"\n⏰ Next cycle in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping bot...")
            
            # Final report
            self.generate_performance_report()
            
            # Close database
            self.database.close()
            
            print("\n✅ Bot stopped successfully")
    
    def run_backtest_all_strategies(self, days=30):
        """Run backtests on all strategies"""
        from backtesting import Backtester
        
        print("\n" + "="*70)
        print("  🧪 BACKTESTING ALL STRATEGIES")
        print("="*70)
        
        results_summary = []
        
        for strategy_name, strategy_class in self.strategies.items():
            print(f"\n📊 Testing {strategy_name} Strategy...")
            
            backtester = Backtester(strategy_class=strategy_class)
            df = backtester.fetch_historical_data(
                'BTCUSDT',
                '5m',
                f'2024-01-01'
            )
            
            if df is None or len(df) < 200:
                df = backtester._generate_sample_data(1000)
            
            results = backtester.run_backtest(df, initial_capital=10000)
            results['strategy'] = strategy_name
            results_summary.append(results)
            
            print(f"\n   Results:")
            print(f"   Total Trades: {results['total_trades']}")
            print(f"   Win Rate: {results['win_rate']:.2f}%")
            print(f"   Total Return: {results['total_return_pct']:.2f}%")
            print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        
        # Compare strategies
        print("\n" + "="*70)
        print("  📊 STRATEGY COMPARISON")
        print("="*70)
        print(f"{'Strategy':<20} {'Trades':>8} {'Win Rate':>10} {'Return':>10} {'Sharpe':>8}")
        print("-"*70)
        
        for r in results_summary:
            print(f"{r['strategy']:<20} {r['total_trades']:>8} "
                  f"{r['win_rate']:>9.1f}% {r['total_return_pct']:>9.1f}% "
                  f"{r['sharpe_ratio']:>8.2f}")
        
        print("="*70 + "\n")
        
        # Find best strategy
        best = max(results_summary, key=lambda x: x['sharpe_ratio'])
        print(f"🏆 Best Strategy: {best['strategy']} (Sharpe: {best['sharpe_ratio']:.2f})")


def main():
    """Main execution"""
    import sys
    
    # Initialize advanced bot
    bot = AdvancedTradingBot(
        symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
        strategies={
            'Scalping': ScalpingStrategy,
            'Swing': SwingStrategy,
            'Breakout': BreakoutStrategy,
            'Mean Reversion': MeanReversionStrategy
        }
    )
    
    # Choose mode
    print("\n📋 Select Mode:")
    print("   1. Single Analysis")
    print("   2. Continuous Mode")
    print("   3. Backtest All Strategies")
    print("   4. Performance Report")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = input("\nEnter mode (1-4, default=1): ").strip() or "1"
    
    if mode == "1":
        # Single analysis
        bot.run_complete_analysis()
        bot.monitor_and_manage_positions()
        
    elif mode == "2":
        # Continuous mode
        bot.run_continuous_mode(interval=300)
        
    elif mode == "3":
        # Backtest all strategies
        bot.run_backtest_all_strategies(days=30)
        
    elif mode == "4":
        # Performance report
        bot.generate_performance_report()
        
    else:
        print("❌ Invalid mode selected")
        return
    
    print("\n✅ Execution complete!")


if __name__ == "__main__":
    main()
