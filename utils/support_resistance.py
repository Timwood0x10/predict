#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支撑阻力识别器
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SupportResistanceFinder:
    """支撑阻力位识别"""
    
    def find_levels(self, df: pd.DataFrame, current_price: float) -> dict:
        """识别关键支撑阻力位"""
        try:
            if len(df) < 20:
                return self._default_levels(current_price)
            
            # 找局部最高点
            df_copy = df.copy()
            df_copy['local_max'] = df_copy['high'].rolling(window=5, center=True).max() == df_copy['high']
            
            # 找局部最低点
            df_copy['local_min'] = df_copy['low'].rolling(window=5, center=True).min() == df_copy['low']
            
            # 提取支撑位
            supports = df_copy[df_copy['local_min'] == True]['low'].values
            supports = supports[supports < current_price]
            
            # 提取阻力位
            resistances = df_copy[df_copy['local_max'] == True]['high'].values
            resistances = resistances[resistances > current_price]
            
            # 找最近的支撑和阻力
            if len(supports) > 0:
                nearest_support = float(max(supports))
            else:
                nearest_support = current_price * 0.95
            
            if len(resistances) > 0:
                nearest_resistance = float(min(resistances))
            else:
                nearest_resistance = current_price * 1.05
            
            # 计算距离
            support_distance = ((current_price - nearest_support) / current_price) * 100
            resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
            
            return {
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance,
                'support_distance': round(support_distance, 2),
                'resistance_distance': round(resistance_distance, 2)
            }
            
        except Exception as e:
            logger.error(f"支撑阻力识别失败: {e}")
            return self._default_levels(current_price)
    
    def _default_levels(self, current_price: float) -> dict:
        """默认支撑阻力"""
        return {
            'nearest_support': current_price * 0.98,
            'nearest_resistance': current_price * 1.02,
            'support_distance': 2.0,
            'resistance_distance': 2.0
        }
