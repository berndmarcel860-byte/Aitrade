"""
Position Management Module
Manages open positions with trailing stops and auto-close
"""
import time
from datetime import datetime
import config


class PositionManager:
    """Manage open trading positions"""
    
    def __init__(self):
        """Initialize position manager"""
        self.positions = {}  # symbol -> position_info
        self.position_history = []
    
    def open_position(self, symbol, signal):
        """
        Open a new position
        
        Args:
            symbol: Trading symbol
            signal: Trading signal dictionary
        """
        if symbol in self.positions:
            print(f"⚠️  Position already open for {symbol}")
            return False
        
        position = {
            'symbol': symbol,
            'direction': signal['direction'],
            'entry_price': signal['current_price'],
            'entry_time': datetime.now(),
            'stop_loss': signal['stop_loss'],
            'take_profit_levels': self._parse_tp(signal['take_profit']),
            'quantity': config.POSITION_SIZE_USDT / signal['current_price'],
            'leverage': signal.get('leverage', config.LEVERAGE),
            'strategy': signal.get('strategy', 'Default'),
            'status': 'OPEN',
            'partial_exits': []
        }
        
        self.positions[symbol] = position
        print(f"✅ Opened {position['direction']} position for {symbol} at ${position['entry_price']:.2f}")
        
        return True
    
    def _parse_tp(self, tp_string):
        """Parse take profit string to list"""
        tps = []
        for part in tp_string.split('|'):
            if 'TP' in part:
                value = float(part.split(':')[1].strip())
                tps.append(value)
        return tps
    
    def update_trailing_stop(self, symbol, current_price, trailing_pct=0.5):
        """
        Update trailing stop loss
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            trailing_pct: Trailing percentage (default 0.5%)
        """
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        trailing_distance = current_price * (trailing_pct / 100)
        
        if position['direction'] == 'LONG':
            # Move stop loss up if price moved up
            new_stop = current_price - trailing_distance
            if new_stop > position['stop_loss']:
                old_stop = position['stop_loss']
                position['stop_loss'] = new_stop
                print(f"📈 Trailing stop updated for {symbol}: ${old_stop:.2f} → ${new_stop:.2f}")
        else:  # SHORT
            # Move stop loss down if price moved down
            new_stop = current_price + trailing_distance
            if new_stop < position['stop_loss']:
                old_stop = position['stop_loss']
                position['stop_loss'] = new_stop
                print(f"📉 Trailing stop updated for {symbol}: ${old_stop:.2f} → ${new_stop:.2f}")
    
    def check_exit_conditions(self, symbol, current_price):
        """
        Check if position should be closed
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            
        Returns:
            tuple: (should_exit, exit_reason, exit_percentage)
        """
        if symbol not in self.positions:
            return False, None, 0
        
        position = self.positions[symbol]
        
        if position['direction'] == 'LONG':
            # Check stop loss
            if current_price <= position['stop_loss']:
                return True, 'Stop Loss Hit', 100
            
            # Check take profit levels
            for i, tp_level in enumerate(position['take_profit_levels'], 1):
                if current_price >= tp_level and i not in [pe['level'] for pe in position['partial_exits']]:
                    # Partial exit at TP levels
                    exit_pct = 50 if i == 1 else 30 if i == 2 else 20
                    return True, f'Take Profit {i}', exit_pct
        
        else:  # SHORT
            # Check stop loss
            if current_price >= position['stop_loss']:
                return True, 'Stop Loss Hit', 100
            
            # Check take profit levels
            for i, tp_level in enumerate(position['take_profit_levels'], 1):
                if current_price <= tp_level and i not in [pe['level'] for pe in position['partial_exits']]:
                    exit_pct = 50 if i == 1 else 30 if i == 2 else 20
                    return True, f'Take Profit {i}', exit_pct
        
        return False, None, 0
    
    def close_position(self, symbol, current_price, reason, exit_percentage=100):
        """
        Close position (fully or partially)
        
        Args:
            symbol: Trading symbol
            current_price: Exit price
            reason: Exit reason
            exit_percentage: Percentage of position to close (default 100)
        """
        if symbol not in self.positions:
            print(f"⚠️  No open position for {symbol}")
            return
        
        position = self.positions[symbol]
        
        # Calculate P&L
        quantity_to_close = position['quantity'] * (exit_percentage / 100)
        
        if position['direction'] == 'LONG':
            pnl = (current_price - position['entry_price']) * quantity_to_close
        else:
            pnl = (position['entry_price'] - current_price) * quantity_to_close
        
        pnl_pct = (pnl / (position['entry_price'] * quantity_to_close)) * 100
        
        # Record exit
        exit_info = {
            'exit_time': datetime.now(),
            'exit_price': current_price,
            'exit_reason': reason,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'quantity_closed': quantity_to_close,
            'exit_percentage': exit_percentage
        }
        
        if exit_percentage == 100:
            # Full exit
            position['status'] = 'CLOSED'
            position['exit_info'] = exit_info
            
            # Move to history
            self.position_history.append(position)
            del self.positions[symbol]
            
            emoji = "✅" if pnl > 0 else "❌"
            print(f"\n{emoji} Closed {position['direction']} position for {symbol}")
            print(f"   Entry: ${position['entry_price']:.2f}")
            print(f"   Exit: ${current_price:.2f}")
            print(f"   P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
            print(f"   Reason: {reason}")
        else:
            # Partial exit
            tp_level = int(reason.split()[-1]) if 'Take Profit' in reason else 0
            position['partial_exits'].append({
                'level': tp_level,
                'info': exit_info
            })
            position['quantity'] -= quantity_to_close
            
            print(f"💰 Partial exit ({exit_percentage}%) for {symbol} at TP{tp_level}")
            print(f"   P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
            print(f"   Remaining: {(position['quantity'] / (position['quantity'] + quantity_to_close) * 100):.0f}%")
    
    def get_position_info(self, symbol):
        """Get information about an open position"""
        return self.positions.get(symbol)
    
    def get_all_positions(self):
        """Get all open positions"""
        return list(self.positions.values())
    
    def get_position_summary(self):
        """Get summary of all positions"""
        if not self.positions:
            return "No open positions"
        
        summary = []
        for symbol, pos in self.positions.items():
            summary.append(f"{symbol}: {pos['direction']} @ ${pos['entry_price']:.2f}")
        
        return "\n".join(summary)
    
    def monitor_positions(self, price_feed):
        """
        Monitor all positions and update stops/check exits
        
        Args:
            price_feed: Dict of symbol -> current_price
        """
        for symbol in list(self.positions.keys()):
            if symbol in price_feed:
                current_price = price_feed[symbol]
                
                # Update trailing stop
                self.update_trailing_stop(symbol, current_price)
                
                # Check exit conditions
                should_exit, reason, exit_pct = self.check_exit_conditions(symbol, current_price)
                
                if should_exit:
                    self.close_position(symbol, current_price, reason, exit_pct)
    
    def get_statistics(self):
        """Get trading statistics from history"""
        if not self.position_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0
            }
        
        total_pnl = 0
        winning_trades = []
        losing_trades = []
        
        for pos in self.position_history:
            pnl = pos['exit_info']['pnl']
            total_pnl += pnl
            
            if pnl > 0:
                winning_trades.append(pnl)
            else:
                losing_trades.append(abs(pnl))
        
        return {
            'total_trades': len(self.position_history),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.position_history) * 100) if self.position_history else 0,
            'total_pnl': total_pnl,
            'avg_win': sum(winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(losing_trades) / len(losing_trades) if losing_trades else 0
        }


def example_usage():
    """Example of position management"""
    print("\n" + "="*70)
    print("  📊 POSITION MANAGEMENT DEMO")
    print("="*70)
    
    # Create position manager
    pm = PositionManager()
    
    # Example signal
    signal = {
        'direction': 'LONG',
        'current_price': 43500,
        'stop_loss': 42800,
        'take_profit': 'TP1: 44000 | TP2: 44500 | TP3: 45000',
        'leverage': 10,
        'strategy': 'Scalping'
    }
    
    # Open position
    print("\n1. Opening position...")
    pm.open_position('BTCUSDT', signal)
    
    # Simulate price movements
    print("\n2. Simulating price movements...")
    
    # Price moves up - update trailing stop
    pm.update_trailing_stop('BTCUSDT', 43800)
    
    # Hit TP1
    should_exit, reason, pct = pm.check_exit_conditions('BTCUSDT', 44000)
    if should_exit:
        pm.close_position('BTCUSDT', 44000, reason, pct)
    
    # Continue monitoring
    should_exit, reason, pct = pm.check_exit_conditions('BTCUSDT', 44500)
    if should_exit:
        pm.close_position('BTCUSDT', 44500, reason, pct)
    
    # Final TP3
    should_exit, reason, pct = pm.check_exit_conditions('BTCUSDT', 45000)
    if should_exit:
        pm.close_position('BTCUSDT', 45000, reason, pct)
    
    # Get statistics
    print("\n3. Trading Statistics:")
    stats = pm.get_statistics()
    print(f"   Total Trades: {stats['total_trades']}")
    print(f"   Win Rate: {stats['win_rate']:.2f}%")
    print(f"   Total P&L: ${stats['total_pnl']:.2f}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    example_usage()
