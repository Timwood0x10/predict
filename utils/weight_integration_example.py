#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态权重集成示例 - 展示如何将增强动态权重管理器集成到决策引擎中

这个文件展示了完整的集成方案，包括：
1. 权重管理器的初始化和使用
2. 与决策引擎的无缝集成
3. 权重调整的实时监控
"""

import logging
from datetime import datetime
from enhanced_dynamic_weights import EnhancedDynamicWeightManager
from decision_engine import DecisionEngine

logger = logging.getLogger(__name__)


class EnhancedDecisionEngine(DecisionEngine):
    """
    增强决策引擎 - 集成动态权重管理
    """
    
    def __init__(self, account_balance: float = 10000, risk_percent: float = 0.015):
        """
        初始化增强决策引擎
        
        Args:
            account_balance: 账户余额
            risk_percent: 风险比例
        """
        # 调用父类初始化
        super().__init__(account_balance, risk_percent)
        
        # 初始化动态权重管理器
        self.weight_manager = EnhancedDynamicWeightManager(history_size=50)
        
        # 权重调整历史
        self.weight_adjustment_log = []
        
        logger.info("增强决策引擎初始化完成 - 集成动态权重管理")
    
    def analyze_with_dynamic_weights(self, features: List[float], 
                                     news_data: Optional[List] = None) -> Dict:
        """
        使用动态权重进行分析
        
        Args:
            features: 特征向量
            news_data: 新闻数据（可选）
            
        Returns:
            完整的分析结果
        """
        # 1. 获取动态调整后的权重
        dynamic_weights = self.weight_manager.get_adjusted_weights(features)
        
        # 2. 更新决策引擎的权重配置
        original_weights = self.weights.copy()
        self.weights = dynamic_weights
        
        # 3. 记录权重变化
        weight_change = {
            'timestamp': datetime.now(),
            'original_weights': original_weights,
            'dynamic_weights': dynamic_weights,
            'market_state': self.weight_manager.market_state_history[-1] if self.weight_manager.market_state_history else 'unknown'
        }
        self.weight_adjustment_log.append(weight_change)
        
        # 4. 执行分析
        result = super().analyze(features, news_data)
        
        # 5. 添加权重信息到结果中
        result['dynamic_weights'] = {
            'current_weights': dynamic_weights,
            'market_state': weight_change['market_state'],
            'weight_adjustments': self._calculate_weight_impact(original_weights, dynamic_weights)
        }
        
        # 6. 恢复原始权重（保持引擎独立性）
        self.weights = original_weights
        
        return result
    
    def _calculate_weight_impact(self, original: Dict[str, float], 
                               adjusted: Dict[str, float]) -> Dict[str, float]:
        """
        计算权重调整的影响
        
        Args:
            original: 原始权重
            adjusted: 调整后权重
            
        Returns:
            权重影响分析
        """
        impact = {}
        
        for dimension in original:
            original_weight = original[dimension]
            adjusted_weight = adjusted.get(dimension, original_weight)
            
            impact[dimension] = {
                'original': round(original_weight, 3),
                'adjusted': round(adjusted_weight, 3),
                'change': round(adjusted_weight - original_weight, 3),
                'change_pct': round((adjusted_weight - original_weight) / original_weight * 100, 1)
            }
        
        return impact
    
    def get_weight_analysis_report(self) -> str:
        """
        生成权重分析报告
        
        Returns:
            格式化的权重分析报告
        """
        if not self.weight_adjustment_log:
            return "暂无权重调整记录"
        
        lines = []
        lines.append("=" * 60)
        lines.append("📊 动态权重分析报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 最新调整信息
        latest = self.weight_adjustment_log[-1]
        lines.append(f"📅 最新调整时间: {latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"🎯 市场状态: {latest['market_state']}")
        lines.append("")
        
        # 权重对比
        lines.append("📈 权重变化对比:")
        for dimension, impact in latest['weight_adjustments'].items():
            change_symbol = "📈" if impact['change'] > 0 else "📉" if impact['change'] < 0 else "➡️"
            lines.append(f"  {change_symbol} {dimension}: {impact['original']:.3f} → {impact['adjusted']:.3f} ({impact['change_pct']:+.1f}%)")
        
        lines.append("")
        
        # 权重管理器摘要
        summary = self.weight_manager.get_adjustment_summary()
        lines.append("📋 权重管理器状态:")
        lines.append(f"  历史记录数: {summary['history_count']}")
        lines.append(f"  当前市场状态: {summary['market_state']}")
        
        # 异常检测
        if summary['weight_changes']:
            lines.append("")
            lines.append("⚠️ 最近权重变化:")
            for change in summary['weight_changes'][-3:]:  # 最近3个变化
                if abs(change['change_pct']) > 5:  # 变化超过5%
                    lines.append(f"  {change['dimension']}: {change['change_pct']:+.1f}%")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def simulate_weight_scenarios(self, features: List[float]) -> Dict[str, Dict]:
        """
        模拟不同市场状态下的权重配置
        
        Args:
            features: 特征向量
            
        Returns:
            各市场状态的权重配置
        """
        scenarios = {}
        
        # 保存当前权重
        original_weights = self.weights.copy()
        
        # 模拟不同市场状态
        for state in ['bull', 'bear', 'sideways', 'volatile']:
            # 强制设置市场状态
            temp_features = features.copy()
            
            # 根据状态调整特征
            if state == 'bull':
                temp_features[5] = 0.03   # 上涨3%
                temp_features[7] = 0.015  # 低波动
                temp_features[8] = 1     # 上涨趋势
            elif state == 'bear':
                temp_features[5] = -0.03  # 下跌3%
                temp_features[7] = 0.015  # 低波动
                temp_features[8] = -1    # 下跌趋势
            elif state == 'sideways':
                temp_features[5] = 0.001  # 微涨
                temp_features[7] = 0.02   # 中等波动
                temp_features[8] = 0     # 无趋势
            elif state == 'volatile':
                temp_features[5] = 0.01   # 小涨
                temp_features[7] = 0.05   # 高波动
                temp_features[8] = 1     # 有趋势
            
            # 获取该状态下的权重
            state_weights = self.weight_manager.get_adjusted_weights(temp_features)
            
            scenarios[state] = {
                'weights': state_weights,
                'market_state': state,
                'description': self._get_state_description(state)
            }
        
        # 恢复原始权重
        self.weights = original_weights
        
        return scenarios
    
    def _get_state_description(self, state: str) -> str:
        """获取市场状态描述"""
        descriptions = {
            'bull': "牛市 - 价格上涨，情绪乐观，趋势明显",
            'bear': "熊市 - 价格下跌，情绪悲观，避险为主",
            'sideways': "震荡市 - 价格横盘，等待突破",
            'volatile': "高波动 - 价格剧烈波动，风险较高"
        }
        return descriptions.get(state, "未知状态")


# 使用示例
def demonstrate_dynamic_weights():
    """演示动态权重功能"""
    print("=" * 60)
    print("🎯 动态权重管理演示")
    print("=" * 60)
    print()
    
    # 创建增强决策引擎
    engine = EnhancedDecisionEngine(account_balance=10000, risk_percent=0.015)
    
    # 模拟不同市场状况的特征向量
    scenarios = {
        "牛市上涨": {
            'features': [0] * 47,
            'description': "BTC上涨3%，波动率低，趋势明显"
        },
        "熊市下跌": {
            'features': [0] * 47,
            'description': "BTC下跌3%，恐慌情绪明显"
        },
        "震荡市场": {
            'features': [0] * 47,
            'description': "BTC横盘整理，等待方向选择"
        },
        "异常情况": {
            'features': [0] * 47,
            'description': "订单簿极度失衡，VIX极端"
        }
    }
    
    # 设置不同场景的特征值
    scenarios["牛市上涨"]['features'][5] = 0.03   # 24h上涨3%
    scenarios["牛市上涨"]['features'][7] = 0.015  # 低波动
    scenarios["牛市上涨"]['features'][8] = 1      # 上涨趋势
    
    scenarios["熊市下跌"]['features'][5] = -0.03  # 24h下跌3%
    scenarios["熊市下跌"]['features'][19] = 20    # 恐惧贪婪指数20（极度恐慌）
    scenarios["熊市下跌"]['features'][8] = -1     # 下跌趋势
    
    scenarios["震荡市场"]['features'][5] = 0.001  # 微涨
    scenarios["震荡市场"]['features'][7] = 0.02   # 中等波动
    scenarios["震荡市场"]['features'][8] = 0      # 无趋势
    
    scenarios["异常情况"]['features'][26] = 0.9   # 订单簿极度失衡
    scenarios["异常情况"]['features'][31] = 35    # VIX极端
    
    # 演示各场景
    for scenario_name, scenario_data in scenarios.items():
        print(f"\n📊 场景: {scenario_name}")
        print(f"描述: {scenario_data['description']}")
        print("-" * 40)
        
        # 使用动态权重分析
        result = engine.analyze_with_dynamic_weights(scenario_data['features'])
        
        # 显示权重调整
        if 'dynamic_weights' in result:
            dw = result['dynamic_weights']
            print(f"市场状态: {dw['market_state']}")
            print("权重配置:")
            
            for dimension, weight in dw['current_weights'].items():
                print(f"  {dimension}: {weight:.3f}")
            
            # 显示权重变化
            if 'weight_adjustments' in dw:
                print("\n权重变化:")
                for dim, impact in dw['weight_adjustments'].items():
                    if abs(impact['change_pct']) > 1:  # 只显示变化超过1%的
                        symbol = "📈" if impact['change'] > 0 else "📉"
                        print(f"  {symbol} {dim}: {impact['change_pct']:+.1f}%")
    
    # 生成分析报告
    print("\n" + "=" * 60)
    print("📋 权重分析报告")
    print("=" * 60)
    print(engine.get_weight_analysis_report())


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 运行演示
    demonstrate_dynamic_weights()
