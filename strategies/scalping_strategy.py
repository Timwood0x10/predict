#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剥头皮策略（超短线）
适合：高频交易，快进快出
原理：捕捉小幅波动，积少成多
"""

from .base_strategy import BaseStrategy
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ScalpingStrategy(BaseStrategy):
    """剥头皮策略"""
    
    def __init__(self):
        super().__init__("剥头皮")
        self.min_confidence = 70
    
    def analyze(self, features: List[float], metadata: Dict) -> Dict:
        """
        生成超短线信号
        
        原理：
        - 捕捉分钟级别波动
        - 快速进出，薄利多销
        - 严格止损止盈
        """
        try:
            # 提取特征
            current_price = metadata.get('current_price', 0)
            price_change_24h = features[5] if len(features) > 5 else 0
            volatility = features[7] if len(features) > 7 else 0
            rsi_norm = features[12] if len(features) > 12 else 0.5
            volume = features[6] if len(features) > 6 else 0
            
            # Gas费用检查（超短线对费用敏感）
            eth_gas = features[0] if len(features) > 0 else 50
            if eth_gas > 25:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': 0,
                    'reason': f'Gas费用过高({eth_gas} Gwei)，不适合超短线'
                }
            
            confidence = 50
            signal = 'NEUTRAL'
            reason = ""
            
            # 快速上涨 + RSI未超买
            if 0.5 < price_change_24h < 2.0 and rsi_norm < 0.6:
                signal = 'LONG'
                confidence += 20
                reason = "短线上涨动能"
                
                # 波动率适中
                if 0.01 < volatility < 0.025:
                    confidence += 15
                    reason += "，波动适中"
                
                # 成交量活跃
                if volume > metadata.get('avg_volume', volume):
                    confidence += 10
                    reason += "，成交活跃"
                
                # RSI理想区间
                if 0.45 < rsi_norm < 0.55:
                    confidence += 10
                    reason += "，RSI中性"
            
            # 快速下跌 + RSI未超卖
            elif -2.0 < price_change_24h < -0.5 and rsi_norm > 0.4:
                signal = 'SHORT'
                confidence += 20
                reason = "短线下跌动能"
                
                # 波动率适中
                if 0.01 < volatility < 0.025:
                    confidence += 15
                    reason += "，波动适中"
                
                # 成交量活跃
                if volume > metadata.get('avg_volume', volume):
                    confidence += 10
                    reason += "，成交活跃"
                
                # RSI理想区间
                if 0.45 < rsi_norm < 0.55:
                    confidence += 10
                    reason += "，RSI中性"
            
            else:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': confidence,
                    'reason': f"无明确超短线机会（涨跌={price_change_24h:.2f}%, RSI={rsi_norm:.2f}）"
                }
            
            # 超短线止损止盈（小而快）
            if signal == 'LONG':
                stop_loss = current_price * 0.995   # 0.5%止损
                take_profit = [
                    current_price * 1.005,  # 0.5%
                    current_price * 1.01,   # 1%
                    current_price * 1.015   # 1.5%
                ]
                position_size_ratio = 0.20  # 20%仓位（快进快出）
            
            elif signal == 'SHORT':
                stop_loss = current_price * 1.005
                take_profit = [
                    current_price * 0.995,
                    current_price * 0.99,
                    current_price * 0.985
                ]
                position_size_ratio = 0.20
            
            return {
                'signal': signal,
                'confidence': min(confidence, 100),
                'reason': reason,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size_ratio': position_size_ratio,
                'holding_time': '5-30分钟',  # 预期持仓时间
                'note': '超短线交易，需要密切监控'
            }
            
        except Exception as e:
            logger.error(f"剥头皮策略分析出错: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reason': f"分析出错: {e}"
            }
    
    def get_description(self) -> str:
        return """
剥头皮策略（超短线）
- 适合：活跃市场，高频交易
- 原理：捕捉小幅波动
- 优势：机会多，风险可控
- 劣势：需要低Gas费，频繁操作
- 止损：0.5%（严格）
- 止盈：0.5% / 1% / 1.5%（快速）
- 持仓时间：5-30分钟
- 注意：需要全程监控
"""
