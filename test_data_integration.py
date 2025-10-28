#!/usr/bin/env python3
"""
测试数据整合功能
演示如何将所有数据转换为AI友好的向量格式
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.gas_monitor import GasFeeMonitor
from utils.multi_source_fetcher import MultiSourceDataFetcher
from utils.sentiment_analyzer import MarketSentimentAnalyzer
from utils.data_integrator import DataIntegrator
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """主测试流程"""
    print("\n" + "="*80)
    print("🔄 数据整合测试 - 将多源数据转换为AI向量")
    print("="*80)
    
    # 1. 获取各类数据
    print("\n📊 步骤1: 获取原始数据...")
    
    # Gas数据
    gas_monitor = GasFeeMonitor(etherscan_key=getattr(config, 'ETHERSCAN_API_KEY', ''))
    gas_conditions = gas_monitor.check_trading_conditions()
    
    # K线数据
    fetcher = MultiSourceDataFetcher()
    kline_df = fetcher.aggregate_and_validate("BTCUSDT", limit=20)
    
    # 市场情绪
    analyzer = MarketSentimentAnalyzer()
    market_sentiment = analyzer.get_comprehensive_sentiment("BTC")
    
    # 2. 整合数据
    print("\n🔄 步骤2: 整合数据为向量...")
    integrator = DataIntegrator()
    
    integrated = integrator.integrate_all(
        gas_data=gas_conditions,
        kline_df=kline_df,
        market_sentiment=market_sentiment
    )
    
    # 3. 展示结果
    print("\n" + "="*80)
    print("📊 整合结果")
    print("="*80)
    
    print(f"\n✅ 特征维度: {integrated['feature_count']}")
    print(f"✅ 时间戳: {integrated['timestamp']}")
    
    # 显示特征向量
    print("\n📈 特征向量:")
    print("-" * 80)
    features = integrated['features']
    names = integrated['feature_names']
    
    for i, (name, value) in enumerate(zip(names, features)):
        if isinstance(value, float):
            print(f"  [{i:2d}] {name:25s} = {value:12.6f}")
        else:
            print(f"  [{i:2d}] {name:25s} = {value:12}")
    
    # 显示摘要
    print("\n📋 数据摘要:")
    print("-" * 80)
    summary = integrated['summary']
    for key, value in summary.items():
        print(f"  {key:20s}: {value}")
    
    # 4. 转换为不同格式
    print("\n" + "="*80)
    print("🔧 格式转换示例")
    print("="*80)
    
    # Numpy数组
    print("\n1️⃣  Numpy数组格式:")
    np_array = integrator.to_numpy_array(integrated)
    print(f"   Shape: {np_array.shape}")
    print(f"   Dtype: {np_array.dtype}")
    print(f"   前10个值: {np_array[:10]}")
    
    # 字典格式
    print("\n2️⃣  字典格式（部分）:")
    dict_format = integrator.to_dict(integrated)
    for i, (k, v) in enumerate(list(dict_format.items())[:5]):
        print(f"   '{k}': {v}")
    
    # AI Prompt格式
    print("\n3️⃣  AI Prompt格式:")
    print("-" * 80)
    prompt = integrator.format_for_ai_prompt(integrated)
    print(prompt)
    
    # 5. 保存结果
    print("\n" + "="*80)
    print("💾 保存结果")
    print("="*80)
    
    import json
    
    # 保存为JSON
    output_file = "data/integrated_features.json"
    with open(output_file, 'w') as f:
        json.dump(integrated, f, indent=2)
    
    print(f"✅ 已保存到: {output_file}")
    
    # 保存AI Prompt
    prompt_file = "data/ai_prompt.txt"
    with open(prompt_file, 'w') as f:
        f.write(prompt)
    
    print(f"✅ AI Prompt已保存到: {prompt_file}")
    
    # 6. 使用建议
    print("\n" + "="*80)
    print("💡 使用建议")
    print("="*80)
    
    print("""
1️⃣  发送给AI模型:
   prompt = integrator.format_for_ai_prompt(integrated)
   # 然后将prompt发送给Grok/Gemini/DeepSeek

2️⃣  机器学习训练:
   X = integrator.to_numpy_array(integrated)
   # 用于sklearn/tensorflow等模型

3️⃣  数据分析:
   df = pd.DataFrame([integrator.to_dict(integrated)])
   # 用pandas进行分析

4️⃣  实时决策:
   if integrated['summary']['gas_suitable']:
       if integrated['summary']['ai_consensus'] == 'bullish':
           # 执行买入逻辑
           pass
    """)
    
    # 7. 数据统计
    print("\n" + "="*80)
    print("📊 数据统计")
    print("="*80)
    
    feature_groups = {
        'Gas数据': ['eth_gas_gwei', 'btc_fee_sat', 'eth_tradeable', 'btc_tradeable'],
        'K线数据': ['current_price', 'price_change_pct', 'avg_volume', 'volatility', 'trend'],
        '新闻情绪': ['news_score', 'news_pos_ratio', 'news_neg_ratio', 'news_count', 'news_sentiment'],
        '市场情绪': ['market_sentiment_score', 'market_confidence', 'fear_greed_index', 'market_sentiment_label'],
        'AI预测': ['ai_avg_confidence', 'ai_up_count', 'ai_down_count', 'ai_agreement_ratio', 'ai_consensus']
    }
    
    dict_data = integrator.to_dict(integrated)
    
    for group_name, features in feature_groups.items():
        print(f"\n{group_name}:")
        available = sum(1 for f in features if f in dict_data and dict_data[f] != 0)
        print(f"  可用特征: {available}/{len(features)}")
        for feat in features:
            if feat in dict_data:
                val = dict_data[feat]
                if isinstance(val, float):
                    print(f"    {feat}: {val:.4f}")
                else:
                    print(f"    {feat}: {val}")
    
    print("\n" + "="*80)
    print("🎉 测试完成！")
    print("="*80)
    
    print(f"""
总结:
✅ 成功将多源数据整合为 {integrated['feature_count']} 维特征向量
✅ 数据已保存到 data/ 目录
✅ 可直接用于AI模型或机器学习

优势:
1. 省Token: 将复杂数据压缩为向量
2. 易理解: 特征名称清晰，有数据摘要
3. 多格式: 支持numpy、dict、prompt等格式
4. 实时性: 包含时间戳，可追溯
    """)


if __name__ == "__main__":
    main()
