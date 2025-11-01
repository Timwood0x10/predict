#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强动态权重管理器 - 根据市场状态和异常情况智能调整维度权重

主要功能：
1. 基础市场状态权重调整
2. 异常情况检测与权重微调
3. 多维度权重平滑过渡
4. 权重历史记录与回溯
"""

from typing import Dict, List, Tuple, Optional
import logging
import numpy as np
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class EnhancedDynamicWeightManager:
    """增强动态权重管理器"""
    
    def __init__(self, history_size: int = 100):
        """
        初始化增强权重管理器
        
        Args:
            history_size: 历史记录保存数量
        """
        self.history_size = history_size
        
        # 基础权重配置（决策引擎使用的4个维度）
        self.base_weights = {
            'news': 0.30,      # 新闻信号 30%
            'price': 0.25,     # 价格信号 25%
            'sentiment': 0.25, # 情绪信号 25%
            'ai': 0.20         # AI信号 20%
        }
        
        # 市场状态权重配置
        self.market_state_weights = {
            'bull': {  # 牛市
                'news': 1.2,        # 新闻影响力增强
                'price': 1.3,       # 价格趋势更重要
                'sentiment': 1.1,   # 情绪适度增强
                'ai': 1.2           # AI预测更可靠
            },
            'bear': {  # 熊市
                'news': 1.3,        # 新闻影响更大
                'price': 1.1,       # 价格趋势作用减弱
                'sentiment': 0.8,   # 情绪容易恐慌，降低权重
                'ai': 0.9           # AI可能被情绪影响
            },
            'sideways': {  # 震荡市
                'news': 1.0,        # 保持正常
                'price': 1.2,       # 技术分析更重要
                'sentiment': 1.0,   # 保持正常
                'ai': 1.1           # AI辅助判断
            },
            'volatile': {  # 高波动
                'news': 0.8,        # 新闻噪音多
                'price': 1.1,       # 价格动量重要
                'sentiment': 1.3,   # 情绪指标重要
                'ai': 0.9           # AI可能滞后
            }
        }
        
        # 异常检测阈值
        self.anomaly_thresholds = {
            'orderbook_imbalance': 0.8,     # 订单簿极度失衡
            'vix_extreme': 30,               # VIX极端水平
            'volume_spike': 3.0,             # 成交量突增倍数
            'price_gap': 0.05,               # 价格跳空
            'news_flood': 50,                # 新闻数量激增
            'sentiment_divergence': 0.7      # 情绪指标严重分歧
        }
        
        # 权重调整限制
        self.adjustment_limits = {
            'min_weight': 0.05,    # 最小权重
            'max_weight': 0.50,    # 最大权重
            'max_change': 0.20     # 单次最大调整幅度
        }
        
        # 历史记录
        self.weight_history = deque(maxlen=history_size)
        self.market_state_history = deque(maxlen=history_size)
        self.last_adjustment_time = None
        
    def get_market_state(self, features: List[float]) -> str:
        """
        智能识别市场状态
        
        Args:
            features: 特征向量
            
        Returns:
            市场状态: 'bull', 'bear', 'sideways', 'volatile'
        """
        try:
            # 提取关键指标
            price_change = features[5] if len(features) > 5 else 0  # 24h价格变化
            volatility = features[7] if len(features) > 7 else 0.02  # 波动率
            volume_ratio = features[6] if len(features) > 6 else 1.0  # 成交量比率
            trend_strength = abs(features[8]) if len(features) > 8 else 0  # 趋势强度
            
            # 多维度判断
            state_scores = {
                'bull': 0,
                'bear': 0,
                'sideways': 0,
                'volatile': 0
            }
            
            # 价格趋势判断
            if price_change > 0.02:  # 上涨超过2%
                state_scores['bull'] += 3
            elif price_change < -0.02:  # 下跌超过2%
                state_scores['bear'] += 3
            else:
                state_scores['sideways'] += 2
            
            # 波动率判断
            if volatility > 0.04:  # 高波动
                state_scores['volatile'] += 3
            elif volatility < 0.015:  # 低波动
                state_scores['sideways'] += 2
            
            # 成交量判断
            if volume_ratio > 2.0:  # 成交量放大
                state_scores['volatile'] += 2
                if price_change > 0:
                    state_scores['bull'] += 1
                else:
                    state_scores['bear'] += 1
            
            # 趋势强度判断
            if trend_strength > 0:  # 有明确趋势
                if price_change > 0:
                    state_scores['bull'] += 2
                else:
                    state_scores['bear'] += 2
            else:
                state_scores['sideways'] += 1
            
            # 选择得分最高的状态
            market_state = max(state_scores.items(), key=lambda x: x[1])[0]
            
            logger.debug(f"市场状态识别: {market_state}, 得分: {state_scores}")
            return market_state
            
        except Exception as e:
            logger.error(f"市场状态识别失败: {e}")
            return 'sideways'
    
    def detect_anomalies(self, features: List[float]) -> Dict[str, Tuple[bool, float]]:
        """
        检测市场异常情况
        
        Args:
            features: 特征向量
            
        Returns:
            异常检测结果: {异常类型: (是否异常, 异常值)}
        """
        anomalies = {}
        
        try:
            # 1. 订单簿失衡检测
            if len(features) > 26:
                orderbook_imbalance = features[26]
                is_anomaly = abs(orderbook_imbalance) > self.anomaly_thresholds['orderbook_imbalance']
                anomalies['orderbook'] = (is_anomaly, abs(orderbook_imbalance))
            
            # 2. VIX极端检测
            if len(features) > 31:
                vix_level = features[31]
                is_anomaly = vix_level > self.anomaly_thresholds['vix_extreme']
                anomalies['vix'] = (is_anomaly, vix_level)
            
            # 3. 成交量突增检测
            if len(features) > 6:
                volume_ratio = features[6]
                is_anomaly = volume_ratio > self.anomaly_thresholds['volume_spike']
                anomalies['volume'] = (is_anomaly, volume_ratio)
            
            # 4. 价格跳空检测
            if len(features) > 12:
                price_gap = features[12]  # 价格区间百分比
                is_anomaly = price_gap > self.anomaly_thresholds['price_gap']
                anomalies['price_gap'] = (is_anomaly, price_gap)
            
            # 5. 新闻洪水检测
            if len(features) > 15:
                news_count = features[15]
                is_anomaly = news_count > self.anomaly_thresholds['news_flood']
                anomalies['news_flood'] = (is_anomaly, news_count)
            
            # 6. 情绪分歧检测
            if len(features) > 24:
                sentiment_divergence = 1 - abs(features[24])  # AI一致性反转
                is_anomaly = sentiment_divergence > self.anomaly_thresholds['sentiment_divergence']
                anomalies['sentiment_divergence'] = (is_anomaly, sentiment_divergence)
            
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
        
        return anomalies
    
    def calculate_anomaly_adjustments(self, anomalies: Dict[str, Tuple[bool, float]]) -> Dict[str, float]:
        """
        根据异常情况计算权重调整
        
        Args:
            anomalies: 异常检测结果
            
        Returns:
            权重调整系数
        """
        adjustments = {
            'news': 1.0,
            'price': 1.0,
            'sentiment': 1.0,
            'ai': 1.0
        }
        
        # 订单簿异常调整
        if anomalies.get('orderbook', (False, 0))[0]:
            # 极端失衡可能是假墙，降低价格相关权重
            adjustments['price'] *= 0.7
            adjustments['sentiment'] *= 0.8
            logger.info("检测到订单簿异常，降低价格和情绪权重")
        
        # VIX极端调整
        if anomalies.get('vix', (False, 0))[0]:
            # 极端恐慌时，宏观和风险指标更重要
            adjustments['sentiment'] *= 1.3
            adjustments['news'] *= 1.2
            adjustments['price'] *= 0.8
            logger.info("检测到VIX极端，增强情绪和新闻权重")
        
        # 成交量突增调整
        if anomalies.get('volume', (False, 0))[0]:
            # 异常成交量可能预示突破，增强价格权重
            adjustments['price'] *= 1.2
            adjustments['ai'] *= 1.1
            logger.info("检测到成交量突增，增强价格和AI权重")
        
        # 新闻洪水调整
        if anomalies.get('news_flood', (False, 0))[0]:
            # 新闻过多可能产生噪音，降低新闻权重
            adjustments['news'] *= 0.6
            adjustments['sentiment'] *= 0.9
            logger.info("检测到新闻洪水，降低新闻权重")
        
        # 情绪分歧调整
        if anomalies.get('sentiment_divergence', (False, 0))[0]:
            # AI模型分歧严重时，降低AI权重
            adjustments['ai'] *= 0.7
            adjustments['price'] *= 1.1
            logger.info("检测到情绪分歧，降低AI权重")
        
        return adjustments
    
    def smooth_weight_transition(self, current_weights: Dict[str, float], 
                                target_weights: Dict[str, float], 
                                smoothing_factor: float = 0.3) -> Dict[str, float]:
        """
        权重平滑过渡，避免剧烈变化
        
        Args:
            current_weights: 当前权重
            target_weights: 目标权重
            smoothing_factor: 平滑因子 (0-1)
            
        Returns:
            平滑后的权重
        """
        smoothed_weights = {}
        
        for dimension in current_weights:
            current = current_weights[dimension]
            target = target_weights.get(dimension, current)
            
            # 线性插值平滑
            smoothed = current + (target - current) * smoothing_factor
            
            # 应用调整限制
            smoothed = max(self.adjustment_limits['min_weight'], 
                          min(self.adjustment_limits['max_weight'], smoothed))
            
            smoothed_weights[dimension] = smoothed
        
        return smoothed_weights
    
    def get_adjusted_weights(self, features: List[float]) -> Dict[str, float]:
        """
        获取调整后的权重
        
        Args:
            features: 特征向量
            
        Returns:
            调整后的权重字典
        """
        try:
            # 1. 识别市场状态
            market_state = self.get_market_state(features)
            
            # 2. 获取基础市场状态权重
            state_weights = self.market_state_weights.get(market_state, 
                                                         self.market_state_weights['sideways'])
            
            # 3. 应用市场状态权重调整
            base_adjusted = {}
            for dimension, base_weight in self.base_weights.items():
                state_multiplier = state_weights.get(dimension, 1.0)
                base_adjusted[dimension] = base_weight * state_multiplier
            
            # 4. 检测异常情况
            anomalies = self.detect_anomalies(features)
            
            # 5. 计算异常调整
            if any(anomaly[0] for anomaly in anomalies.values()):
                anomaly_adjustments = self.calculate_anomaly_adjustments(anomalies)
                
                # 应用异常调整
                for dimension in base_adjusted:
                    anomaly_multiplier = anomaly_adjustments.get(dimension, 1.0)
                    base_adjusted[dimension] *= anomaly_multiplier
            
            # 6. 权重归一化（确保总和为1）
            total_weight = sum(base_adjusted.values())
            if total_weight > 0:
                normalized_weights = {
                    dim: weight / total_weight 
                    for dim, weight in base_adjusted.items()
                }
            else:
                normalized_weights = self.base_weights
            
            # 7. 平滑过渡（如果有历史记录）
            if self.weight_history:
                last_weights = self.weight_history[-1]
                final_weights = self.smooth_weight_transition(last_weights, normalized_weights)
            else:
                final_weights = normalized_weights
            
            # 8. 记录历史
            self.weight_history.append(final_weights.copy())
            self.market_state_history.append(market_state)
            self.last_adjustment_time = datetime.now()
            
            # 9. 日志记录
            logger.info(f"权重调整完成 - 市场状态: {market_state}")
            if anomalies:
                detected = [k for k, v in anomalies.items() if v[0]]
                logger.info(f"检测到异常: {detected}")
            
            return final_weights
            
        except Exception as e:
            logger.error(f"权重调整失败: {e}")
            return self.base_weights
    
    def get_weight_history(self, hours: int = 24) -> List[Dict]:
        """
        获取权重历史记录
        
        Args:
            hours: 查询最近几小时的历史
            
        Returns:
            权重历史列表
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 简化版本，返回最近N条记录
        recent_count = min(len(self.weight_history), max(1, hours))
        return list(self.weight_history)[-recent_count:]
    
    def get_adjustment_summary(self) -> Dict:
        """
        获取权重调整摘要
        
        Returns:
            调整摘要信息
        """
        if not self.weight_history:
            return {'status': 'no_history'}
        
        current_weights = self.weight_history[-1]
        weight_changes = []
        
        if len(self.weight_history) > 1:
            prev_weights = self.weight_history[-2]
            for dimension in current_weights:
                change = current_weights[dimension] - prev_weights[dimension]
                weight_changes.append({
                    'dimension': dimension,
                    'change': change,
                    'change_pct': change / prev_weights[dimension] * 100
                })
        
        return {
            'status': 'active',
            'current_weights': current_weights,
            'market_state': self.market_state_history[-1] if self.market_state_history else 'unknown',
            'last_adjustment': self.last_adjustment_time,
            'weight_changes': weight_changes,
            'history_count': len(self.weight_history)
        }


# 使用示例
if __name__ == "__main__":
    # 创建增强权重管理器
    weight_manager = EnhancedDynamicWeightManager()
    
    # 模拟特征向量（47维）
    features = [0] * 47
    features[5] = 0.025   # 24h价格上涨2.5%
    features[7] = 0.018   # 波动率1.8%
    features[8] = 1       # 上涨趋势
    features[26] = 0.9    # 订单簿极度失衡
    
    # 获取调整后的权重
    adjusted_weights = weight_manager.get_adjusted_weights(features)
    
    print("调整后的权重:")
    for dimension, weight in adjusted_weights.items():
        print(f"  {dimension}: {weight:.3f}")
    
    # 获取调整摘要
    summary = weight_manager.get_adjustment_summary()
    print(f"\n市场状态: {summary['market_state']}")
    print(f"权重变化数量: {len(summary['weight_changes'])}")