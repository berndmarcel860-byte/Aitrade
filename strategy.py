"""
Trading Strategy Module
Analyzes market conditions and generates trading signals
"""
import numpy as np
from indicators import TechnicalIndicators
import config


class TradingStrategy:
    """Generate trading signals based on multiple indicators"""
    
    def __init__(self, df):
        """
        Initialize with OHLCV dataframe
        
        Args:
            df: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        self.df = df
        self.indicators = TechnicalIndicators(df)
        self.indicator_values = self.indicators.get_all_indicators()
        
    def check_trend(self):
        """
        Determine market trend using EMA crossovers
        
        Returns:
            str: 'UPTREND', 'DOWNTREND', or 'SIDEWAYS'
        """
        ema = self.indicator_values['ema']
        
        # Strong uptrend: EMA short > medium > long
        if ema['short'] > ema['medium'] > ema['long']:
            return 'UPTREND'
        # Strong downtrend: EMA short < medium < long
        elif ema['short'] < ema['medium'] < ema['long']:
            return 'DOWNTREND'
        else:
            return 'SIDEWAYS'
    
    def check_volatility(self):
        """
        Check if market volatility is suitable for trading
        
        Returns:
            dict: Volatility status and ATR values
        """
        atr = self.indicator_values['atr']
        
        is_volatile = atr['atr_percentage'] >= config.MIN_VOLATILITY
        
        return {
            'is_suitable': is_volatile,
            'atr': atr['atr'],
            'atr_percentage': atr['atr_percentage'],
            'status': 'HIGH' if atr['atr_percentage'] >= 1.0 else 'MEDIUM' if is_volatile else 'LOW'
        }
    
    def check_direction(self):
        """
        Determine if trade should be LONG or SHORT
        
        Returns:
            str: 'LONG', 'SHORT', or 'NEUTRAL'
        """
        rsi = self.indicator_values['rsi']
        macd = self.indicator_values['macd']
        bb = self.indicator_values['bollinger_bands']
        current_price = self.indicator_values['current_price']
        trend = self.check_trend()
        
        long_signals = 0
        short_signals = 0
        
        # RSI signals
        if rsi < config.RSI_OVERSOLD:
            long_signals += 2
        elif rsi < 45:
            long_signals += 1
        elif rsi > config.RSI_OVERBOUGHT:
            short_signals += 2
        elif rsi > 55:
            short_signals += 1
        
        # MACD signals
        if macd['diff'] > 0 and macd['macd'] > macd['signal']:
            long_signals += 2
        elif macd['diff'] < 0 and macd['macd'] < macd['signal']:
            short_signals += 2
        
        # Bollinger Bands signals
        if current_price <= bb['lower']:
            long_signals += 1
        elif current_price >= bb['upper']:
            short_signals += 1
        
        # Trend confirmation
        if trend == 'UPTREND':
            long_signals += 2
        elif trend == 'DOWNTREND':
            short_signals += 2
        
        # Decision logic
        if long_signals >= 5 and long_signals > short_signals:
            return 'LONG'
        elif short_signals >= 5 and short_signals > long_signals:
            return 'SHORT'
        else:
            return 'NEUTRAL'
    
    def calculate_price_ranges(self, direction):
        """
        Calculate entry, take profit, and stop loss levels
        
        Args:
            direction: 'LONG' or 'SHORT'
            
        Returns:
            dict: Entry range, profit targets, and stop loss
        """
        current_price = self.indicator_values['current_price']
        atr = self.indicator_values['atr']['atr']
        bb = self.indicator_values['bollinger_bands']
        
        # Calculate based on ATR and Bollinger Bands
        if direction == 'LONG':
            entry_low = current_price - (atr * 0.5)
            entry_high = current_price + (atr * 0.3)
            
            # Multiple take profit targets
            tp1 = current_price + (atr * 2)
            tp2 = current_price + (atr * 3)
            tp3 = bb['upper'] if bb['upper'] > tp2 else current_price + (atr * 4)
            
            stop_loss = current_price - (atr * 1.5)
            
        else:  # SHORT
            entry_low = current_price - (atr * 0.3)
            entry_high = current_price + (atr * 0.5)
            
            # Multiple take profit targets
            tp1 = current_price - (atr * 2)
            tp2 = current_price - (atr * 3)
            tp3 = bb['lower'] if bb['lower'] < tp2 else current_price - (atr * 4)
            
            stop_loss = current_price + (atr * 1.5)
        
        return {
            'entry_low': round(entry_low, 2),
            'entry_high': round(entry_high, 2),
            'tp1': round(tp1, 2),
            'tp2': round(tp2, 2),
            'tp3': round(tp3, 2),
            'stop_loss': round(stop_loss, 2)
        }
    
    def calculate_risk_reward(self, direction, price_ranges):
        """
        Calculate risk-reward ratio
        
        Args:
            direction: 'LONG' or 'SHORT'
            price_ranges: Dict with entry and exit levels
            
        Returns:
            dict: Risk-reward metrics
        """
        current_price = self.indicator_values['current_price']
        entry_avg = (price_ranges['entry_low'] + price_ranges['entry_high']) / 2
        
        if direction == 'LONG':
            risk = entry_avg - price_ranges['stop_loss']
            reward = price_ranges['tp2'] - entry_avg
        else:
            risk = price_ranges['stop_loss'] - entry_avg
            reward = entry_avg - price_ranges['tp2']
        
        rr_ratio = reward / risk if risk > 0 else 0
        
        return {
            'risk': round(risk, 2),
            'reward': round(reward, 2),
            'rr_ratio': round(rr_ratio, 2)
        }
    
    def generate_signal(self):
        """
        Generate complete trading signal with all analysis
        
        Returns:
            dict: Complete trading signal or None if no valid signal
        """
        # Check volatility first
        volatility = self.check_volatility()
        if not volatility['is_suitable']:
            return None
        
        # Check trend
        trend = self.check_trend()
        
        # Check direction
        direction = self.check_direction()
        
        if direction == 'NEUTRAL':
            return None
        
        # Calculate price ranges
        price_ranges = self.calculate_price_ranges(direction)
        
        # Calculate risk-reward
        risk_reward = self.calculate_risk_reward(direction, price_ranges)
        
        # Only take trades with good risk-reward ratio
        if risk_reward['rr_ratio'] < 1.5:
            return None
        
        signal = {
            'direction': direction,
            'trend': trend,
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
            'risk_reward': risk_reward,
            'leverage': config.LEVERAGE,
            'position_size': config.POSITION_SIZE_USDT
        }
        
        return signal
