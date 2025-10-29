#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有交易策略
"""

import sys
import logging
from strategies import (
    TrendFollowingStrategy,
    MeanReversionStrategy,
    BreakoutStrategy,
    GridStrategy,
    ScalpingStrategy
)

logging.basicConfig(level=logging.INFO)


def test_all_strategies():
    """测试所有策略"""
    
    print("="*80)
    print("🧪 交易策略测试")
    print("="*80)
    
    # 初始化所有策略
    strategies = {
        '趋势跟踪': TrendFollowingStrategy(),
        '均值回归': MeanReversionStrategy(),
        '突破策略': BreakoutStrategy(),
        '网格策略': GridStrategy(),
        '剥头皮': ScalpingStrategy()
    }
    
    # 测试场景
    scenarios = [
        {
            'name': '场景1: 强上涨趋势',
            'features': [
                15.0, 8.0, 1, 1, 50000, 3.5, 1500000, 0.020, 1,
                51500, 48500, 49000, 0.68, 0.40, 0.10, 18, 1,
                0.80, 0.75, 60, 1, 0.80, 3, 0, 1.0, 1
            ],
            'metadata': {'current_price': 50000, 'avg_volume': 1000000}
        },
        {
            'name': '场景2: 强下跌趋势',
            'features': [
                15.0, 8.0, 1, 1, 50000, -3.2, 1200000, 0.025, -1,
                50500, 48000, 50300, 0.32, 0.12, 0.40, 15, -1,
                0.75, 0.70, 35, -1, 0.78, 0, 3, 1.0, -1
            ],
            'metadata': {'current_price': 50000, 'avg_volume': 1000000}
        },
        {
            'name': '场景3: 震荡市场',
            'features': [
                15.0, 8.0, 1, 1, 50000, 0.3, 1000000, 0.015, 0,
                50300, 49700, 50000, 0.50, 0.25, 0.20, 10, 0,
                0.65, 0.60, 50, 0, 0.65, 1, 1, 0.50, 0
            ],
            'metadata': {'current_price': 50000, 'avg_volume': 1000000}
        },
        {
            'name': '场景4: 超卖反弹',
            'features': [
                15.0, 8.0, 1, 1, 50000, -4.5, 1800000, 0.035, -1,
                51000, 47500, 50800, 0.28, 0.10, 0.45, 20, -1,
                0.70, 0.75, 28, -1, 0.75, 0, 3, 1.0, -1
            ],
            'metadata': {'current_price': 50000, 'avg_volume': 1000000}
        },
        {
            'name': '场景5: 向上突破',
            'features': [
                15.0, 8.0, 1, 1, 50000, 2.2, 1600000, 0.018, 1,
                50100, 49000, 49200, 0.65, 0.35, 0.12, 16, 1,
                0.75, 0.72, 58, 1, 0.78, 2, 1, 0.75, 1
            ],
            'metadata': {'current_price': 50000, 'avg_volume': 1000000}
        }
    ]
    
    # 测试每个场景
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"📋 {scenario['name']}")
        print(f"{'='*80}")
        
        features = scenario['features']
        metadata = scenario['metadata']
        
        # 打印市场状态
        print(f"\n市场状态:")
        print(f"  价格: ${metadata['current_price']:,}")
        print(f"  24h涨跌: {features[5]:.2f}%")
        print(f"  波动率: {features[7]*100:.2f}%")
        print(f"  趋势: {features[8]}")
        
        # 测试每个策略
        print(f"\n策略信号:")
        results = {}
        
        for name, strategy in strategies.items():
            try:
                signal = strategy.analyze(features, metadata)
                
                if signal and signal['signal'] != 'NEUTRAL':
                    emoji = "🟢" if signal['signal'] == 'LONG' else "🔴"
                    print(f"  {emoji} {name}: {signal['signal']} (置信度: {signal['confidence']:.0f}%)")
                    print(f"      原因: {signal['reason']}")
                    results[name] = signal
                else:
                    print(f"  ⚪ {name}: NEUTRAL")
                    
            except Exception as e:
                print(f"  ❌ {name}: 出错 - {e}")
        
        # 统计
        long_count = sum(1 for s in results.values() if s['signal'] == 'LONG')
        short_count = sum(1 for s in results.values() if s['signal'] == 'SHORT')
        
        print(f"\n统计:")
        print(f"  看多: {long_count}个策略")
        print(f"  看空: {short_count}个策略")
        
        if long_count > short_count:
            print(f"  ✓ 综合判断: 做多机会")
        elif short_count > long_count:
            print(f"  ✓ 综合判断: 做空机会")
        else:
            print(f"  ✓ 综合判断: 信号不明确")
    
    # 策略说明
    print(f"\n{'='*80}")
    print("📖 策略说明")
    print(f"{'='*80}")
    
    for name, strategy in strategies.items():
        print(f"\n{name}:")
        print(strategy.get_description())
    
    print("="*80)
    print("✅ 测试完成！")
    print("="*80)


if __name__ == "__main__":
    test_all_strategies()
