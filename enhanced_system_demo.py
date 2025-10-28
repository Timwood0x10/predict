#!/usr/bin/env python3
"""
增强版交易系统演示
整合了Gas监控、多数据源、新闻分析、情绪预测

使用方法:
    python enhanced_system_demo.py
"""

import logging
from datetime import datetime
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入现有模块
from utils.data_fetcher import BinanceDataFetcher, format_klines_for_prompt
from models.ai_predictor import MultiModelPredictor
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedTradingSystem:
    """增强版交易系统"""
    
    def __init__(self):
        """初始化所有组件"""
        logger.info("="*80)
        logger.info("初始化增强版交易系统")
        logger.info("="*80)
        
        # 基础组件
        self.data_fetcher = BinanceDataFetcher()
        logger.info("✅ Binance数据获取器已初始化")
        
        self.ai_predictor = MultiModelPredictor({
            "deepseek": config.DEEPSEEK_API_KEY,
            "gemini": config.GEMINI_API_KEY
        })
        logger.info("✅ AI预测器已初始化")
        
        # 注意：新功能需要安装对应模块后才能使用
        # 这里先用占位符表示
        self.enhanced_features_available = False
        
        logger.info("="*80)
        logger.info("系统初始化完成！")
        logger.info("="*80)
    
    def basic_analysis(self, symbol="BTCUSDT"):
        """
        基础分析（使用现有功能）
        
        Args:
            symbol: 交易对
        
        Returns:
            分析报告
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"开始对 {symbol} 进行基础分析")
        logger.info(f"{'='*80}\n")
        
        report = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analysis": {}
        }
        
        # 1. 获取K线数据
        logger.info("📊 步骤 1/2: 获取K线数据...")
        klines = self.data_fetcher.fetch_recent_klines(symbol, minutes=15)
        
        if klines is not None:
            current_price = klines.iloc[-1]['close']
            report["analysis"]["kline_data"] = {
                "available": True,
                "data_points": len(klines),
                "latest_price": float(current_price),
                "price_change_24h": float((klines.iloc[-1]['close'] - klines.iloc[0]['close']) / klines.iloc[0]['close'] * 100)
            }
            
            # 2. AI预测
            logger.info("📊 步骤 2/2: 生成AI价格预测...")
            kline_text = format_klines_for_prompt(klines, limit=15)
            
            predictions = self.ai_predictor.predict_multiple_windows(
                prompt_template=config.PREDICTION_PROMPT_TEMPLATE,
                windows=[5, 15, 30],
                symbol=symbol,
                current_price=current_price,
                kline_data=kline_text
            )
            
            if not predictions.empty:
                report["analysis"]["ai_predictions"] = {
                    "available": True,
                    "count": len(predictions),
                    "predictions": predictions.to_dict('records')
                }
                
                # 简单决策
                decision = self._make_basic_decision(predictions, current_price)
                report["decision"] = decision
            else:
                report["analysis"]["ai_predictions"] = {"available": False}
                report["decision"] = {"action": "HOLD", "reason": "无AI预测数据"}
        else:
            report["analysis"]["kline_data"] = {"available": False}
            report["decision"] = {"action": "HOLD", "reason": "无K线数据"}
        
        self._print_report(report)
        
        return report
    
    def _make_basic_decision(self, predictions, current_price):
        """基础决策逻辑"""
        decision = {
            "action": "HOLD",
            "confidence": 0,
            "reasons": []
        }
        
        # 统计预测方向
        up_count = 0
        down_count = 0
        
        for _, pred in predictions.iterrows():
            if pred.get("grok_direction") == "up":
                up_count += 1
            elif pred.get("grok_direction") == "down":
                down_count += 1
            
            if pred.get("gemini_direction") == "up":
                up_count += 1
            elif pred.get("gemini_direction") == "down":
                down_count += 1
            
            if pred.get("deepseek_direction") == "up":
                up_count += 1
            elif pred.get("deepseek_direction") == "down":
                down_count += 1
        
        total = up_count + down_count
        
        if total > 0:
            if up_count > down_count * 1.5:
                decision["action"] = "BUY"
                decision["confidence"] = min(100, (up_count / total) * 100)
                decision["reasons"].append(f"🤖 AI预测看涨 ({up_count}/{total})")
            elif down_count > up_count * 1.5:
                decision["action"] = "SELL"
                decision["confidence"] = min(100, (down_count / total) * 100)
                decision["reasons"].append(f"🤖 AI预测看跌 ({down_count}/{total})")
            else:
                decision["action"] = "HOLD"
                decision["confidence"] = 50
                decision["reasons"].append("🤖 AI预测不明确")
        
        return decision
    
    def _print_report(self, report):
        """打印报告"""
        print("\n" + "="*80)
        print(f"📊 {report['symbol']} 分析报告")
        print("="*80)
        
        # K线数据
        kline = report["analysis"].get("kline_data", {})
        if kline.get("available"):
            print(f"\n📈 K线数据:")
            print(f"   数据点数: {kline['data_points']}")
            print(f"   最新价格: ${kline['latest_price']:.2f}")
            print(f"   24小时涨跌: {kline['price_change_24h']:.2f}%")
        
        # AI预测
        ai_preds = report["analysis"].get("ai_predictions", {})
        if ai_preds.get("available"):
            print(f"\n🤖 AI预测:")
            print(f"   预测数量: {ai_preds['count']}")
            
            for i, pred in enumerate(ai_preds['predictions'][:3], 1):
                print(f"\n   预测 #{i} (窗口: {pred.get('window_minutes', 'N/A')}分钟):")
                print(f"      Grok: {pred.get('grok_direction', 'N/A')} (置信度: {pred.get('grok_confidence', 0)}%)")
                print(f"      Gemini: {pred.get('gemini_direction', 'N/A')} (置信度: {pred.get('gemini_confidence', 0)}%)")
                print(f"      DeepSeek: {pred.get('deepseek_direction', 'N/A')} (置信度: {pred.get('deepseek_confidence', 0)}%)")
        
        # 决策
        decision = report.get("decision", {})
        print(f"\n🎯 交易建议:")
        print(f"   建议操作: {decision.get('action', 'N/A')}")
        print(f"   置信度: {decision.get('confidence', 0):.1f}%")
        if decision.get("reasons"):
            print(f"   原因:")
            for reason in decision["reasons"]:
                print(f"      {reason}")
        
        print("\n" + "="*80)


def print_banner():
    """打印横幅"""
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║          🚀 增强版加密货币交易系统演示                          ║
    ║                                                                ║
    ║  当前可用功能:                                                  ║
    ║    ✅ Binance K线数据获取                                      ║
    ║    ✅ 多AI模型价格预测                                         ║
    ║    ✅ 基础交易决策                                             ║
    ║                                                                ║
    ║  增强功能 (需要配置对应模块):                                   ║
    ║    🔧 Gas费用监控                                              ║
    ║    🔧 多数据源K线                                              ║
    ║    🔧 新闻情绪分析                                             ║
    ║    🔧 市场情绪预测                                             ║
    ║                                                                ║
    ║  提示: 查看 ENHANCEMENT_PLAN.md 了解如何启用增强功能           ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """主程序"""
    print_banner()
    
    try:
        # 创建系统
        system = EnhancedTradingSystem()
        
        # 进行分析
        symbols = ["BTCUSDT", "ETHUSDT"]
        
        for symbol in symbols:
            report = system.basic_analysis(symbol)
            
            # 保存报告
            filename = f"data/{symbol}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            
            print(f"\n✅ 报告已保存到 {filename}")
            print("\n" + "-"*80 + "\n")
        
        print("\n🎉 分析完成！")
        print("\n💡 下一步:")
        print("   1. 查看 ENHANCEMENT_PLAN.md 了解如何添加更多功能")
        print("   2. 配置 .env 文件中的API密钥")
        print("   3. 运行 test_system.py 验证系统")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  程序已停止")
    except Exception as e:
        logger.error(f"❌ 系统错误: {e}", exc_info=True)
        print(f"\n❌ 发生错误: {e}")
        print("请检查日志文件: logs/enhanced_system.log")


if __name__ == "__main__":
    main()
