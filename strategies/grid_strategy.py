#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网格策略
适合：震荡市场
原理：设置价格网格，高抛低吸
"""

from .base_strategy import BaseStrategy
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class GridStrategy(BaseStrategy):
    """网格策略"""
    
    def __init__(self):
        super().__init__("网格策略")
        self.min_confidence = 65
        self.grid_levels = 5  # 网格层数
        self.grid_spacing = 0.02  # 网格间距2%
    
    def analyze(self, features: List[float], metadata: Dict) -> Dict:
        """
        生成网格交易信号
        
        原理：
        - 震荡市场最适合
        - 设置多个买卖网格
        - 价格下跌到网格 → 买入
        - 价格上涨到网格 → 卖出
        """
        try:
            # 提取特征
            current_price = metadata.get('current_price', 0)
            high_price = features[9] if len(features) > 9 else current_price
            low_price = features[10] if len(features) > 10 else current_price
            volatility = features[7] if len(features) > 7 else 0
            trend = features[8] if len(features) > 8 else 0
            price_change_24h = features[5] if len(features) > 5 else 0
            
            confidence = 50
            signal = 'NEUTRAL'
            reason = ""
            
            # 网格策略适合震荡市场
            if abs(price_change_24h) > 3.0 or volatility > 0.03:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': 0,
                    'reason': '波动过大，不适合网格策略'
                }
            
            if trend != 0:
                confidence -= 15
                reason = "有趋势，适合度降低"
            else:
                confidence += 20
                reason = "震荡市场，适合网格"
            
            # 计算价格在区间的位置
            price_range = high_price - low_price
            if price_range == 0:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': 0,
                    'reason': '价格无波动'
                }
            
            price_position = (current_price - low_price) / price_range
            
            # 低位买入
            if price_position < 0.3:
                signal = 'LONG'
                confidence += 20
                reason += "，价格处于低位"
                
                if price_position < 0.2:
                    confidence += 10
                    reason += "，极低位"
            
            # 高位卖出
            elif price_position > 0.7:
                signal = 'SHORT'
                confidence += 20
                reason += "，价格处于高位"
                
                if price_position > 0.8:
                    confidence += 10
                    reason += "，极高位"
            
            else:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': confidence,
                    'reason': f"价格在中间区域（位置={price_position:.2f}），等待网格触发"
                }
            
            # 计算网格
            center_price = (high_price + low_price) / 2
            
            if signal == 'LONG':
                # 买入网格
                buy_grids = [
                    center_price * (1 - self.grid_spacing * i)
                    for i in range(1, self.grid_levels + 1)
                ]
                
                stop_loss = low_price * 0.95  # 低点下方5%
                take_profit = [
                    center_price * 1.01,  # 中位上方1%
                    center_price * 1.02,  # 中位上方2%
                    center_price * 1.03   # 中位上方3%
                ]
                position_size_ratio = 0.10  # 每个网格10%仓位
                
                reason += f"，买入网格: {len(buy_grids)}层"
            
            elif signal == 'SHORT':
                # 卖出网格
                sell_grids = [
                    center_price * (1 + self.grid_spacing * i)
                    for i in range(1, self.grid_levels + 1)
                ]
                
                stop_loss = high_price * 1.05  # 高点上方5%
                take_profit = [
                    center_price * 0.99,  # 中位下方1%
                    center_price * 0.98,  # 中位下方2%
                    center_price * 0.97   # 中位下方3%
                ]
                position_size_ratio = 0.10
                
                reason += f"，卖出网格: {len(sell_grids)}层"
            
            return {
                'signal': signal,
                'confidence': min(confidence, 100),
                'reason': reason,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size_ratio': position_size_ratio,
                'grid_levels': self.grid_levels,
                'grid_spacing': self.grid_spacing
            }
            
        except Exception as e:
            logger.error(f"网格策略分析出错: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reason': f"分析出错: {e}"
            }
    
    def get_description(self) -> str:
        return """
网格策略
- 适合：震荡市场
- 原理：设置价格网格，高抛低吸
- 优势：震荡市场稳定盈利
- 劣势：趋势市场容易亏损
- 网格层数：5层
- 网格间距：2%
- 适合长期运行
"""
