#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多周期分析器 - 1m, 15m, 1h, 4h
"""

import logging
from typing import Dict
from utils.technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class MultiTimeframeAnalyzer:
    """多周期K线分析"""
    
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher
        self.tech_indicators = TechnicalIndicators()
    
    def analyze_all_timeframes(self, symbol: str) -> Dict:
        """分析所有时间周期"""
        timeframes = {
            '1m': {'interval': '1m', 'limit': 100},
            '15m': {'interval': '15m', 'limit': 100},
            '1h': {'interval': '1h', 'limit': 100},
            '4h': {'interval': '4h', 'limit': 50}
        }
        
        results = {}
        trends = []
        
        for tf_name, tf_config in timeframes.items():
            try:
                # 获取K线
                df = self.data_fetcher.fetch_klines(
                    symbol=symbol,
                    interval=tf_config['interval'],
                    limit=tf_config['limit']
                )
                
                if df is None or len(df) < 50:
                    results[tf_name] = self._default_result()
                    trends.append(0)
                    continue
                
                # 计算技术指标
                indicators = self.tech_indicators.calculate_all(df)
                
                # 判断趋势
                trend = self._determine_trend(indicators)
                trends.append(trend)
                
                results[tf_name] = {
                    'trend': trend,
                    'rsi': indicators['rsi'],
                    'macd_signal': indicators['macd_signal_text'],
                    'bb_position': indicators['bb_position']
                }
                
            except Exception as e:
                logger.warning(f"  {tf_name}周期分析失败: {e}")
                results[tf_name] = self._default_result()
                trends.append(0)
        
        # 趋势一致性
        if trends:
            # 计算主流趋势
            main_trend = max(set(trends), key=trends.count)
            consistency = trends.count(main_trend) / len(trends)
        else:
            main_trend = 0
            consistency = 0
        
        return {
            'timeframes': results,
            'trend_consistency': consistency,
            'overall_trend': main_trend,
            'trends_list': trends
        }
    
    def _determine_trend(self, indicators: Dict) -> int:
        """判断趋势方向"""
        score = 0
        
        # MACD信号
        if indicators['macd_signal_text'] == 'bullish':
            score += 1
        elif indicators['macd_signal_text'] == 'bearish':
            score -= 1
        
        # RSI
        if indicators['rsi'] > 50:
            score += 1
        else:
            score -= 1
        
        # EMA趋势
        score += indicators['ema_trend']
        
        # 布林带位置
        if indicators['bb_position'] > 0.6:
            score += 1
        elif indicators['bb_position'] < 0.4:
            score -= 1
        
        # 综合判断
        if score >= 2:
            return 1  # 上涨
        elif score <= -2:
            return -1  # 下跌
        else:
            return 0  # 震荡
    
    def _default_result(self) -> Dict:
        """默认结果"""
        return {
            'trend': 0,
            'rsi': 50,
            'macd_signal': 'neutral',
            'bb_position': 0.5
        }
