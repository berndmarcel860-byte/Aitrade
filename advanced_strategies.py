"""
Advanced Trading Strategies
Professional strategies for different market conditions
"""
import numpy as np
from indicators import TechnicalIndicators
import config


class ScalpingStrategy:
    """
    Aggressive scalping strategy for quick profits
    Focuses on short-term price movements with tight stops
    """
    
    def __init__(self, df):
        self.df = df
        self.indicators = TechnicalIndicators(df)
        self.indicator_values = self.indicators.get_all_indicators()
    
    def check_trend(self):
        """Quick trend detection for scalping"""
        ema = self.indicator_values['ema']
        if ema['short'] > ema['medium']:
            return 'UPTREND'
        elif ema['short'] < ema['medium']:
            return 'DOWNTREND'
        return 'SIDEWAYS'
    
    def check_volatility(self):
        """High volatility preferred for scalping"""
        atr = self.indicator_values['atr']
        is_suitable = atr['atr_percentage'] >= 0.3  # Lower threshold for scalping
        return {
            'is_suitable': is_suitable,
            'atr': atr['atr'],
            'atr_percentage': atr['atr_percentage'],
            'status': 'HIGH' if atr['atr_percentage'] >= 1.0 else 'MEDIUM' if is_suitable else 'LOW'
        }
    
    def check_direction(self):
        """Scalping direction with momentum focus"""
        rsi = self.indicator_values['rsi']
        macd = self.indicator_values['macd']
        current_price = self.indicator_values['current_price']
        
        # Scalping looks for quick reversals
        if rsi < 35 and macd['diff'] > 0:
            return 'LONG'
        elif rsi > 65 and macd['diff'] < 0:
            return 'SHORT'
        return 'NEUTRAL'
    
    def calculate_price_ranges(self, direction):
        """Tighter ranges for scalping"""
        current_price = self.indicator_values['current_price']
        atr = self.indicator_values['atr']['atr']
        
        if direction == 'LONG':
            entry_low = current_price - (atr * 0.2)
            entry_high = current_price + (atr * 0.1)
            tp1 = current_price + (atr * 1.0)  # Quick profit target
            tp2 = current_price + (atr * 1.5)
            tp3 = current_price + (atr * 2.0)
            stop_loss = current_price - (atr * 1.0)  # Tight stop
        else:
            entry_low = current_price - (atr * 0.1)
            entry_high = current_price + (atr * 0.2)
            tp1 = current_price - (atr * 1.0)
            tp2 = current_price - (atr * 1.5)
            tp3 = current_price - (atr * 2.0)
            stop_loss = current_price + (atr * 1.0)
        
        return {
            'entry_low': round(entry_low, 2),
            'entry_high': round(entry_high, 2),
            'tp1': round(tp1, 2),
            'tp2': round(tp2, 2),
            'tp3': round(tp3, 2),
            'stop_loss': round(stop_loss, 2)
        }
    
    def generate_signal(self):
        """Generate scalping signal"""
        volatility = self.check_volatility()
        if not volatility['is_suitable']:
            return None
        
        direction = self.check_direction()
        if direction == 'NEUTRAL':
            return None
        
        price_ranges = self.calculate_price_ranges(direction)
        
        signal = {
            'strategy': 'Scalping',
            'direction': direction,
            'trend': self.check_trend(),
            'volatility': volatility,
            'current_price': round(self.indicator_values['current_price'], 2),
            'entry_range': f"{price_ranges['entry_low']} - {price_ranges['entry_high']}",
            'take_profit': f"TP1: {price_ranges['tp1']} | TP2: {price_ranges['tp2']} | TP3: {price_ranges['tp3']}",
            'stop_loss': price_ranges['stop_loss'],
            'rsi': round(self.indicator_values['rsi'], 2),
            'macd': {
                'value': round(self.indicator_values['macd']['macd'], 2),
                'signal': round(self.indicator_values['macd']['signal'], 2),
                'histogram': round(self.indicator_values['macd']['diff'], 2)
            },
            'leverage': config.LEVERAGE,
            'position_size': config.POSITION_SIZE_USDT
        }
        
        return signal


class SwingStrategy:
    """
    Swing trading strategy for medium-term positions
    Holds positions for multiple days
    """
    
    def __init__(self, df):
        self.df = df
        self.indicators = TechnicalIndicators(df)
        self.indicator_values = self.indicators.get_all_indicators()
    
    def check_trend(self):
        """Strong trend confirmation for swing trading"""
        ema = self.indicator_values['ema']
        
        # All EMAs aligned
        if ema['short'] > ema['medium'] > ema['long']:
            # Check slope strength
            if (ema['short'] - ema['long']) / ema['long'] > 0.02:  # 2% gap
                return 'STRONG_UPTREND'
            return 'UPTREND'
        elif ema['short'] < ema['medium'] < ema['long']:
            if (ema['long'] - ema['short']) / ema['long'] > 0.02:
                return 'STRONG_DOWNTREND'
            return 'DOWNTREND'
        return 'SIDEWAYS'
    
    def check_direction(self):
        """Swing direction with strong confirmation"""
        rsi = self.indicator_values['rsi']
        macd = self.indicator_values['macd']
        bb = self.indicator_values['bollinger_bands']
        current_price = self.indicator_values['current_price']
        trend = self.check_trend()
        
        long_signals = 0
        short_signals = 0
        
        # RSI in favorable zone (not extreme)
        if 40 < rsi < 60:
            if rsi < 50:
                long_signals += 1
            else:
                short_signals += 1
        
        # Strong MACD
        if macd['diff'] > 20:
            long_signals += 2
        elif macd['diff'] < -20:
            short_signals += 2
        
        # Price position in Bollinger Bands
        bb_range = bb['upper'] - bb['lower']
        price_position = (current_price - bb['lower']) / bb_range
        if price_position < 0.3:
            long_signals += 1
        elif price_position > 0.7:
            short_signals += 1
        
        # Strong trend confirmation
        if 'STRONG_UPTREND' in trend:
            long_signals += 3
        elif 'STRONG_DOWNTREND' in trend:
            short_signals += 3
        
        if long_signals >= 4:
            return 'LONG'
        elif short_signals >= 4:
            return 'SHORT'
        return 'NEUTRAL'
    
    def calculate_price_ranges(self, direction):
        """Wider ranges for swing trading"""
        current_price = self.indicator_values['current_price']
        atr = self.indicator_values['atr']['atr']
        bb = self.indicator_values['bollinger_bands']
        
        if direction == 'LONG':
            entry_low = current_price - (atr * 1.0)
            entry_high = current_price + (atr * 0.5)
            tp1 = current_price + (atr * 3.0)
            tp2 = current_price + (atr * 5.0)
            tp3 = max(bb['upper'], current_price + (atr * 7.0))
            stop_loss = current_price - (atr * 2.5)
        else:
            entry_low = current_price - (atr * 0.5)
            entry_high = current_price + (atr * 1.0)
            tp1 = current_price - (atr * 3.0)
            tp2 = current_price - (atr * 5.0)
            tp3 = min(bb['lower'], current_price - (atr * 7.0))
            stop_loss = current_price + (atr * 2.5)
        
        return {
            'entry_low': round(entry_low, 2),
            'entry_high': round(entry_high, 2),
            'tp1': round(tp1, 2),
            'tp2': round(tp2, 2),
            'tp3': round(tp3, 2),
            'stop_loss': round(stop_loss, 2)
        }
    
    def generate_signal(self):
        """Generate swing trading signal"""
        atr = self.indicator_values['atr']
        if atr['atr_percentage'] < 0.5:  # Need some volatility
            return None
        
        direction = self.check_direction()
        if direction == 'NEUTRAL':
            return None
        
        price_ranges = self.calculate_price_ranges(direction)
        
        signal = {
            'strategy': 'Swing Trading',
            'direction': direction,
            'trend': self.check_trend(),
            'current_price': round(self.indicator_values['current_price'], 2),
            'entry_range': f"{price_ranges['entry_low']} - {price_ranges['entry_high']}",
            'take_profit': f"TP1: {price_ranges['tp1']} | TP2: {price_ranges['tp2']} | TP3: {price_ranges['tp3']}",
            'stop_loss': price_ranges['stop_loss'],
            'leverage': max(1, config.LEVERAGE // 2),  # Lower leverage for swing
            'position_size': config.POSITION_SIZE_USDT
        }
        
        return signal


class BreakoutStrategy:
    """
    Breakout strategy - trades when price breaks key levels
    """
    
    def __init__(self, df):
        self.df = df
        self.indicators = TechnicalIndicators(df)
        self.indicator_values = self.indicators.get_all_indicators()
    
    def detect_breakout(self):
        """Detect if price is breaking out"""
        bb = self.indicator_values['bollinger_bands']
        current_price = self.indicator_values['current_price']
        atr = self.indicator_values['atr']
        
        # Calculate recent high/low
        recent_data = self.df.tail(20)
        resistance = recent_data['high'].max()
        support = recent_data['low'].min()
        
        # Check for breakout
        if current_price > bb['upper'] and current_price > resistance:
            return 'BULLISH_BREAKOUT'
        elif current_price < bb['lower'] and current_price < support:
            return 'BEARISH_BREAKOUT'
        
        # Consolidation before potential breakout
        price_range = resistance - support
        if price_range / current_price < 0.02 and atr['atr_percentage'] < 0.5:
            return 'CONSOLIDATION'
        
        return 'NO_BREAKOUT'
    
    def generate_signal(self):
        """Generate breakout signal"""
        breakout_type = self.detect_breakout()
        macd = self.indicator_values['macd']
        current_price = self.indicator_values['current_price']
        atr = self.indicator_values['atr']['atr']
        
        if breakout_type == 'BULLISH_BREAKOUT' and macd['diff'] > 0:
            direction = 'LONG'
        elif breakout_type == 'BEARISH_BREAKOUT' and macd['diff'] < 0:
            direction = 'SHORT'
        else:
            return None
        
        # Aggressive entries on breakouts
        if direction == 'LONG':
            entry_low = current_price
            entry_high = current_price + (atr * 0.3)
            tp1 = current_price + (atr * 2.5)
            tp2 = current_price + (atr * 4.0)
            tp3 = current_price + (atr * 6.0)
            stop_loss = current_price - (atr * 1.5)
        else:
            entry_low = current_price - (atr * 0.3)
            entry_high = current_price
            tp1 = current_price - (atr * 2.5)
            tp2 = current_price - (atr * 4.0)
            tp3 = current_price - (atr * 6.0)
            stop_loss = current_price + (atr * 1.5)
        
        signal = {
            'strategy': 'Breakout',
            'direction': direction,
            'breakout_type': breakout_type,
            'current_price': round(current_price, 2),
            'entry_range': f"{round(entry_low, 2)} - {round(entry_high, 2)}",
            'take_profit': f"TP1: {round(tp1, 2)} | TP2: {round(tp2, 2)} | TP3: {round(tp3, 2)}",
            'stop_loss': round(stop_loss, 2),
            'leverage': config.LEVERAGE,
            'position_size': config.POSITION_SIZE_USDT
        }
        
        return signal


class MeanReversionStrategy:
    """
    Mean reversion strategy - trades when price deviates from mean
    """
    
    def __init__(self, df):
        self.df = df
        self.indicators = TechnicalIndicators(df)
        self.indicator_values = self.indicators.get_all_indicators()
    
    def check_deviation(self):
        """Check if price has deviated significantly from mean"""
        bb = self.indicator_values['bollinger_bands']
        current_price = self.indicator_values['current_price']
        rsi = self.indicator_values['rsi']
        
        # Calculate deviation from middle band
        deviation = (current_price - bb['middle']) / bb['middle'] * 100
        
        # Extreme oversold - expect reversion up
        if current_price < bb['lower'] and rsi < 30:
            return 'OVERSOLD', abs(deviation)
        # Extreme overbought - expect reversion down
        elif current_price > bb['upper'] and rsi > 70:
            return 'OVERBOUGHT', abs(deviation)
        
        return 'NEUTRAL', 0
    
    def generate_signal(self):
        """Generate mean reversion signal"""
        condition, deviation = self.check_deviation()
        
        if condition == 'NEUTRAL' or deviation < 1.5:  # Need significant deviation
            return None
        
        current_price = self.indicator_values['current_price']
        bb = self.indicator_values['bollinger_bands']
        atr = self.indicator_values['atr']['atr']
        
        if condition == 'OVERSOLD':
            direction = 'LONG'
            entry_low = current_price - (atr * 0.3)
            entry_high = current_price + (atr * 0.2)
            tp1 = bb['middle']  # Revert to mean
            tp2 = bb['middle'] + (atr * 1.0)
            tp3 = bb['upper']
            stop_loss = bb['lower'] - (atr * 0.5)
        else:  # OVERBOUGHT
            direction = 'SHORT'
            entry_low = current_price - (atr * 0.2)
            entry_high = current_price + (atr * 0.3)
            tp1 = bb['middle']
            tp2 = bb['middle'] - (atr * 1.0)
            tp3 = bb['lower']
            stop_loss = bb['upper'] + (atr * 0.5)
        
        signal = {
            'strategy': 'Mean Reversion',
            'direction': direction,
            'condition': condition,
            'deviation': round(deviation, 2),
            'current_price': round(current_price, 2),
            'entry_range': f"{round(entry_low, 2)} - {round(entry_high, 2)}",
            'take_profit': f"TP1: {round(tp1, 2)} | TP2: {round(tp2, 2)} | TP3: {round(tp3, 2)}",
            'stop_loss': round(stop_loss, 2),
            'leverage': config.LEVERAGE,
            'position_size': config.POSITION_SIZE_USDT
        }
        
        return signal
