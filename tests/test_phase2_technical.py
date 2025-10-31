#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 技术指标测试
测试MACD、RSI、布林带、EMA、多周期分析、支撑阻力等功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import pandas as pd
import numpy as np
from utils.technical_indicators import TechnicalIndicators
from utils.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from utils.support_resistance import SupportResistanceFinder
from utils.data_fetcher import BinanceDataFetcher


class TestTechnicalIndicators(unittest.TestCase):
    """测试技术指标计算"""
    
    def setUp(self):
        """初始化测试数据"""
        self.tech = TechnicalIndicators()
        
        # 创建模拟K线数据（100根）
        np.random.seed(42)
        self.test_df = pd.DataFrame({
            'open': np.random.randn(100) * 100 + 50000,
            'high': np.random.randn(100) * 100 + 50100,
            'low': np.random.randn(100) * 100 + 49900,
            'close': np.random.randn(100) * 100 + 50000,
            'volume': np.random.randn(100) * 1000 + 10000
        })
        
        # 确保high >= close >= low
        self.test_df['high'] = self.test_df[['open', 'close', 'high']].max(axis=1)
        self.test_df['low'] = self.test_df[['open', 'close', 'low']].min(axis=1)
    
    def test_calculate_all(self):
        """测试计算所有指标"""
        result = self.tech.calculate_all(self.test_df)
        
        # 检查返回的键
        self.assertIn('macd_line', result)
        self.assertIn('macd_signal', result)
        self.assertIn('macd_hist', result)
        self.assertIn('rsi', result)
        self.assertIn('bb_position', result)
        self.assertIn('ema_trend', result)
        
        # 检查数据类型
        self.assertIsInstance(result['macd_line'], float)
        self.assertIsInstance(result['rsi'], float)
        self.assertIsInstance(result['bb_position'], float)
        self.assertIsInstance(result['ema_trend'], int)
        
        print("\n✅ 技术指标计算测试通过")
        print(f"   MACD: {result['macd_line']:.2f}")
        print(f"   RSI: {result['rsi']:.1f}")
        print(f"   布林带位置: {result['bb_position']:.2f}")
        print(f"   EMA趋势: {result['ema_trend']}")
    
    def test_rsi_range(self):
        """测试RSI范围在0-100之间"""
        result = self.tech.calculate_all(self.test_df)
        rsi = result['rsi']
        
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
        
        print(f"\n✅ RSI范围测试通过: {rsi:.1f}")
    
    def test_bb_position_range(self):
        """测试布林带位置在0-1之间"""
        result = self.tech.calculate_all(self.test_df)
        bb_pos = result['bb_position']
        
        self.assertGreaterEqual(bb_pos, 0)
        self.assertLessEqual(bb_pos, 1)
        
        print(f"\n✅ 布林带位置测试通过: {bb_pos:.2f}")
    
    def test_ema_trend_values(self):
        """测试EMA趋势值在-1,0,1之间"""
        result = self.tech.calculate_all(self.test_df)
        ema_trend = result['ema_trend']
        
        self.assertIn(ema_trend, [-1, 0, 1])
        
        print(f"\n✅ EMA趋势测试通过: {ema_trend}")
    
    def test_insufficient_data(self):
        """测试数据不足的情况"""
        small_df = self.test_df.head(10)  # 只有10根K线
        result = self.tech.calculate_all(small_df)
        
        # 应该返回默认值
        self.assertIsInstance(result, dict)
        self.assertEqual(result['rsi'], 50)  # 默认RSI
        
        print("\n✅ 数据不足测试通过（返回默认值）")


class TestSupportResistance(unittest.TestCase):
    """测试支撑阻力识别"""
    
    def setUp(self):
        """初始化测试数据"""
        self.sr_finder = SupportResistanceFinder()
        
        # 创建有明显支撑阻力的数据
        prices = [50000 + i*10 + np.random.randn()*50 for i in range(100)]
        self.test_df = pd.DataFrame({
            'open': prices,
            'high': [p + abs(np.random.randn()*100) for p in prices],
            'low': [p - abs(np.random.randn()*100) for p in prices],
            'close': prices,
            'volume': np.random.randn(100) * 1000 + 10000
        })
        
        self.current_price = 50500
    
    def test_find_levels(self):
        """测试找到支撑阻力位"""
        result = self.sr_finder.find_levels(self.test_df, self.current_price)
        
        # 检查返回的键
        self.assertIn('nearest_support', result)
        self.assertIn('nearest_resistance', result)
        self.assertIn('support_distance', result)
        self.assertIn('resistance_distance', result)
        
        # 检查支撑位低于当前价，阻力位高于当前价
        self.assertLess(result['nearest_support'], self.current_price)
        self.assertGreater(result['nearest_resistance'], self.current_price)
        
        print("\n✅ 支撑阻力识别测试通过")
        print(f"   当前价格: ${self.current_price:,.2f}")
        print(f"   支撑位: ${result['nearest_support']:,.2f} (距离{result['support_distance']:.2f}%)")
        print(f"   阻力位: ${result['nearest_resistance']:,.2f} (距离{result['resistance_distance']:.2f}%)")
    
    def test_distance_positive(self):
        """测试距离为正数"""
        result = self.sr_finder.find_levels(self.test_df, self.current_price)
        
        self.assertGreaterEqual(result['support_distance'], 0)
        self.assertGreaterEqual(result['resistance_distance'], 0)
        
        print("\n✅ 距离计算测试通过")
    
    def test_insufficient_data(self):
        """测试数据不足的情况"""
        small_df = self.test_df.head(5)
        result = self.sr_finder.find_levels(small_df, self.current_price)
        
        # 应该返回默认值
        self.assertIsInstance(result, dict)
        self.assertIn('nearest_support', result)
        
        print("\n✅ 支撑阻力数据不足测试通过")


class TestMultiTimeframeAnalyzer(unittest.TestCase):
    """测试多周期分析器"""
    
    def setUp(self):
        """初始化"""
        # 注意：这个测试需要真实的数据获取器
        # 在实际测试中可能需要mock
        pass
    
    def test_trend_values(self):
        """测试趋势值的有效性"""
        # 这个测试需要真实数据，暂时跳过
        # 可以在集成测试中进行
        print("\n⚠️ 多周期分析器需要实时数据，建议在集成测试中测试")


class TestDataIntegration(unittest.TestCase):
    """测试数据整合（包含Phase2的12个新维度）"""
    
    def setUp(self):
        """初始化"""
        from utils.data_integrator import DataIntegrator
        self.integrator = DataIntegrator()
        
        # 准备测试数据
        self.tech_indicators = {
            'macd_line': 10.5,
            'macd_signal': 8.3,
            'macd_hist': 2.2,
            'rsi': 65.0,
            'bb_position': 0.7,
            'ema_trend': 1
        }
        
        self.multi_timeframe = {
            'timeframes': {
                '1m': {'trend': 1, 'rsi': 60},
                '15m': {'trend': 1, 'rsi': 62},
                '1h': {'trend': 0, 'rsi': 55},
                '4h': {'trend': 1, 'rsi': 58}
            },
            'trend_consistency': 0.75,
            'overall_trend': 1
        }
        
        self.support_resistance = {
            'nearest_support': 49500,
            'nearest_resistance': 51000,
            'support_distance': 1.5,
            'resistance_distance': 2.0
        }
    
    def test_integrate_phase2_features(self):
        """测试整合Phase2的新特征"""
        result = self.integrator.integrate_all(
            technical_indicators=self.tech_indicators,
            multi_timeframe=self.multi_timeframe,
            support_resistance=self.support_resistance
        )
        
        features = result['features']
        names = result['feature_names']
        
        # 检查是否包含Phase2的特征
        self.assertIn('macd_line', names)
        self.assertIn('rsi', names)
        self.assertIn('trend_1m', names)
        self.assertIn('trend_4h', names)
        self.assertIn('support_distance', names)
        
        # 检查维度数量（应该包含Phase2的12维）
        # 基础26维 + Phase1的9维 + Phase2的12维 = 47维
        self.assertGreaterEqual(len(features), 47)
        
        print(f"\n✅ Phase2特征整合测试通过")
        print(f"   总维度: {len(features)}维")
        print(f"   包含MACD: {'macd_line' in names}")
        print(f"   包含多周期: {'trend_1m' in names}")
        print(f"   包含支撑阻力: {'support_distance' in names}")
    
    def test_format_for_ai_prompt(self):
        """测试AI提示词格式化（包含Phase2信息）"""
        integrated_data = self.integrator.integrate_all(
            technical_indicators=self.tech_indicators,
            multi_timeframe=self.multi_timeframe,
            support_resistance=self.support_resistance
        )
        
        prompt = self.integrator.format_for_ai_prompt(
            integrated_data,
            technical_indicators=self.tech_indicators,
            multi_timeframe=self.multi_timeframe,
            support_resistance=self.support_resistance
        )
        
        # 检查提示词是否包含关键信息
        self.assertIn('MACD', prompt)
        self.assertIn('RSI', prompt)
        self.assertIn('多周期', prompt)
        self.assertIn('支撑', prompt)
        self.assertIn('阻力', prompt)
        self.assertIn('Phase 2', prompt)
        
        print("\n✅ AI提示词格式化测试通过")
        print(f"   提示词长度: {len(prompt)} 字符")
        print(f"   包含技术指标: ✓")
        print(f"   包含多周期分析: ✓")
        print(f"   包含支撑阻力: ✓")


def run_tests():
    """运行所有测试"""
    print("="*80)
    print("Phase 2 技术指标测试套件")
    print("="*80)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTechnicalIndicators))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSupportResistance))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMultiTimeframeAnalyzer))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDataIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("="*80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
