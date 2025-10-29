#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
趋势跟踪策略
适合：强趋势市场
原理：顺势而为，趋势确立后入场
"""

from .base_strategy import BaseStrategy
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class TrendFollowingStrategy(BaseStrategy):
    """趋势跟踪策略"""
    
    def __init__(self):
        super().__init__("趋势跟踪")
        self.min_confidence = 75  # 需要高置信度
    
    def analyze(self, features: List[float], metadata: Dict) -> Dict:
        """
        分析趋势并生成信号
        
        特征索引:
        [8] 趋势 (1=上涨, -1=下跌, 0=平稳)
        [5] 24h涨跌幅
        [7] 波动率
        [12] RSI归一化
        """
        try:
            # 提取特征
            trend = features[8] if len(features) > 8 else 0
            price_change_24h = features[5] if len(features) > 5 else 0
            volatility = features[7] if len(features) > 7 else 0
            rsi_norm = features[12] if len(features) > 12 else 0.5
            current_price = metadata.get('current_price', 0)
            
            # 计算信号
            confidence = 50
            signal = 'NEUTRAL'
            reason = ""
            
            # 上涨趋势
            if trend == 1 and price_change_24h > 1.0:
                signal = 'LONG'
                confidence += 20
                reason = "明确上涨趋势"
                
                # 涨幅适中（不追高）
                if 1.0 < price_change_24h < 3.0:
                    confidence += 10
                    reason += "，涨幅适中"
                elif price_change_24h >= 3.0:
                    confidence += 5
                    reason += "，涨幅较大"
                
                # RSI未超买
                if rsi_norm < 0.7:
                    confidence += 10
                    reason += "，RSI健康"
                
                # 波动率适中
                if volatility < 0.03:
                    confidence += 10
                    reason += "，波动可控"
            
            # 下跌趋势
            elif trend == -1 and price_change_24h < -1.0:
                signal = 'SHORT'
                confidence += 20
                reason = "明确下跌趋势"
                
                # 跌幅适中
                if -3.0 < price_change_24h < -1.0:
                    confidence += 10
                    reason += "，跌幅适中"
                elif price_change_24h <= -3.0:
                    confidence += 5
                    reason += "，跌幅较大"
                
                # RSI未超卖
                if rsi_norm > 0.3:
                    confidence += 10
                    reason += "，RSI健康"
                
                # 波动率适中
                if volatility < 0.03:
                    confidence += 10
                    reason += "，波动可控"
            
            # 趋势不明确
            else:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': confidence,
                    'reason': f"趋势不明确（趋势={trend}, 涨跌={price_change_24h:.2f}%）"
                }
            
            # 计算止损止盈
            if signal == 'LONG':
                stop_loss = current_price * 0.97  # 3%止损
                take_profit = [
                    current_price * 1.045,  # 4.5%
                    current_price * 1.075,  # 7.5%
                    current_price * 1.12    # 12%
                ]
                position_size_ratio = 0.15  # 15%仓位
            
            elif signal == 'SHORT':
                stop_loss = current_price * 1.03  # 3%止损
                take_profit = [
                    current_price * 0.955,  # 4.5%
                    current_price * 0.925,  # 7.5%
                    current_price * 0.88    # 12%
                ]
                position_size_ratio = 0.15  # 15%仓位
            
            return {
                'signal': signal,
                'confidence': min(confidence, 100),
                'reason': reason,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size_ratio': position_size_ratio
            }
            
        except Exception as e:
            logger.error(f"趋势跟踪策略分析出错: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reason': f"分析出错: {e}"
            }
    
    def get_description(self) -> str:
        return """
趋势跟踪策略
- 适合：强趋势市场
- 原理：顺势而为，趋势确立后入场
- 优势：捕捉大行情，风险收益比高
- 劣势：震荡市场表现差
- 止损：3%
- 止盈：4.5% / 7.5% / 12%
"""
