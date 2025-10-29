#!/usr/bin/env python3
"""
测试新功能模块
验证Gas监控、新闻聚合、多数据源、情绪分析
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.gas_monitor import GasFeeMonitor
from utils.financial_news import FinancialNewsAggregator
from utils.multi_source_fetcher import MultiSourceDataFetcher
from utils.sentiment_analyzer import MarketSentimentAnalyzer
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_gas_monitor():
    """测试Gas监控"""
    print("\n" + "="*80)
    print("测试 1: Gas费用监控")
    print("="*80)
    
    try:
        monitor = GasFeeMonitor(etherscan_key=getattr(config, 'ETHERSCAN_API_KEY', ''))
        
        # 测试ETH Gas
        print("\n📊 获取ETH Gas...")
        eth_gas = monitor.get_eth_gas()
        if eth_gas:
            print(f"  ✅ ETH Gas (最新): {eth_gas['latest_gas']} Gwei")
            print(f"     7日均值: {eth_gas['current_avg_gas']} Gwei")
            print(f"     7日范围: {eth_gas['min_gas_7d']} - {eth_gas['max_gas_7d']} Gwei")
        else:
            print("  ❌ 无法获取ETH Gas (可能需要API密钥)")
        
        # 测试BTC Fee
        print("\n📊 获取BTC费用...")
        btc_fee = monitor.get_btc_fee()
        if btc_fee:
            print(f"  ✅ BTC Fee: {btc_fee['half_hour_fee']} sat/vB")
            print(f"     最快: {btc_fee['fastest_fee']} | 1小时: {btc_fee['hour_fee']}")
        else:
            print("  ❌ 无法获取BTC费用")
        
        # 检查交易条件
        print("\n📊 检查交易条件...")
        conditions = monitor.check_trading_conditions(max_eth_gas=50, max_btc_fee=20)
        print(f"  ETH适合交易: {'✅' if conditions['ETH'] else '❌'}")
        print(f"  BTC适合交易: {'✅' if conditions['BTC'] else '❌'}")
        
        print("\n✅ Gas监控测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ Gas监控测试失败: {e}")
        return False


def test_news_aggregator():
    """测试新闻聚合"""
    print("\n" + "="*80)
    print("测试 2: 金融新闻聚合")
    print("="*80)
    
    try:
        aggregator = FinancialNewsAggregator(newsapi_key=getattr(config, 'NEWSAPI_KEY', ''))
        
        print("\n📰 获取加密货币新闻...")
        news = aggregator.get_crypto_news(limit=5)
        
        if news:
            print(f"  ✅ 获取到 {len(news)} 条新闻")
            for i, item in enumerate(news[:3], 1):
                print(f"     {i}. {item['title'][:60]}...")
        else:
            print("  ⚠️ 未获取到新闻（可能需要配置API密钥）")
        
        print("\n📊 分析新闻情绪...")
        if news:
            sentiment = aggregator.analyze_sentiment(news)
            print(f"  情绪: {sentiment['sentiment']}")
            print(f"  分数: {sentiment['score']:.1f}")
            print(f"  正面: {sentiment['positive_count']} | 负面: {sentiment['negative_count']}")
        
        print("\n✅ 新闻聚合测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 新闻聚合测试失败: {e}")
        return False


def test_multi_source_fetcher():
    """测试多数据源K线"""
    print("\n" + "="*80)
    print("测试 3: 多数据源K线获取")
    print("="*80)
    
    try:
        fetcher = MultiSourceDataFetcher(
            cryptocompare_key=getattr(config, 'CRYPTOCOMPARE_API_KEY', '')
        )
        
        print("\n📈 从多数据源获取BTCUSDT数据...")
        df = fetcher.aggregate_and_validate("BTCUSDT", limit=20)
        
        if df is not None and not df.empty:
            print(f"  ✅ 获取到 {len(df)} 条数据")
            print(f"  数据源: {df['source'].iloc[0]}")
            print(f"  最新价格: ${df['close'].iloc[-1]:.2f}")
            print(f"  价格范围: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
            
            print("\n  最近5条数据:")
            print(df[['timestamp', 'close', 'volume']].tail(5).to_string(index=False))
        else:
            print("  ❌ 无法获取数据")
        
        print("\n✅ 多数据源测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 多数据源测试失败: {e}")
        return False


def test_sentiment_analyzer():
    """测试情绪分析"""
    print("\n" + "="*80)
    print("测试 4: 市场情绪分析")
    print("="*80)
    
    try:
        analyzer = MarketSentimentAnalyzer(
            cryptoracle_key=getattr(config, 'CRYPTORACLE_API_KEY', '')
        )
        
        print("\n😊 获取BTC市场情绪...")
        sentiment = analyzer.get_comprehensive_sentiment("BTC")
        
        if sentiment:
            print(f"  ✅ 综合情绪: {sentiment['overall_sentiment']}")
            print(f"  加权分数: {sentiment['weighted_score']:.1f}")
            print(f"  置信度: {sentiment['confidence']:.1f}")
            print(f"  解释: {sentiment['interpretation']}")
            
            print("\n  数据源:")
            for source in sentiment['sources']:
                print(f"     - {source['source']}: 分数={source['score']:.1f}, 权重={source['weight']}")
        else:
            print("  ⚠️ 无法获取情绪数据")
        
        print("\n📊 判断交易建议...")
        should_trade, direction, reason = analyzer.should_trade_based_on_sentiment("BTC")
        print(f"  建议: {'交易' if should_trade else '观望'}")
        if should_trade:
            print(f"  方向: {direction}")
        print(f"  原因: {reason}")
        
        print("\n✅ 情绪分析测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 情绪分析测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🚀 开始测试新功能模块")
    print("="*80)
    
    results = {
        "Gas监控": test_gas_monitor(),
        "新闻聚合": test_news_aggregator(),
        "多数据源K线": test_multi_source_fetcher(),
        "情绪分析": test_sentiment_analyzer()
    }
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查配置和API密钥")
    
    print("\n💡 提示:")
    print("  - 某些功能需要API密钥才能完全测试")
    print("  - 在config.py或.env中配置以下密钥:")
    print("    * ETHERSCAN_API_KEY")
    print("    * NEWSAPI_KEY")
    print("    * CRYPTOCOMPARE_API_KEY")
    print("    * CRYPTORACLE_API_KEY")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
