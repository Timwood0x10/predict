#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态权重管理器 - 根据市场状态调整维度权重
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


class DynamicWeightManager:
    """动态权重管理 - 根据市场状态自动调整"""
    
    def __init__(self):
        # 不同市场状态的权重配置
        self.weight_configs = {
            'bull': {  # 牛市
                'sentiment': 1.3,      # 情绪更重要
                'orderbook': 1.2,      # 买盘强劲
                'macro': 0.8,          # 宏观影响小
                'technical': 1.0,
                'news': 1.2,
                'futures': 1.0
            },
            'bear': {  # 熊市
                'macro': 1.4,          # 宏观主导
                'risk': 1.3,           # 风险指标
                'sentiment': 0.7,      # 情绪易误导
                'futures': 1.2,        # 空头力量
                'technical': 1.0,
                'orderbook': 0.9
            },
            'sideways': {  # 震荡
                'technical': 1.3,      # 技术分析
                'orderbook': 1.2,      # 支撑阻力
                'sentiment': 1.0,
                'macro': 1.0,
                'news': 1.0,
                'futures': 1.0
            }
        }
    
    def get_market_state(self, features: list) -> str:
        """
        识别市场状态
        
        Args:
            features: 特征向量（35维）
            
        Returns:
            'bull', 'bear', or 'sideways'
        """
        try:
            # 从特征中提取关键指标
            # features[2]: 价格变化率
            # features[7]: 波动率
            
            price_change = features[2] if len(features) > 2 else 0
            volatility = features[7] if len(features) > 7 else 0.02
            
            # 市场状态判断
            if price_change > 0.02 and volatility < 0.04:
                return 'bull'  # 稳定上涨
            elif price_change < -0.02 and volatility < 0.04:
                return 'bear'  # 稳定下跌
            else:
                return 'sideways'  # 震荡
                
        except Exception as e:
            logger.warning(f"市场状态识别失败: {e}")
            return 'sideways'
    
    def get_weights(self, market_state: str) -> Dict[str, float]:
        """
        获取建议权重（AI可调整）
        
        Args:
            market_state: 市场状态
            
        Returns:
            权重配置字典
        """
        return self.weight_configs.get(market_state, self.weight_configs['sideways'])
    
    def adjust_weights_by_dimensions(self, base_weights: Dict, features: list) -> Dict:
        """
        根据特征自动微调权重（可选）
        
        Args:
            base_weights: 基础权重
            features: 特征向量
            
        Returns:
            调整后的权重
        """
        adjusted = base_weights.copy()
        
        try:
            # 如果订单簿数据异常（如假墙），降低权重
            if len(features) > 28:  # 有订单簿数据
                orderbook_imbalance = features[26]
                if abs(orderbook_imbalance) > 0.8:  # 极端失衡可能是假墙
                    adjusted['orderbook'] = adjusted.get('orderbook', 1.0) * 0.7
            
            # 如果VIX极端，增加风险指标权重
            if len(features) > 31:  # 有VIX数据
                vix_level = features[31]
                if vix_level > 30:  # VIX>30表示极端恐慌
                    adjusted['risk'] = adjusted.get('risk', 1.0) * 1.3
                    adjusted['macro'] = adjusted.get('macro', 1.0) * 1.2
            
        except Exception as e:
            logger.warning(f"权重微调失败: {e}")
        
        return adjusted
