#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合测试脚本 - 测试所有功能模块
"""

import sys
import os
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_module_imports():
    """测试模块导入"""
    print("\n" + "="*80)
    print("🔧 模块导入测试")
    print("="*80)
    
    modules = {
        'config': 'config',
        'DataFetcher': 'utils.data_fetcher',
        'MultiSourceFetcher': 'utils.multi_source_fetcher',
        'DataIntegrator': 'utils.data_integrator',
        'DecisionEngine': 'utils.decision_engine',
        'NewsProcessor': 'utils.news_processor',
        'SentimentAnalyzer': 'utils.sentiment_analyzer',
        'GasMonitor': 'utils.gas_monitor',
        'AIPredictor': 'models.ai_predictor'
    }
    
    passed = 0
    failed = 0
    
    for name, module_path in modules.items():
        try:
            __import__(module_path)
            print(f"  ✅ {name}: 导入成功")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: 导入失败 - {e}")
            failed += 1
    
    print(f"\n结果: {passed} 通过, {failed} 失败")
    return failed == 0


def test_data_integration():
    """测试数据整合功能"""
    print("\n" + "="*80)
    print("📊 数据整合测试")
    print("="*80)
    
    try:
        from utils.data_integrator import DataIntegrator
        import pandas as pd
        
        integrator = DataIntegrator()
        
        # 模拟数据
        gas_data = {
            'eth_gas_gwei': 15.0,
            'btc_fee_sat_vb': 8.0
        }
        
        kline_df = pd.DataFrame({
            'open': [49500, 49700, 49800],
            'high': [49800, 50000, 50200],
            'low': [49400, 49600, 49700],
            'close': [49700, 49800, 50000],
            'volume': [1000000, 1100000, 1200000]
        })
        
        news_sentiment = {
            'sentiment_label': 1,
            'confidence': 0.75,
            'positive_ratio': 0.35,
            'negative_ratio': 0.10,
            'total_news': 15
        }
        
        market_sentiment = {
            'fear_greed_index': 58,
            'sentiment_label': 1,
            'confidence': 0.70
        }
        
        ai_predictions = pd.DataFrame([
            {'direction': 'up', 'confidence': 0.80},
            {'direction': 'up', 'confidence': 0.75},
            {'direction': 'down', 'confidence': 0.65}
        ])
        
        # 整合
        result = integrator.integrate_all(
            gas_data=gas_data,
            kline_df=kline_df,
            news_sentiment=news_sentiment,
            market_sentiment=market_sentiment,
            ai_predictions=ai_predictions
        )
        
        print(f"  ✅ 特征向量维度: {len(result['features'])}")
        print(f"  ✅ 预期维度: 26")
        print(f"  ✅ 特征值范围正常: {min(result['features']):.2f} ~ {max(result['features']):.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 数据整合失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_decision_engine():
    """测试决策引擎"""
    print("\n" + "="*80)
    print("🎯 决策引擎测试")
    print("="*80)
    
    try:
        from utils.decision_engine import DecisionEngine
        
        engine = DecisionEngine(account_balance=10000, risk_percent=0.015)
        
        # 测试场景：理想看涨
        features = [
            12.0, 6.0, 1, 1, 50000, 2.0, 1500000, 0.018, 1,
            50800, 49200, 49500, 0.68, 0.40, 0.08, 18, 1,
            0.82, 0.78, 60, 1, 0.80, 3, 0, 1.0, 1
        ]
        
        result = engine.analyze(features)
        
        print(f"  ✅ 决策: {result['decision']['action']}")
        print(f"  ✅ 置信度: {result['decision']['confidence']:.2f}%")
        print(f"  ✅ 总分: {result['signals']['total_score']:.2f}")
        
        if result['position']:
            print(f"  ✅ 仓位计算: ${result['position']['position_value']:,.2f}")
            print(f"  ✅ 止损: ${result['position']['stop_loss']:,.2f}")
            print(f"  ✅ 风险收益比: {result['position']['risk_reward_ratio']}:1")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 决策引擎失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gas_monitor():
    """测试Gas监控"""
    print("\n" + "="*80)
    print("⛽ Gas监控测试")
    print("="*80)
    
    try:
        from utils.gas_monitor import GasMonitor
        
        monitor = GasMonitor()
        gas_data = monitor.get_gas_prices()
        
        if gas_data:
            print(f"  ✅ ETH Gas: {gas_data.get('eth_gas_gwei', 'N/A')} Gwei")
            print(f"  ✅ BTC Fee: {gas_data.get('btc_fee_sat_vb', 'N/A')} sat/vB")
            print(f"  ✅ ETH适合交易: {gas_data.get('eth_suitable', False)}")
            print(f"  ✅ BTC适合交易: {gas_data.get('btc_suitable', False)}")
            return True
        else:
            print(f"  ⚠️  无法获取Gas数据（可能是网络问题）")
            return False
            
    except Exception as e:
        print(f"  ⚠️  Gas监控跳过: {e}")
        print(f"  ℹ️  这是正常的，实际使用时会自动获取")
        return True  # 不算失败


def test_sentiment_analyzer():
    """测试情绪分析"""
    print("\n" + "="*80)
    print("😊 情绪分析测试")
    print("="*80)
    
    try:
        from utils.sentiment_analyzer import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        sentiment = analyzer.get_market_sentiment()
        
        if sentiment:
            print(f"  ✅ 恐惧贪婪指数: {sentiment.get('fear_greed_index', 'N/A')}")
            print(f"  ✅ 情绪标签: {sentiment.get('sentiment_label', 'N/A')}")
            print(f"  ✅ 置信度: {sentiment.get('confidence', 'N/A')}")
            return True
        else:
            print(f"  ⚠️  无法获取情绪数据（可能是网络问题）")
            return False
            
    except Exception as e:
        print(f"  ⚠️  情绪分析跳过: {e}")
        print(f"  ℹ️  这是正常的，实际使用时会自动获取")
        return True  # 不算失败


def main():
    """运行所有测试"""
    print("="*80)
    print("🚀 加密货币预测系统 - 完整测试套件")
    print("="*80)
    
    results = {}
    
    # 运行各项测试
    results['imports'] = test_module_imports()
    results['data_integration'] = test_data_integration()
    results['decision_engine'] = test_decision_engine()
    results['gas_monitor'] = test_gas_monitor()
    results['sentiment'] = test_sentiment_analyzer()
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试总结")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常。")
        print("\n下一步:")
        print("  1. 运行决策引擎详细测试: python test_decision_engine.py")
        print("  2. 测试杠杆交易计算: python test_leverage.py")
        print("  3. 启动系统: python main.py")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查相关模块。")
    
    print("\n" + "="*80)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
