"""
Backtesting Module
Evaluate trading strategies using historical data
"""
import pandas as pd
import numpy as np
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
import config
from strategy import TradingStrategy
from advanced_strategies import (
    ScalpingStrategy, 
    SwingStrategy, 
    BreakoutStrategy,
    MeanReversionStrategy
)


class Backtester:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, strategy_class=TradingStrategy):
        """
        Initialize backtester
        
        Args:
            strategy_class: Strategy class to test (default: TradingStrategy)
        """
        self.strategy_class = strategy_class
        self.client = None
        
        if config.BINANCE_API_KEY and config.BINANCE_API_SECRET:
            try:
                self.client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
            except:
                pass
    
    def fetch_historical_data(self, symbol, interval, start_date, end_date=None):
        """
        Fetch historical data from Binance
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe (e.g., '5m', '15m', '1h')
            start_date: Start date (string or timestamp)
            end_date: End date (optional)
            
        Returns:
            DataFrame: OHLCV data
        """
        if not self.client:
            print("⚠️  No Binance client available. Using sample data.")
            return self._generate_sample_data(1000)
        
        try:
            klines = self.client.get_historical_klines(
                symbol,
                interval,
                start_date,
                end_date
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
        except BinanceAPIException as e:
            print(f"❌ Error fetching historical data: {e}")
            return None
    
    def _generate_sample_data(self, periods):
        """Generate sample data for testing"""
        base_price = 43000
        dates = pd.date_range(start='2024-01-01', periods=periods, freq='5T')
        
        closes = [base_price]
        for i in range(1, periods):
            change = np.random.randn() * 0.003
            closes.append(closes[-1] * (1 + change))
        
        data = {
            'timestamp': dates,
            'open': [c * (1 + np.random.randn() * 0.001) for c in closes],
            'close': closes,
            'volume': [abs(np.random.randn()) * 100 + 50 for _ in closes]
        }
        data['high'] = [max(o, c) * (1 + abs(np.random.randn()) * 0.002) 
                        for o, c in zip(data['open'], closes)]
        data['low'] = [min(o, c) * (1 - abs(np.random.randn()) * 0.002) 
                       for o, c in zip(data['open'], closes)]
        
        return pd.DataFrame(data)
    
    def run_backtest(self, df, initial_capital=10000, position_size_pct=0.1):
        """
        Run backtest on historical data
        
        Args:
            df: Historical OHLCV dataframe
            initial_capital: Starting capital in USDT
            position_size_pct: Position size as percentage of capital
            
        Returns:
            dict: Backtest results
        """
        capital = initial_capital
        position = None
        trades = []
        equity_curve = [initial_capital]
        
        # Ensure we have enough data for indicators
        lookback = 200
        
        for i in range(lookback, len(df)):
            # Get data window
            window_df = df.iloc[:i+1].copy()
            
            # Generate signal
            strategy = self.strategy_class(window_df)
            signal = strategy.generate_signal()
            
            current_price = df.iloc[i]['close']
            timestamp = df.iloc[i]['timestamp']
            
            # Check if we have an open position
            if position is None and signal:
                # Open new position
                position_size = capital * position_size_pct
                quantity = position_size / current_price
                
                position = {
                    'direction': signal['direction'],
                    'entry_price': current_price,
                    'entry_time': timestamp,
                    'quantity': quantity,
                    'stop_loss': signal['stop_loss'],
                    'take_profit': self._parse_tp(signal['take_profit'])
                }
                
            elif position:
                # Check exit conditions
                exit_trade = False
                exit_reason = None
                exit_price = current_price
                
                if position['direction'] == 'LONG':
                    if current_price <= position['stop_loss']:
                        exit_trade = True
                        exit_reason = 'Stop Loss'
                        exit_price = position['stop_loss']
                    elif current_price >= position['take_profit'][0]:
                        exit_trade = True
                        exit_reason = 'Take Profit'
                        exit_price = position['take_profit'][0]
                else:  # SHORT
                    if current_price >= position['stop_loss']:
                        exit_trade = True
                        exit_reason = 'Stop Loss'
                        exit_price = position['stop_loss']
                    elif current_price <= position['take_profit'][0]:
                        exit_trade = True
                        exit_reason = 'Take Profit'
                        exit_price = position['take_profit'][0]
                
                if exit_trade:
                    # Calculate P&L
                    if position['direction'] == 'LONG':
                        pnl = (exit_price - position['entry_price']) * position['quantity']
                    else:
                        pnl = (position['entry_price'] - exit_price) * position['quantity']
                    
                    pnl_pct = (pnl / (position['entry_price'] * position['quantity'])) * 100
                    
                    capital += pnl
                    
                    # Record trade
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': timestamp,
                        'direction': position['direction'],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'quantity': position['quantity'],
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'exit_reason': exit_reason
                    })
                    
                    position = None
            
            equity_curve.append(capital)
        
        # Calculate statistics
        results = self._calculate_statistics(trades, initial_capital, capital, equity_curve)
        results['trades'] = trades
        
        return results
    
    def _parse_tp(self, tp_string):
        """Parse take profit string to list of values"""
        # Extract TP values from string like "TP1: 44000 | TP2: 44500 | TP3: 45000"
        tps = []
        for part in tp_string.split('|'):
            if 'TP' in part:
                value = float(part.split(':')[1].strip())
                tps.append(value)
        return tps if tps else [0, 0, 0]
    
    def _calculate_statistics(self, trades, initial_capital, final_capital, equity_curve):
        """Calculate backtest statistics"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_return_pct': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        total_pnl = sum(t['pnl'] for t in trades)
        total_return_pct = ((final_capital - initial_capital) / initial_capital) * 100
        
        # Calculate max drawdown
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max * 100
        max_drawdown = abs(drawdown.min())
        
        # Calculate Sharpe ratio (simplified)
        returns = np.diff(equity_array) / equity_array[:-1]
        sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losing_trades])) if losing_trades else 0
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(trades) * 100) if trades else 0,
            'total_pnl': total_pnl,
            'total_return_pct': total_return_pct,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': (avg_win / avg_loss) if avg_loss > 0 else 0,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'final_capital': final_capital
        }
    
    def print_results(self, results):
        """Print backtest results in a formatted way"""
        print("\n" + "="*70)
        print("  📊 BACKTEST RESULTS")
        print("="*70)
        
        print(f"\n📈 Performance Metrics:")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Winning Trades: {results['winning_trades']}")
        print(f"   Losing Trades: {results['losing_trades']}")
        print(f"   Win Rate: {results['win_rate']:.2f}%")
        
        print(f"\n💰 Financial Metrics:")
        print(f"   Total P&L: ${results['total_pnl']:.2f}")
        print(f"   Total Return: {results['total_return_pct']:.2f}%")
        print(f"   Final Capital: ${results['final_capital']:.2f}")
        
        if results['total_trades'] > 0:
            print(f"   Average Win: ${results['avg_win']:.2f}")
            print(f"   Average Loss: ${results['avg_loss']:.2f}")
            print(f"   Profit Factor: {results['profit_factor']:.2f}")
        
        print(f"\n📉 Risk Metrics:")
        print(f"   Max Drawdown: {results['max_drawdown']:.2f}%")
        print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        
        print("\n" + "="*70)


def main():
    """Example backtest execution"""
    print("\n🚀 Starting Backtest...")
    
    # Initialize backtester
    backtester = Backtester(strategy_class=TradingStrategy)
    
    # Fetch or generate data
    print("📊 Fetching historical data...")
    df = backtester.fetch_historical_data(
        symbol='BTCUSDT',
        interval='5m',
        start_date='2024-01-01',
        end_date='2024-01-31'
    )
    
    if df is None or len(df) < 200:
        print("⚠️  Using sample data for demonstration")
        df = backtester._generate_sample_data(1000)
    
    print(f"✅ Loaded {len(df)} candles")
    
    # Run backtest
    print("\n🔄 Running backtest...")
    results = backtester.run_backtest(df, initial_capital=10000, position_size_pct=0.1)
    
    # Print results
    backtester.print_results(results)
    
    # Show sample trades
    if results['trades']:
        print("\n📋 Sample Trades (first 5):")
        for i, trade in enumerate(results['trades'][:5], 1):
            print(f"\n   Trade {i}:")
            print(f"      Direction: {trade['direction']}")
            print(f"      Entry: ${trade['entry_price']:.2f}")
            print(f"      Exit: ${trade['exit_price']:.2f}")
            print(f"      P&L: ${trade['pnl']:.2f} ({trade['pnl_pct']:.2f}%)")
            print(f"      Exit Reason: {trade['exit_reason']}")


if __name__ == "__main__":
    main()
