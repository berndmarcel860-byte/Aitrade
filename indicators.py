"""
Technical Indicators Module
Calculates various technical indicators for trading decisions
"""
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange


class TechnicalIndicators:
    """Calculate technical indicators for trading analysis"""
    
    def __init__(self, df):
        """
        Initialize with OHLCV dataframe
        
        Args:
            df: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        self.df = df.copy()
        
    def calculate_rsi(self, period=14):
        """Calculate Relative Strength Index"""
        rsi = RSIIndicator(close=self.df['close'], window=period)
        self.df['rsi'] = rsi.rsi()
        return self.df['rsi'].iloc[-1]
    
    def calculate_macd(self, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        macd = MACD(close=self.df['close'], window_fast=fast, window_slow=slow, window_sign=signal)
        self.df['macd'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()
        self.df['macd_diff'] = macd.macd_diff()
        
        return {
            'macd': self.df['macd'].iloc[-1],
            'signal': self.df['macd_signal'].iloc[-1],
            'diff': self.df['macd_diff'].iloc[-1]
        }
    
    def calculate_bollinger_bands(self, period=20, std=2):
        """Calculate Bollinger Bands"""
        bb = BollingerBands(close=self.df['close'], window=period, window_dev=std)
        self.df['bb_upper'] = bb.bollinger_hband()
        self.df['bb_middle'] = bb.bollinger_mavg()
        self.df['bb_lower'] = bb.bollinger_lband()
        
        return {
            'upper': self.df['bb_upper'].iloc[-1],
            'middle': self.df['bb_middle'].iloc[-1],
            'lower': self.df['bb_lower'].iloc[-1]
        }
    
    def calculate_ema(self, short=9, medium=21, long=50):
        """Calculate Exponential Moving Averages"""
        ema_short = EMAIndicator(close=self.df['close'], window=short)
        ema_medium = EMAIndicator(close=self.df['close'], window=medium)
        ema_long = EMAIndicator(close=self.df['close'], window=long)
        
        self.df['ema_short'] = ema_short.ema_indicator()
        self.df['ema_medium'] = ema_medium.ema_indicator()
        self.df['ema_long'] = ema_long.ema_indicator()
        
        return {
            'short': self.df['ema_short'].iloc[-1],
            'medium': self.df['ema_medium'].iloc[-1],
            'long': self.df['ema_long'].iloc[-1]
        }
    
    def calculate_atr(self, period=14):
        """Calculate Average True Range for volatility"""
        atr = AverageTrueRange(high=self.df['high'], low=self.df['low'], close=self.df['close'], window=period)
        self.df['atr'] = atr.average_true_range()
        
        current_price = self.df['close'].iloc[-1]
        atr_value = self.df['atr'].iloc[-1]
        atr_percentage = (atr_value / current_price) * 100
        
        return {
            'atr': atr_value,
            'atr_percentage': atr_percentage
        }
    
    def get_all_indicators(self):
        """Calculate and return all indicators"""
        rsi = self.calculate_rsi()
        macd = self.calculate_macd()
        bb = self.calculate_bollinger_bands()
        ema = self.calculate_ema()
        atr = self.calculate_atr()
        
        return {
            'rsi': rsi,
            'macd': macd,
            'bollinger_bands': bb,
            'ema': ema,
            'atr': atr,
            'current_price': self.df['close'].iloc[-1]
        }
