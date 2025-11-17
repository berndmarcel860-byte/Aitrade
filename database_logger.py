"""
Database Logger Module
Logs all signals and trades to SQLite database
"""
import sqlite3
import json
from datetime import datetime
import os


class DatabaseLogger:
    """Log trading signals and performance to database"""
    
    def __init__(self, db_path='trading_data.db'):
        """
        Initialize database logger
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.create_tables()
    
    def connect(self):
        """Connect to database"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                strategy TEXT,
                direction TEXT NOT NULL,
                current_price REAL NOT NULL,
                entry_range TEXT,
                take_profit TEXT,
                stop_loss REAL,
                leverage INTEGER,
                position_size REAL,
                rsi REAL,
                macd_value REAL,
                macd_signal REAL,
                trend TEXT,
                volatility_status TEXT,
                volatility_pct REAL,
                signal_data TEXT
            )
        ''')
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_time TEXT,
                exit_price REAL,
                exit_reason TEXT,
                quantity REAL NOT NULL,
                leverage INTEGER,
                pnl REAL,
                pnl_pct REAL,
                status TEXT DEFAULT 'OPEN',
                FOREIGN KEY (signal_id) REFERENCES signals (id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                avg_win REAL DEFAULT 0,
                avg_loss REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
    
    def log_signal(self, signal, symbol):
        """
        Log a trading signal
        
        Args:
            signal: Signal dictionary
            symbol: Trading symbol
            
        Returns:
            int: Signal ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (
                timestamp, symbol, strategy, direction, current_price,
                entry_range, take_profit, stop_loss, leverage, position_size,
                rsi, macd_value, macd_signal, trend, volatility_status,
                volatility_pct, signal_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            symbol,
            signal.get('strategy', 'Default'),
            signal['direction'],
            signal['current_price'],
            signal['entry_range'],
            signal['take_profit'],
            signal['stop_loss'],
            signal.get('leverage', 10),
            signal.get('position_size', 100),
            signal.get('rsi', 0),
            signal.get('macd', {}).get('value', 0),
            signal.get('macd', {}).get('signal', 0),
            signal.get('trend', 'UNKNOWN'),
            signal.get('volatility', {}).get('status', 'UNKNOWN'),
            signal.get('volatility', {}).get('atr_percentage', 0),
            json.dumps(signal)
        ))
        
        conn.commit()
        signal_id = cursor.lastrowid
        
        print(f"📝 Signal logged to database (ID: {signal_id})")
        return signal_id
    
    def log_trade_open(self, signal_id, symbol, direction, entry_price, quantity, leverage):
        """
        Log opening of a trade
        
        Args:
            signal_id: Related signal ID
            symbol: Trading symbol
            direction: LONG or SHORT
            entry_price: Entry price
            quantity: Trade quantity
            leverage: Leverage used
            
        Returns:
            int: Trade ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                signal_id, symbol, direction, entry_time, entry_price,
                quantity, leverage, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')
        ''', (
            signal_id,
            symbol,
            direction,
            datetime.now().isoformat(),
            entry_price,
            quantity,
            leverage
        ))
        
        conn.commit()
        trade_id = cursor.lastrowid
        
        print(f"📝 Trade opened and logged (ID: {trade_id})")
        return trade_id
    
    def log_trade_close(self, trade_id, exit_price, exit_reason, pnl, pnl_pct):
        """
        Log closing of a trade
        
        Args:
            trade_id: Trade ID to close
            exit_price: Exit price
            exit_reason: Reason for exit
            pnl: Profit/Loss in USDT
            pnl_pct: Profit/Loss percentage
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE trades
            SET exit_time = ?, exit_price = ?, exit_reason = ?,
                pnl = ?, pnl_pct = ?, status = 'CLOSED'
            WHERE id = ?
        ''', (
            datetime.now().isoformat(),
            exit_price,
            exit_reason,
            pnl,
            pnl_pct,
            trade_id
        ))
        
        conn.commit()
        print(f"📝 Trade closed and logged (ID: {trade_id}, P&L: ${pnl:.2f})")
    
    def get_recent_signals(self, limit=10):
        """Get recent signals"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM signals
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        return cursor.fetchall()
    
    def get_open_trades(self):
        """Get all open trades"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades
            WHERE status = 'OPEN'
            ORDER BY entry_time DESC
        ''')
        
        return cursor.fetchall()
    
    def get_trade_history(self, days=30):
        """Get trade history for specified days"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades
            WHERE status = 'CLOSED'
            AND entry_time >= datetime('now', '-' || ? || ' days')
            ORDER BY entry_time DESC
        ''', (days,))
        
        return cursor.fetchall()
    
    def calculate_daily_performance(self, date=None):
        """
        Calculate and store daily performance metrics
        
        Args:
            date: Date to calculate (default: today)
        """
        if date is None:
            date = datetime.now().date().isoformat()
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get trades for the day
        cursor.execute('''
            SELECT * FROM trades
            WHERE DATE(exit_time) = ?
            AND status = 'CLOSED'
        ''', (date,))
        
        trades = cursor.fetchall()
        
        if not trades:
            return
        
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in trades)
        avg_win = sum(t['pnl'] for t in trades if t['pnl'] > 0) / winning_trades if winning_trades > 0 else 0
        avg_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] <= 0)) / losing_trades if losing_trades > 0 else 0
        
        # Insert or update performance
        cursor.execute('''
            INSERT OR REPLACE INTO performance (
                date, total_trades, winning_trades, losing_trades,
                win_rate, total_pnl, avg_win, avg_loss
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date, total_trades, winning_trades, losing_trades,
            win_rate, total_pnl, avg_win, avg_loss
        ))
        
        conn.commit()
        print(f"📊 Daily performance calculated for {date}")
    
    def get_performance_summary(self, days=30):
        """Get performance summary for specified period"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(total_trades) as total_trades,
                SUM(winning_trades) as winning_trades,
                SUM(losing_trades) as losing_trades,
                AVG(win_rate) as avg_win_rate,
                SUM(total_pnl) as total_pnl,
                AVG(avg_win) as avg_win,
                AVG(avg_loss) as avg_loss
            FROM performance
            WHERE date >= date('now', '-' || ? || ' days')
        ''', (days,))
        
        return cursor.fetchone()
    
    def export_to_csv(self, table_name, output_file):
        """
        Export table to CSV
        
        Args:
            table_name: Name of table to export
            output_file: Output CSV file path
        """
        import csv
        
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"⚠️  No data to export from {table_name}")
            return
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([col[0] for col in cursor.description])
            # Write data
            writer.writerows(rows)
        
        print(f"✅ Exported {len(rows)} rows from {table_name} to {output_file}")
    
    def print_statistics(self):
        """Print database statistics"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Count signals
        cursor.execute("SELECT COUNT(*) FROM signals")
        signal_count = cursor.fetchone()[0]
        
        # Count trades
        cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'OPEN'")
        open_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'CLOSED'")
        closed_trades = cursor.fetchone()[0]
        
        # Get total P&L
        cursor.execute("SELECT SUM(pnl) FROM trades WHERE status = 'CLOSED'")
        total_pnl = cursor.fetchone()[0] or 0
        
        print("\n" + "="*70)
        print("  📊 DATABASE STATISTICS")
        print("="*70)
        print(f"   Total Signals: {signal_count}")
        print(f"   Open Trades: {open_trades}")
        print(f"   Closed Trades: {closed_trades}")
        print(f"   Total P&L: ${total_pnl:.2f}")
        print("="*70 + "\n")


def example_usage():
    """Example usage of database logger"""
    db = DatabaseLogger('example_trading.db')
    
    # Example signal
    signal = {
        'strategy': 'Scalping',
        'direction': 'LONG',
        'current_price': 43500,
        'entry_range': '43250 - 43600',
        'take_profit': 'TP1: 44000 | TP2: 44500 | TP3: 45000',
        'stop_loss': 42800,
        'leverage': 10,
        'position_size': 100,
        'rsi': 42.5,
        'macd': {'value': 156.23, 'signal': 142.18},
        'trend': 'UPTREND',
        'volatility': {'status': 'MEDIUM', 'atr_percentage': 0.73}
    }
    
    # Log signal
    signal_id = db.log_signal(signal, 'BTCUSDT')
    
    # Log trade
    trade_id = db.log_trade_open(signal_id, 'BTCUSDT', 'LONG', 43500, 0.0023, 10)
    
    # Close trade
    db.log_trade_close(trade_id, 44000, 'Take Profit 1', 115, 2.65)
    
    # Print statistics
    db.print_statistics()
    
    # Clean up
    db.close()
    os.remove('example_trading.db')


if __name__ == "__main__":
    example_usage()
