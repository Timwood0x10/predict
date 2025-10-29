#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本 - 测试各个模块是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("加密货币价格预测系统 - 模块测试")
print("=" * 80)

# 测试1: 导入配置
print("\n[测试1] 配置模块")
try:
    import config
    print("✓ 配置模块导入成功")
    print(f"  - 交易对: {config.SYMBOLS}")
    print(f"  - 预测窗口: {config.PREDICTION_WINDOWS}")
    print(f"  - 数据目录: {config.DATA_DIR}")
except Exception as e:
    print(f"✗ 配置模块导入失败: {e}")
    sys.exit(1)

# 测试2: 数据获取模块
print("\n[测试2] 数据获取模块")
try:
    from utils.data_fetcher import BinanceDataFetcher
    fetcher = BinanceDataFetcher()
    print("✓ 数据获取模块导入成功")
    
    # 测试获取当前价格
    print("\n  测试获取BTC当前价格...")
    btc_price = fetcher.get_current_price("BTCUSDT")
    if btc_price:
        print(f"  ✓ BTC当前价格: ${btc_price:,.2f}")
    else:
        print("  ⚠ 无法获取BTC价格（可能是网络问题）")
    
    # 测试获取K线数据
    print("\n  测试获取K线数据...")
    klines = fetcher.fetch_klines("BTCUSDT", interval="1m", limit=5)
    if klines is not None:
        print(f"  ✓ 成功获取 {len(klines)} 条K线数据")
        print(f"  最新收盘价: ${klines.iloc[-1]['close']:,.2f}")
    else:
        print("  ⚠ 无法获取K线数据（可能是网络问题）")
        
except Exception as e:
    print(f"✗ 数据获取模块测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: AI预测模块
print("\n[测试3] AI预测模块")
try:
    from models.ai_predictor import MultiModelPredictor
    print("✓ AI预测模块导入成功")
    
    # 检查API密钥配置
    predictor = MultiModelPredictor(config.API_KEYS)
    active_models = list(predictor.predictors.keys())
    
    if active_models:
        print(f"  ✓ 已配置的模型: {', '.join(active_models)}")
    else:
        print("  ⚠ 没有配置任何模型API密钥")
        print("  请在 config.py 中设置API密钥")
    
except Exception as e:
    print(f"✗ AI预测模块测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 主程序
print("\n[测试4] 主程序模块")
try:
    import main
    print("✓ 主程序模块导入成功")
except Exception as e:
    print(f"✗ 主程序模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试5: 目录结构
print("\n[测试5] 目录结构")
required_dirs = [config.DATA_DIR, config.LOGS_DIR]
all_exist = True
for directory in required_dirs:
    if os.path.exists(directory):
        print(f"  ✓ {directory}/ 存在")
    else:
        print(f"  ⚠ {directory}/ 不存在，将自动创建")
        os.makedirs(directory, exist_ok=True)
        all_exist = False

if all_exist:
    print("  ✓ 所有必需目录都存在")

# 总结
print("\n" + "=" * 80)
print("测试总结")
print("=" * 80)

if btc_price and klines is not None:
    print("✓ 数据获取功能正常")
else:
    print("⚠ 数据获取可能存在问题（检查网络连接）")

if active_models:
    print(f"✓ AI预测功能已配置 ({len(active_models)}/3 个模型)")
else:
    print("⚠ 需要配置AI模型API密钥才能使用预测功能")

print("\n下一步:")
if not active_models:
    print("1. 在 config.py 中设置API密钥")
    print("2. 或设置环境变量:")
    print("   export GROK_API_KEY='your-key'")
    print("   export GEMINI_API_KEY='your-key'")
    print("   export DEEPSEEK_API_KEY='your-key'")
else:
    print("✓ 系统已就绪！运行以下命令开始预测:")
    print("   python main.py")

print("\n" + "=" * 80)
