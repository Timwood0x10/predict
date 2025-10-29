#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
突破策略
适合：盘整后突破
原理：价格突破关键位时入场
"""

from .base_strategy import BaseStrategy
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class BreakoutStrategy(BaseStrategy):
    """突破策略"""
    
    def __init__(self):
        super().__init__("突破策略")
        self.min_confidence = 75
    
    def analyze(self, features: List[float], metadata: Dict) -> Dict:
        """
        分析突破信号
        
        原理：
        - 价格接近最高价 → 向上突破 → 做多
        - 价格接近最低价 → 向下突破 → 做空
        """
        try:
            # 提取特征
            current_price = metadata.get('current_price', 0)
            high_price = features[9] if len(features) > 9 else current_price
            low_price = features[10] if len(features) > 10 else current_price
            open_price = features[11] if len(features) > 11 else current_price
            price_change_24h = features[5] if len(features) > 5 else 0
            volatility = features[7] if len(features) > 7 else 0
            volume = features[6] if len(features) > 6 else 0
            
            # 计算价格位置
            price_range = high_price - low_price
            if price_range == 0:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': 0,
                    'reason': '价格无波动'
                }
            
            price_position = (current_price - low_price) / price_range
            
            confidence = 50
            signal = 'NEUTRAL'
            reason = ""
            
            # 向上突破
            if price_position > 0.90 and price_change_24h > 1.5:
                signal = 'LONG'
                confidence += 25
                reason = "向上突破"
                
                # 接近最高价
                if price_position > 0.95:
                    confidence += 10
                    reason += "，创新高"
                
                # 涨幅强劲
                if price_change_24h > 3.0:
                    confidence += 10
                    reason += "，涨幅强劲"
                
                # 成交量配合
                if volume > metadata.get('avg_volume', volume):
                    confidence += 10
                    reason += "，成交量放大"
                
                # 低波动率（盘整后突破）
                if volatility < 0.02:
                    confidence += 10
                    reason += "，盘整后突破"
            
            # 向下突破
            elif price_position < 0.10 and price_change_24h < -1.5:
                signal = 'SHORT'
                confidence += 25
                reason = "向下突破"
                
                # 接近最低价
                if price_position < 0.05:
                    confidence += 10
                    reason += "，破新低"
                
                # 跌幅强劲
                if price_change_24h < -3.0:
                    confidence += 10
                    reason += "，跌幅强劲"
                
                # 成交量配合
                if volume > metadata.get('avg_volume', volume):
                    confidence += 10
                    reason += "，成交量放大"
                
                # 低波动率
                if volatility < 0.02:
                    confidence += 10
                    reason += "，盘整后突破"
            
            else:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': confidence,
                    'reason': f"未出现突破（价格位置={price_position:.2f}, 涨跌={price_change_24h:.2f}%）"
                }
            
            # 计算止损止盈
            if signal == 'LONG':
                stop_loss = low_price * 0.995  # 最低价下方0.5%
                take_profit = [
                    current_price * 1.04,
                    current_price * 1.07,
                    current_price * 1.12
                ]
                position_size_ratio = 0.20  # 20%仓位（突破信号较强）
            
            elif signal == 'SHORT':
                stop_loss = high_price * 1.005  # 最高价上方0.5%
                take_profit = [
                    current_price * 0.96,
                    current_price * 0.93,
                    current_price * 0.88
                ]
                position_size_ratio = 0.20
            
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
            logger.error(f"突破策略分析出错: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reason': f"分析出错: {e}"
            }
    
    def get_description(self) -> str:
        return """
突破策略
- 适合：盘整后突破
- 原理：价格突破关键位时入场
- 优势：捕捉趋势起点
- 劣势：假突破风险
- 止损：关键位外0.5%
- 止盈：4% / 7% / 12%
"""
