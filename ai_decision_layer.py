#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能决策层
让AI根据市场环境自动选择最优策略并执行交易
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

from strategies import (
    TrendFollowingStrategy,
    MeanReversionStrategy,
    BreakoutStrategy,
    GridStrategy,
    ScalpingStrategy
)
from utils.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)


class AIDecisionLayer:
    """
    AI智能决策层
    
    功能：
    1. 分析市场环境
    2. 选择最优策略
    3. 综合多策略信号
    4. 生成最终决策
    5. 执行风险控制
    """
    
    def __init__(self, account_balance: float = 10000, risk_percent: float = 0.015):
        """
        初始化AI决策层
        
        Args:
            account_balance: 账户余额
            risk_percent: 单笔风险比例
        """
        logger.info("初始化AI智能决策层")
        
        # 初始化决策引擎
        self.decision_engine = DecisionEngine(
            account_balance=account_balance,
            risk_percent=risk_percent
        )
        
        # 初始化所有策略
        self.strategies = {
            'trend_following': TrendFollowingStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'breakout': BreakoutStrategy(),
            'grid': GridStrategy(),
            'scalping': ScalpingStrategy()
        }
        
        logger.info(f"✓ 已加载 {len(self.strategies)} 个交易策略")
    
    def analyze_market_environment(self, features: List[float], metadata: Dict) -> Dict:
        """
        分析市场环境，判断适合什么类型的策略
        
        Args:
            features: 26维特征向量
            metadata: 元数据
        
        Returns:
            市场环境分析结果
        """
        try:
            # 提取关键特征
            trend = features[8] if len(features) > 8 else 0
            volatility = features[7] if len(features) > 7 else 0
            price_change_24h = features[5] if len(features) > 5 else 0
            rsi_norm = features[12] if len(features) > 12 else 0.5
            
            # 判断市场状态
            market_state = {
                'type': 'unknown',
                'confidence': 0,
                'description': '',
                'suitable_strategies': []
            }
            
            # 强趋势市场
            if abs(trend) == 1 and abs(price_change_24h) > 2.0:
                if trend == 1:
                    market_state['type'] = 'strong_uptrend'
                    market_state['description'] = '强上涨趋势'
                else:
                    market_state['type'] = 'strong_downtrend'
                    market_state['description'] = '强下跌趋势'
                
                market_state['confidence'] = 80
                market_state['suitable_strategies'] = ['trend_following', 'breakout']
            
            # 震荡市场
            elif trend == 0 and volatility < 0.025:
                market_state['type'] = 'ranging'
                market_state['description'] = '震荡市场'
                market_state['confidence'] = 75
                market_state['suitable_strategies'] = ['mean_reversion', 'grid', 'scalping']
            
            # 波动市场
            elif volatility > 0.03:
                market_state['type'] = 'volatile'
                market_state['description'] = '高波动市场'
                market_state['confidence'] = 70
                market_state['suitable_strategies'] = ['scalping']
            
            # 盘整突破
            elif abs(price_change_24h) < 1.0 and volatility < 0.015:
                market_state['type'] = 'consolidation'
                market_state['description'] = '盘整整理'
                market_state['confidence'] = 65
                market_state['suitable_strategies'] = ['breakout', 'grid']
            
            # 超买超卖
            elif rsi_norm < 0.3 or rsi_norm > 0.7:
                if rsi_norm < 0.3:
                    market_state['type'] = 'oversold'
                    market_state['description'] = '超卖'
                else:
                    market_state['type'] = 'overbought'
                    market_state['description'] = '超买'
                
                market_state['confidence'] = 70
                market_state['suitable_strategies'] = ['mean_reversion']
            
            # 默认
            else:
                market_state['type'] = 'neutral'
                market_state['description'] = '中性市场'
                market_state['confidence'] = 50
                market_state['suitable_strategies'] = ['trend_following', 'scalping']
            
            logger.info(f"市场环境: {market_state['description']} ({market_state['confidence']}%)")
            logger.info(f"推荐策略: {', '.join(market_state['suitable_strategies'])}")
            
            return market_state
            
        except Exception as e:
            logger.error(f"市场环境分析出错: {e}")
            return {
                'type': 'error',
                'confidence': 0,
                'description': f'分析出错: {e}',
                'suitable_strategies': []
            }
    
    def run_all_strategies(self, features: List[float], metadata: Dict) -> Dict[str, Dict]:
        """
        运行所有策略，收集信号
        
        Args:
            features: 26维特征向量
            metadata: 元数据
        
        Returns:
            各策略的信号字典
        """
        signals = {}
        
        for name, strategy in self.strategies.items():
            try:
                if strategy.is_enabled():
                    signal = strategy.analyze(features, metadata)
                    
                    if strategy.validate_signal(signal):
                        signals[name] = signal
                        logger.info(f"✓ {name}: {signal['signal']} ({signal['confidence']:.0f}%)")
                    else:
                        logger.debug(f"✗ {name}: 信号无效或置信度不足")
                        
            except Exception as e:
                logger.error(f"{name} 策略执行出错: {e}")
        
        return signals
    
    def select_best_strategy(
        self,
        market_env: Dict,
        all_signals: Dict[str, Dict]
    ) -> Optional[Dict]:
        """
        根据市场环境选择最优策略
        
        Args:
            market_env: 市场环境分析结果
            all_signals: 所有策略信号
        
        Returns:
            最优策略及其信号
        """
        if not all_signals:
            logger.info("无有效策略信号")
            return None
        
        # 过滤出适合当前市场的策略
        suitable_signals = {
            name: signal
            for name, signal in all_signals.items()
            if name in market_env['suitable_strategies']
        }
        
        # 如果没有适合的策略，使用所有信号
        if not suitable_signals:
            logger.warning("没有适合当前市场的策略，使用所有策略")
            suitable_signals = all_signals
        
        # 选择置信度最高的策略
        best_strategy = max(
            suitable_signals.items(),
            key=lambda x: x[1]['confidence']
        )
        
        logger.info(f"🎯 选择策略: {best_strategy[0]} (置信度: {best_strategy[1]['confidence']:.0f}%)")
        
        return {
            'strategy_name': best_strategy[0],
            'signal': best_strategy[1]
        }
    
    def aggregate_signals(self, all_signals: Dict[str, Dict]) -> Dict:
        """
        综合多个策略信号
        
        Args:
            all_signals: 所有策略信号
        
        Returns:
            综合信号
        """
        if not all_signals:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'reason': '无有效策略信号',
                'strategies_count': 0
            }
        
        # 统计各方向信号
        long_signals = [s for s in all_signals.values() if s['signal'] == 'LONG']
        short_signals = [s for s in all_signals.values() if s['signal'] == 'SHORT']
        
        # 计算平均置信度
        long_confidence = sum(s['confidence'] for s in long_signals) / len(long_signals) if long_signals else 0
        short_confidence = sum(s['confidence'] for s in short_signals) / len(short_signals) if short_signals else 0
        
        # 综合判断
        if len(long_signals) > len(short_signals) and long_confidence > 70:
            signal = 'LONG'
            confidence = long_confidence
            reason = f"{len(long_signals)}个策略看多"
        elif len(short_signals) > len(long_signals) and short_confidence > 70:
            signal = 'SHORT'
            confidence = short_confidence
            reason = f"{len(short_signals)}个策略看空"
        else:
            signal = 'NEUTRAL'
            confidence = 50
            reason = f"策略分歧（多:{len(long_signals)}, 空:{len(short_signals)}）"
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'long_count': len(long_signals),
            'short_count': len(short_signals),
            'strategies_count': len(all_signals)
        }
    
    def make_final_decision(
        self,
        features: List[float],
        metadata: Dict,
        use_aggregation: bool = False
    ) -> Dict:
        """
        生成最终交易决策
        
        Args:
            features: 26维特征向量
            metadata: 元数据
            use_aggregation: 是否使用信号聚合（否则选择最优策略）
        
        Returns:
            完整的交易决策
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info("\n" + "="*80)
        logger.info("AI智能决策开始")
        logger.info("="*80)
        
        # 注意：安全检查由DecisionEngine统一负责，这里不再重复检查
        
        # 1. 分析市场环境
        market_env = self.analyze_market_environment(features, metadata)
        
        # 2. 运行所有策略
        all_signals = self.run_all_strategies(features, metadata)
        
        if not all_signals:
            logger.info("无有效策略信号，保持中性")
            return {
                'timestamp': timestamp,
                'decision': {
                    'action': 'NEUTRAL',
                    'confidence': 50,  # 改为50而不是0，表示中性而不是失败
                    'reason': '无有效策略信号，市场方向不明确',
                    'source': 'no_signals'
                },
                'market_environment': market_env,
                'strategies_signals': {},
                'selected_strategy': None
            }
        
        # 3. 选择决策方式
        if use_aggregation:
            # 方式A: 信号聚合
            aggregated = self.aggregate_signals(all_signals)
            
            final_decision = {
                'action': aggregated['signal'],
                'confidence': aggregated['confidence'],
                'reason': aggregated['reason'],
                'source': 'aggregation',
                'details': aggregated
            }
            
            selected_strategy = None
        
        else:
            # 方式B: 选择最优策略
            best = self.select_best_strategy(market_env, all_signals)
            
            if not best:
                final_decision = {
                    'action': 'NEUTRAL',
                    'confidence': 0,
                    'reason': '无适合的策略',
                    'source': 'no_suitable_strategy'
                }
                selected_strategy = None
            else:
                final_decision = {
                    'action': best['signal']['signal'],
                    'confidence': best['signal']['confidence'],
                    'reason': f"[{best['strategy_name']}] {best['signal']['reason']}",
                    'source': best['strategy_name'],
                    'entry_price': best['signal'].get('entry_price'),
                    'stop_loss': best['signal'].get('stop_loss'),
                    'take_profit': best['signal'].get('take_profit'),
                    'position_size_ratio': best['signal'].get('position_size_ratio', 0.15)
                }
                selected_strategy = best
        
        logger.info("\n" + "="*80)
        logger.info(f"🎯 最终决策: {final_decision['action']}")
        logger.info(f"📈 置信度: {final_decision['confidence']:.0f}%")
        logger.info(f"💡 原因: {final_decision['reason']}")
        logger.info("="*80)
        
        return {
            'timestamp': timestamp,
            'decision': final_decision,
            'market_environment': market_env,
            'strategies_signals': all_signals,
            'selected_strategy': selected_strategy
        }
    
    def format_decision_report(self, result: Dict) -> str:
        """格式化决策报告"""
        lines = []
        lines.append("="*80)
        lines.append("🤖 AI智能交易决策报告")
        lines.append("="*80)
        lines.append(f"时间: {result['timestamp']}")
        lines.append("")
        
        # 市场环境
        if result['market_environment']:
            env = result['market_environment']
            lines.append("🌍 市场环境:")
            lines.append(f"   类型: {env['description']}")
            lines.append(f"   置信度: {env['confidence']}%")
            lines.append(f"   推荐策略: {', '.join(env['suitable_strategies'])}")
            lines.append("")
        
        # 策略信号
        if result['strategies_signals']:
            lines.append("📡 策略信号:")
            for name, signal in result['strategies_signals'].items():
                emoji = "🟢" if signal['signal'] == 'LONG' else ("🔴" if signal['signal'] == 'SHORT' else "⚪")
                lines.append(f"   {emoji} {name}: {signal['signal']} ({signal['confidence']:.0f}%) - {signal['reason']}")
            lines.append("")
        
        # 最终决策
        decision = result['decision']
        action_emoji = "🟢" if decision['action'] == 'LONG' else ("🔴" if decision['action'] == 'SHORT' else "⚪")
        lines.append(f"{action_emoji} 最终决策: {decision['action']}")
        lines.append(f"   置信度: {decision['confidence']:.0f}%")
        lines.append(f"   原因: {decision['reason']}")
        lines.append(f"   来源: {decision['source']}")
        lines.append("")
        
        # 交易计划
        if decision['action'] in ['LONG', 'SHORT'] and 'entry_price' in decision:
            lines.append("💰 交易计划:")
            lines.append(f"   入场价: ${decision['entry_price']:,.2f}")
            lines.append(f"   止损价: ${decision['stop_loss']:,.2f}")
            if decision.get('take_profit'):
                tp = decision['take_profit']
                lines.append(f"   止盈1 (50%): ${tp[0]:,.2f}")
                lines.append(f"   止盈2 (30%): ${tp[1]:,.2f}")
                lines.append(f"   止盈3 (20%): ${tp[2]:,.2f}")
            lines.append(f"   建议仓位: {decision.get('position_size_ratio', 0.15)*100:.0f}%")
            lines.append("")
        
        lines.append("="*80)
        
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试AI决策层
    logging.basicConfig(level=logging.INFO)
    
    ai = AIDecisionLayer(account_balance=10000)
    
    # 模拟特征向量
    features = [
        15.0, 8.0, 1, 1, 50000, 2.0, 1500000, 0.018, 1,
        50800, 49200, 49500, 0.68, 0.40, 0.08, 18, 1,
        0.82, 0.78, 60, 1, 0.80, 3, 0, 1.0, 1
    ]
    
    metadata = {
        'current_price': 50000,
        'avg_volume': 1000000
    }
    
    # 生成决策
    result = ai.make_final_decision(features, metadata)
    
    # 打印报告
    print(ai.format_decision_report(result))
