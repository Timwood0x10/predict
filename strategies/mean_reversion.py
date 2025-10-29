#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
均值回归策略
适合：震荡市场
原理：价格偏离均值后会回归
"""

from .base_strategy import BaseStrategy
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    
    def __init__(self):
        super().__init__("均值回归")
        self.min_confidence = 70
    
    def analyze(self, features: List[float], metadata: Dict) -> Dict:
        """
        分析价格偏离并生成信号
        
        原理：
        - 价格大幅下跌 → 可能超卖 → 做多
        - 价格大幅上涨 → 可能超买 → 做空
        """
        try:
            # 提取特征
            price_change_24h = features[5] if len(features) > 5 else 0
            volatility = features[7] if len(features) > 7 else 0
            rsi_norm = features[12] if len(features) > 12 else 0.5
            trend = features[8] if len(features) > 8 else 0
            current_price = metadata.get('current_price', 0)
            
            confidence = 50
            signal = 'NEUTRAL'
            reason = ""
            
            # 超卖反弹（做多）
            if price_change_24h < -2.5 and rsi_norm < 0.35:
                signal = 'LONG'
                confidence += 25
                reason = "价格超卖"
                
                # 下跌幅度越大，反弹概率越高
                if price_change_24h < -4.0:
                    confidence += 15
                    reason += "，深度超卖"
                elif price_change_24h < -3.0:
                    confidence += 10
                    reason += "，明显超卖"
                
                # RSI极低
                if rsi_norm < 0.25:
                    confidence += 10
                    reason += "，RSI极低"
                
                # 非下跌趋势（避免接飞刀）
                if trend != -1:
                    confidence += 5
                    reason += "，非下跌趋势"
                else:
                    confidence -= 10
                    reason += "，但仍在下跌趋势中"
            
            # 超买回调（做空）
            elif price_change_24h > 3.0 and rsi_norm > 0.65:
                signal = 'SHORT'
                confidence += 25
                reason = "价格超买"
                
                # 上涨幅度越大，回调概率越高
                if price_change_24h > 5.0:
                    confidence += 15
                    reason += "，严重超买"
                elif price_change_24h > 4.0:
                    confidence += 10
                    reason += "，明显超买"
                
                # RSI极高
                if rsi_norm > 0.75:
                    confidence += 10
                    reason += "，RSI极高"
                
                # 非上涨趋势
                if trend != 1:
                    confidence += 5
                    reason += "，非上涨趋势"
                else:
                    confidence -= 10
                    reason += "，但仍在上涨趋势中"
            
            else:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': confidence,
                    'reason': f"价格未严重偏离（涨跌={price_change_24h:.2f}%, RSI={rsi_norm:.2f}）"
                }
            
            # 计算止损止盈
            if signal == 'LONG':
                stop_loss = current_price * 0.975  # 2.5%止损（偏小，因为是抄底）
                take_profit = [
                    current_price * 1.03,   # 3%
                    current_price * 1.05,   # 5%
                    current_price * 1.08    # 8%
                ]
                position_size_ratio = 0.10  # 10%仓位（抄底风险大）
            
            elif signal == 'SHORT':
                stop_loss = current_price * 1.025  # 2.5%止损
                take_profit = [
                    current_price * 0.97,   # 3%
                    current_price * 0.95,   # 5%
                    current_price * 0.92    # 8%
                ]
                position_size_ratio = 0.10  # 10%仓位
            
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
            logger.error(f"均值回归策略分析出错: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reason': f"分析出错: {e}"
            }
    
    def get_description(self) -> str:
        return """
均值回归策略
- 适合：震荡市场
- 原理：价格偏离均值后会回归
- 优势：捕捉反弹机会
- 劣势：趋势市场容易接飞刀
- 止损：2.5%（严格）
- 止盈：3% / 5% / 8%
"""
