"""
Performance Analytics Module
Analyze trading performance and generate reports
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database_logger import DatabaseLogger


class PerformanceAnalytics:
    """Analyze and visualize trading performance"""
    
    def __init__(self, db_path='trading_data.db'):
        """
        Initialize performance analytics
        
        Args:
            db_path: Path to trading database
        """
        self.db = DatabaseLogger(db_path)
    
    def get_trade_dataframe(self, days=30):
        """
        Get trades as pandas DataFrame
        
        Args:
            days: Number of days to look back
            
        Returns:
            DataFrame: Trade data
        """
        trades = self.db.get_trade_history(days)
        
        if not trades:
            return pd.DataFrame()
        
        df = pd.DataFrame([dict(t) for t in trades])
        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['exit_time'] = pd.to_datetime(df['exit_time'])
        df['duration'] = (df['exit_time'] - df['entry_time']).dt.total_seconds() / 3600  # hours
        
        return df
    
    def calculate_metrics(self, days=30):
        """
        Calculate comprehensive performance metrics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            dict: Performance metrics
        """
        df = self.get_trade_dataframe(days)
        
        if df.empty:
            return self._empty_metrics()
        
        # Basic metrics
        total_trades = len(df)
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] <= 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = df['pnl'].sum()
        avg_win = df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = abs(df[df['pnl'] <= 0]['pnl'].mean()) if losing_trades > 0 else 0
        largest_win = df['pnl'].max() if total_trades > 0 else 0
        largest_loss = df['pnl'].min() if total_trades > 0 else 0
        
        # Profit factor
        gross_profit = df[df['pnl'] > 0]['pnl'].sum() if winning_trades > 0 else 0
        gross_loss = abs(df[df['pnl'] <= 0]['pnl'].sum()) if losing_trades > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
        
        # Consecutive wins/losses
        df['win'] = df['pnl'] > 0
        df['streak'] = df['win'].ne(df['win'].shift()).cumsum()
        win_streaks = df[df['win']].groupby('streak').size()
        loss_streaks = df[~df['win']].groupby('streak').size()
        
        max_consecutive_wins = win_streaks.max() if len(win_streaks) > 0 else 0
        max_consecutive_losses = loss_streaks.max() if len(loss_streaks) > 0 else 0
        
        # Duration metrics
        avg_trade_duration = df['duration'].mean()
        
        # Drawdown calculation
        df['cumulative_pnl'] = df['pnl'].cumsum()
        df['running_max'] = df['cumulative_pnl'].cumsum().expanding().max()
        df['drawdown'] = df['cumulative_pnl'] - df['running_max']
        max_drawdown = abs(df['drawdown'].min()) if total_trades > 0 else 0
        
        # Risk-adjusted returns (Sharpe ratio)
        returns = df['pnl_pct'].values
        sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        
        # Direction analysis
        long_trades = df[df['direction'] == 'LONG']
        short_trades = df[df['direction'] == 'SHORT']
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'avg_trade_duration_hours': avg_trade_duration,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'long_trades': len(long_trades),
            'long_win_rate': (len(long_trades[long_trades['pnl'] > 0]) / len(long_trades) * 100) if len(long_trades) > 0 else 0,
            'short_trades': len(short_trades),
            'short_win_rate': (len(short_trades[short_trades['pnl'] > 0]) / len(short_trades) * 100) if len(short_trades) > 0 else 0
        }
    
    def _empty_metrics(self):
        """Return empty metrics dictionary"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'profit_factor': 0,
            'expectancy': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'avg_trade_duration_hours': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'long_trades': 0,
            'long_win_rate': 0,
            'short_trades': 0,
            'short_win_rate': 0
        }
    
    def print_performance_report(self, days=30):
        """
        Print comprehensive performance report
        
        Args:
            days: Number of days to analyze
        """
        metrics = self.calculate_metrics(days)
        
        print("\n" + "="*70)
        print(f"  📊 PERFORMANCE REPORT (Last {days} days)")
        print("="*70)
        
        print("\n📈 Trading Activity:")
        print(f"   Total Trades: {metrics['total_trades']}")
        print(f"   Winning Trades: {metrics['winning_trades']} ({metrics['win_rate']:.2f}%)")
        print(f"   Losing Trades: {metrics['losing_trades']}")
        print(f"   Average Duration: {metrics['avg_trade_duration_hours']:.2f} hours")
        
        print("\n💰 Profitability:")
        print(f"   Total P&L: ${metrics['total_pnl']:.2f}")
        print(f"   Average Win: ${metrics['avg_win']:.2f}")
        print(f"   Average Loss: ${metrics['avg_loss']:.2f}")
        print(f"   Largest Win: ${metrics['largest_win']:.2f}")
        print(f"   Largest Loss: ${metrics['largest_loss']:.2f}")
        print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"   Expectancy: ${metrics['expectancy']:.2f}")
        
        print("\n📊 Risk Metrics:")
        print(f"   Max Drawdown: ${metrics['max_drawdown']:.2f}")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"   Max Consecutive Wins: {metrics['max_consecutive_wins']}")
        print(f"   Max Consecutive Losses: {metrics['max_consecutive_losses']}")
        
        print("\n🎯 Direction Analysis:")
        print(f"   Long Trades: {metrics['long_trades']} (Win Rate: {metrics['long_win_rate']:.2f}%)")
        print(f"   Short Trades: {metrics['short_trades']} (Win Rate: {metrics['short_win_rate']:.2f}%)")
        
        print("\n" + "="*70)
        
        # Performance grade
        grade = self._calculate_grade(metrics)
        print(f"\n🏆 Performance Grade: {grade}")
        print("="*70 + "\n")
    
    def _calculate_grade(self, metrics):
        """Calculate performance grade A-F"""
        score = 0
        
        # Win rate (max 30 points)
        if metrics['win_rate'] >= 60:
            score += 30
        elif metrics['win_rate'] >= 50:
            score += 25
        elif metrics['win_rate'] >= 40:
            score += 20
        else:
            score += 10
        
        # Profit factor (max 30 points)
        if metrics['profit_factor'] >= 2.0:
            score += 30
        elif metrics['profit_factor'] >= 1.5:
            score += 25
        elif metrics['profit_factor'] >= 1.2:
            score += 20
        else:
            score += 10
        
        # Sharpe ratio (max 20 points)
        if metrics['sharpe_ratio'] >= 2.0:
            score += 20
        elif metrics['sharpe_ratio'] >= 1.0:
            score += 15
        elif metrics['sharpe_ratio'] >= 0.5:
            score += 10
        else:
            score += 5
        
        # Profitability (max 20 points)
        if metrics['total_pnl'] > 0:
            score += 20
        else:
            score += 5
        
        # Grade assignment
        if score >= 85:
            return "A+ (Excellent)"
        elif score >= 75:
            return "A (Very Good)"
        elif score >= 65:
            return "B (Good)"
        elif score >= 55:
            return "C (Average)"
        elif score >= 45:
            return "D (Below Average)"
        else:
            return "F (Poor)"
    
    def get_daily_performance(self, days=30):
        """
        Get daily performance summary
        
        Args:
            days: Number of days
            
        Returns:
            DataFrame: Daily performance
        """
        df = self.get_trade_dataframe(days)
        
        if df.empty:
            return pd.DataFrame()
        
        df['date'] = df['exit_time'].dt.date
        
        daily = df.groupby('date').agg({
            'pnl': ['sum', 'count'],
            'pnl_pct': 'mean'
        }).reset_index()
        
        daily.columns = ['date', 'total_pnl', 'num_trades', 'avg_return_pct']
        daily['cumulative_pnl'] = daily['total_pnl'].cumsum()
        
        return daily
    
    def print_daily_summary(self, days=7):
        """Print daily performance summary"""
        daily = self.get_daily_performance(days)
        
        if daily.empty:
            print("⚠️  No trade data available")
            return
        
        print("\n" + "="*70)
        print(f"  📅 DAILY PERFORMANCE SUMMARY (Last {days} days)")
        print("="*70)
        print(f"{'Date':<12} {'Trades':>8} {'Daily P&L':>12} {'Cumulative':>12}")
        print("-"*70)
        
        for _, row in daily.iterrows():
            emoji = "📈" if row['total_pnl'] > 0 else "📉"
            print(f"{emoji} {row['date']!s:<10} {row['num_trades']:>8.0f} "
                  f"${row['total_pnl']:>10.2f} ${row['cumulative_pnl']:>10.2f}")
        
        print("="*70 + "\n")
    
    def analyze_strategy_performance(self):
        """Analyze performance by strategy"""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.strategy, COUNT(*) as trades,
                   SUM(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END) as wins,
                   SUM(t.pnl) as total_pnl,
                   AVG(t.pnl_pct) as avg_return_pct
            FROM trades t
            JOIN signals s ON t.signal_id = s.id
            WHERE t.status = 'CLOSED'
            GROUP BY s.strategy
        ''')
        
        results = cursor.fetchall()
        
        if not results:
            print("⚠️  No strategy data available")
            return
        
        print("\n" + "="*70)
        print("  📊 STRATEGY PERFORMANCE COMPARISON")
        print("="*70)
        print(f"{'Strategy':<20} {'Trades':>8} {'Win Rate':>10} {'Total P&L':>12}")
        print("-"*70)
        
        for row in results:
            strategy = row['strategy'] or 'Default'
            trades = row['trades']
            wins = row['wins']
            win_rate = (wins / trades * 100) if trades > 0 else 0
            total_pnl = row['total_pnl']
            
            print(f"{strategy:<20} {trades:>8} {win_rate:>9.1f}% ${total_pnl:>10.2f}")
        
        print("="*70 + "\n")
    
    def export_report(self, filename='performance_report.txt', days=30):
        """
        Export performance report to file
        
        Args:
            filename: Output filename
            days: Number of days to analyze
        """
        import sys
        from io import StringIO
        
        # Capture print output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        self.print_performance_report(days)
        self.print_daily_summary(min(days, 7))
        self.analyze_strategy_performance()
        
        report = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Write to file
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"✅ Performance report exported to {filename}")


def main():
    """Example usage"""
    print("\n🚀 Performance Analytics Demo")
    
    # Create example database with sample data
    from database_logger import DatabaseLogger
    import os
    
    db_path = 'example_analytics.db'
    db = DatabaseLogger(db_path)
    
    # Add sample trades
    for i in range(10):
        signal_id = db.log_signal({
            'strategy': 'Scalping' if i % 2 == 0 else 'Swing',
            'direction': 'LONG' if i % 3 == 0 else 'SHORT',
            'current_price': 43000 + i * 100,
            'entry_range': '43000 - 43500',
            'take_profit': 'TP1: 44000 | TP2: 44500 | TP3: 45000',
            'stop_loss': 42500,
            'leverage': 10,
            'position_size': 100
        }, 'BTCUSDT')
        
        trade_id = db.log_trade_open(signal_id, 'BTCUSDT', 'LONG', 43000, 0.002, 10)
        
        # Random P&L
        pnl = np.random.randn() * 50
        pnl_pct = pnl / 86  # Assuming 86 USDT position
        
        db.log_trade_close(trade_id, 43000 + pnl, 'Take Profit', pnl, pnl_pct)
    
    # Create analytics
    analytics = PerformanceAnalytics(db_path)
    
    # Print reports
    analytics.print_performance_report(30)
    analytics.print_daily_summary(7)
    analytics.analyze_strategy_performance()
    
    # Cleanup
    db.close()
    os.remove(db_path)


if __name__ == "__main__":
    main()
