#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算器 - MACD, RSI, 布林带, EMA, ATR
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """专业技术指标计算"""
    
    def calculate_all(self, df: pd.DataFrame) -> dict:
        """
        计算所有技术指标
        
        Args:
            df: K线数据（需要包含 open, high, low, close, volume）
            
        Returns:
            {
                'macd_line': float,
                'macd_signal': float,
                'macd_hist': float,
                'rsi': float,
                'bb_position': float,
                'ema_trend': int
            }
        """
        try:
            if len(df) < 50:
                logger.warning("数据不足50根K线，指标可能不准确")
                return self._default_indicators()
            
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values
            
            # MACD
            macd_data = self._calculate_macd(close)
            
            # RSI
            rsi_value = self._calculate_rsi(close)
            
            # 布林带
            bb_data = self._calculate_bollinger_bands(close)
            
            # EMA
            ema_data = self._calculate_ema(close)
            
            return {
                'macd_line': macd_data['line'],
                'macd_signal': macd_data['signal'],
                'macd_hist': macd_data['hist'],
                'rsi': rsi_value,
                'bb_position': bb_data['position'],
                'ema_trend': ema_data['trend'],
                
                # 辅助信息
                'macd_signal_text': macd_data['signal_text'],
                'rsi_signal': self._get_rsi_signal(rsi_value),
                'bb_signal': bb_data['signal']
            }
            
        except Exception as e:
            logger.error(f"技术指标计算失败: {e}")
            return self._default_indicators()
    
    def _calculate_macd(self, close: np.ndarray) -> dict:
        """计算MACD指标"""
        try:
            import talib as ta
            macd_line, signal_line, hist = ta.MACD(
                close,
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            
            macd_val = float(macd_line[-1]) if not np.isnan(macd_line[-1]) else 0
            signal_val = float(signal_line[-1]) if not np.isnan(signal_line[-1]) else 0
            hist_val = float(hist[-1]) if not np.isnan(hist[-1]) else 0
            
            # 判断信号
            if macd_val > signal_val and hist_val > 0:
                signal_text = 'bullish'  # 金叉
            elif macd_val < signal_val and hist_val < 0:
                signal_text = 'bearish'  # 死叉
            else:
                signal_text = 'neutral'
            
            return {
                'line': macd_val,
                'signal': signal_val,
                'hist': hist_val,
                'signal_text': signal_text
            }
        except ImportError:
            # 如果没有talib，使用pandas实现
            return self._calculate_macd_pandas(close)
    
    def _calculate_macd_pandas(self, close: np.ndarray) -> dict:
        """使用pandas计算MACD（talib不可用时）"""
        close_series = pd.Series(close)
        
        # 快线EMA
        ema_12 = close_series.ewm(span=12, adjust=False).mean()
        # 慢线EMA
        ema_26 = close_series.ewm(span=26, adjust=False).mean()
        # MACD线
        macd_line = ema_12 - ema_26
        # 信号线
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        # 柱状图
        hist = macd_line - signal_line
        
        macd_val = float(macd_line.iloc[-1])
        signal_val = float(signal_line.iloc[-1])
        hist_val = float(hist.iloc[-1])
        
        signal_text = 'bullish' if macd_val > signal_val else 'bearish'
        
        return {
            'line': macd_val,
            'signal': signal_val,
            'hist': hist_val,
            'signal_text': signal_text
        }
    
    def _calculate_rsi(self, close: np.ndarray, period: int = 14) -> float:
        """计算RSI指标"""
        try:
            import talib as ta
            rsi = ta.RSI(close, timeperiod=period)
            return float(rsi[-1]) if not np.isnan(rsi[-1]) else 50.0
        except ImportError:
            return self._calculate_rsi_pandas(close, period)
    
    def _calculate_rsi_pandas(self, close: np.ndarray, period: int = 14) -> float:
        """使用pandas计算RSI"""
        close_series = pd.Series(close)
        delta = close_series.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0
    
    def _calculate_bollinger_bands(self, close: np.ndarray, period: int = 20, std: int = 2) -> dict:
        """计算布林带"""
        try:
            import talib as ta
            upper, middle, lower = ta.BBANDS(
                close,
                timeperiod=period,
                nbdevup=std,
                nbdevdn=std
            )
            
            upper_val = float(upper[-1]) if not np.isnan(upper[-1]) else close[-1] * 1.02
            middle_val = float(middle[-1]) if not np.isnan(middle[-1]) else close[-1]
            lower_val = float(lower[-1]) if not np.isnan(lower[-1]) else close[-1] * 0.98
            
        except ImportError:
            # pandas实现
            close_series = pd.Series(close)
            middle_val = float(close_series.rolling(window=period).mean().iloc[-1])
            std_val = float(close_series.rolling(window=period).std().iloc[-1])
            upper_val = middle_val + (std * std_val)
            lower_val = middle_val - (std * std_val)
        
        # 计算当前价格在布林带中的位置 (0=下轨, 0.5=中轨, 1=上轨)
        current_price = close[-1]
        bb_width = upper_val - lower_val
        if bb_width > 0:
            position = (current_price - lower_val) / bb_width
        else:
            position = 0.5
        
        position = max(0, min(1, position))  # 限制在[0,1]
        
        # 判断信号
        if position < 0.2:
            signal = 'lower'  # 接近下轨
        elif position > 0.8:
            signal = 'upper'  # 接近上轨
        else:
            signal = 'middle'
        
        return {
            'position': position,
            'signal': signal,
            'upper': upper_val,
            'middle': middle_val,
            'lower': lower_val
        }
    
    def _calculate_ema(self, close: np.ndarray) -> dict:
        """计算EMA指标"""
        try:
            import talib as ta
            ema_20 = ta.EMA(close, timeperiod=20)
            ema_50 = ta.EMA(close, timeperiod=50)
            
            ema20_current = float(ema_20[-1]) if not np.isnan(ema_20[-1]) else close[-1]
            ema20_prev = float(ema_20[-2]) if len(ema_20) > 1 and not np.isnan(ema_20[-2]) else close[-1]
            ema50_current = float(ema_50[-1]) if not np.isnan(ema_50[-1]) else close[-1]
            ema50_prev = float(ema_50[-2]) if len(ema_50) > 1 and not np.isnan(ema_50[-2]) else close[-1]
            
        except ImportError:
            # pandas实现
            close_series = pd.Series(close)
            ema_20 = close_series.ewm(span=20, adjust=False).mean()
            ema_50 = close_series.ewm(span=50, adjust=False).mean()
            
            ema20_current = float(ema_20.iloc[-1])
            ema20_prev = float(ema_20.iloc[-2]) if len(ema_20) > 1 else ema20_current
            ema50_current = float(ema_50.iloc[-1])
            ema50_prev = float(ema_50.iloc[-2]) if len(ema_50) > 1 else ema50_current
        
        # 判断EMA趋势
        if ema20_current > ema50_current and ema20_prev <= ema50_prev:
            trend = 1  # 金叉
        elif ema20_current < ema50_current and ema20_prev >= ema50_prev:
            trend = -1  # 死叉
        elif ema20_current > ema50_current:
            trend = 1  # 多头排列
        elif ema20_current < ema50_current:
            trend = -1  # 空头排列
        else:
            trend = 0
        
        return {
            'trend': trend,
            'ema_20': ema20_current,
            'ema_50': ema50_current
        }
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """获取RSI信号"""
        if rsi < 30:
            return 'oversold'  # 超卖
        elif rsi > 70:
            return 'overbought'  # 超买
        else:
            return 'neutral'
    
    def _default_indicators(self) -> dict:
        """默认指标值"""
        return {
            'macd_line': 0,
            'macd_signal': 0,
            'macd_hist': 0,
            'rsi': 50,
            'bb_position': 0.5,
            'ema_trend': 0,
            'macd_signal_text': 'neutral',
            'rsi_signal': 'neutral',
            'bb_signal': 'middle'
        }
