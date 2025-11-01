#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实交易决策系统 - 双向交易（做多/做空）
整合AI决策层 + 决策引擎，给出完整的交易建议
"""

import sys
import os
import logging
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 导入所有组件
from utils.gas_monitor import GasFeeMonitor
from utils.data_fetcher import BinanceDataFetcher
from utils.financial_news import FinancialNewsAggregator
from utils.sentiment_analyzer import MarketSentimentAnalyzer
from utils.data_integrator import DataIntegrator
from utils.decision_engine import DecisionEngine
from utils.dynamic_weights import DynamicWeightManager
from ai_decision_layer import AIDecisionLayer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealTradingDecisionSystem:
    """真实交易决策系统"""
    
    def __init__(self, account_balance=10000, risk_percent=0.015):
        """
        初始化交易决策系统
        
        Args:
            account_balance: 账户余额
            risk_percent: 单笔风险比例（默认1.5%）
        """
        logger.info("=" * 80)
        logger.info("🚀 初始化真实交易决策系统")
        logger.info("=" * 80)
        
        # 获取API密钥（兼容两种格式）
        newsapi_key = os.getenv('NEWSAPI_KEY') or os.getenv('NEWS_API_KEY') or ''
        
        # 初始化数据获取组件
        self.gas_monitor = GasFeeMonitor()
        self.data_fetcher = BinanceDataFetcher()
        self.news_api = FinancialNewsAggregator(newsapi_key=newsapi_key)
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        self.data_integrator = DataIntegrator()
        
        # 初始化决策组件
        self.decision_engine = DecisionEngine(
            account_balance=account_balance,
            risk_percent=risk_percent
        )
        self.ai_decision_layer = AIDecisionLayer(
            account_balance=account_balance,
            risk_percent=risk_percent
        )
        self.weight_manager = DynamicWeightManager()  # 动态权重管理器
        
        logger.info("✅ 所有组件初始化完成")
        logger.info(f"   账户余额: ${account_balance:,.2f}")
        logger.info(f"   单笔风险: {risk_percent*100:.2f}%")
        logger.info(f"   动态权重: 已启用")
    
    def fetch_market_data(self, symbol="BTCUSDT", hours=12):
        """
        获取市场数据
        
        Args:
            symbol: 交易对
            hours: 分析的小时数（默认12小时）
            
        Returns:
            dict: 市场数据
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"📊 获取 {symbol} 市场数据（最近{hours}小时）")
        logger.info("=" * 80)
        
        all_data = {}
        
        # 1. Gas费用
        logger.info("\n[1/5] 获取Gas费用...")
        try:
            gas_data = self.gas_monitor.get_all_fees()
            if gas_data:
                eth_suitable = self.gas_monitor.should_trade_eth()
                btc_suitable = self.gas_monitor.should_trade_btc()
                all_data['gas_data'] = {
                    'ETH': eth_suitable,
                    'BTC': btc_suitable,
                    'details': gas_data
                }
                logger.info(f"   ✓ ETH Gas: {gas_data.get('ETH', {}).get('latest_gas', 'N/A')} Gwei")
                logger.info(f"   ✓ BTC Fee: {gas_data.get('BTC', {}).get('half_hour_fee', 'N/A')} sat/vB")
            else:
                all_data['gas_data'] = None
        except Exception as e:
            logger.error(f"   ✗ 获取失败: {e}")
            all_data['gas_data'] = None
        
        # 2. K线数据（获取更多数据点，但只分析最近hours小时）
        logger.info(f"\n[2/5] 获取K线数据（分析最近{hours}小时）...")
        try:
            # 获取足够的数据点用于技术分析
            kline_df = self.data_fetcher.fetch_klines(symbol=symbol, interval="1h", limit=100)
            all_data['kline_df'] = kline_df
            all_data['analysis_hours'] = hours
            
            if kline_df is not None and not kline_df.empty:
                current_price = kline_df.iloc[-1]['close']
                
                # 计算指定小时数的价格变化
                if len(kline_df) >= hours:
                    start_price = kline_df.iloc[-hours]['close']
                else:
                    start_price = kline_df.iloc[0]['close']
                
                price_change = ((current_price - start_price) / start_price) * 100
                logger.info(f"   ✓ 当前价格: ${current_price:,.2f}")
                logger.info(f"   ✓ {hours}h价格变化: {price_change:+.2f}%")
                logger.info(f"   ✓ {hours}h前价格: ${start_price:,.2f}")
        except Exception as e:
            logger.error(f"   ✗ 获取失败: {e}")
            all_data['kline_df'] = None
        
        # 3. 新闻数据
        logger.info("\n[3/5] 获取新闻...")
        try:
            news_list = self.news_api.get_all_news(crypto_limit=10, macro_limit=5, include_chinese=True)
            all_data['news_list'] = news_list
            if news_list:
                news_sentiment = self.news_api.analyze_sentiment(news_list)
                all_data['news_sentiment'] = news_sentiment
                logger.info(f"   ✓ 新闻数量: {len(news_list)}条")
                logger.info(f"   ✓ 情绪: {news_sentiment.get('sentiment', 'N/A')}")
        except Exception as e:
            logger.error(f"   ✗ 获取失败: {e}")
            all_data['news_list'] = []
            all_data['news_sentiment'] = None
        
        # 4. 市场情绪
        logger.info("\n[4/5] 分析市场情绪...")
        try:
            market_sentiment = self.sentiment_analyzer.get_comprehensive_sentiment(symbol="BTC")
            all_data['market_sentiment'] = market_sentiment
            if market_sentiment:
                logger.info(f"   ✓ 情绪: {market_sentiment.get('overall_sentiment', 'N/A')}")
                logger.info(f"   ✓ 恐惧贪婪指数: {market_sentiment.get('sources', [{}])[0].get('score', 'N/A')}")
        except Exception as e:
            logger.error(f"   ✗ 获取失败: {e}")
            all_data['market_sentiment'] = None
        
        # 5. 生成AI预测
        logger.info("\n[5/5] 生成AI预测...")
        ai_predictions = self._generate_ai_predictions(
            news_sentiment=all_data.get('news_sentiment'),
            market_sentiment=all_data.get('market_sentiment'),
            kline_df=all_data.get('kline_df')
        )
        all_data['ai_predictions'] = ai_predictions
        logger.info(f"   ✓ AI预测已生成")
        
        return all_data
    
    def _generate_ai_predictions(self, news_sentiment, market_sentiment, kline_df):
        """基于市场数据生成AI预测"""
        direction = 'up'
        confidence = 60
        
        # 综合分析
        bullish_signals = 0
        bearish_signals = 0
        
        # 新闻信号
        if news_sentiment:
            news_sent = news_sentiment.get('sentiment', 'neutral')
            if news_sent == 'bullish':
                bullish_signals += 1
            elif news_sent == 'bearish':
                bearish_signals += 1
        
        # 市场情绪信号
        if market_sentiment:
            market_sent = market_sentiment.get('overall_sentiment', 'neutral')
            if market_sent == 'bullish':
                bullish_signals += 1
            elif market_sent == 'bearish':
                bearish_signals += 1
        
        # 价格趋势信号
        if kline_df is not None and not kline_df.empty:
            price_change = ((kline_df.iloc[-1]['close'] - kline_df.iloc[0]['close']) / kline_df.iloc[0]['close']) * 100
            if price_change > 1.5:
                bullish_signals += 1
            elif price_change < -1.5:
                bearish_signals += 1
        
        # 综合判断
        if bullish_signals > bearish_signals:
            direction = 'up'
            confidence = min(85, 60 + (bullish_signals - bearish_signals) * 10)
        elif bearish_signals > bullish_signals:
            direction = 'down'
            confidence = min(85, 60 + (bearish_signals - bullish_signals) * 10)
        else:
            direction = 'up'
            confidence = 55
        
        # 创建预测数据
        return pd.DataFrame({
            'timestamp': [datetime.now()],
            'grok_direction': [direction],
            'grok_confidence': [confidence],
            'gemini_direction': [direction],
            'gemini_confidence': [max(50, confidence - 5)],
            'deepseek_direction': [direction],
            'deepseek_confidence': [min(90, confidence + 5)]
        })
    
    def analyze_and_decide(self, symbol="BTCUSDT"):
        """
        完整的分析和决策流程
        
        Args:
            symbol: 交易对
            
        Returns:
            dict: 完整的决策结果
        """
        start_time = datetime.now()
        
        print("\n")
        print("=" * 80)
        print("🤖 加密货币双向交易决策系统")
        print("=" * 80)
        print(f"交易对: {symbol}")
        print(f"时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # 步骤1: 获取市场数据
            market_data = self.fetch_market_data(symbol)
            
            # 步骤2: 整合特征向量
            logger.info("\n" + "=" * 80)
            logger.info("🔄 整合26维特征向量")
            logger.info("=" * 80)
            
            # 传递hours参数到数据整合器
            hours = market_data.get('analysis_hours', 12)
            integrated_data = self.data_integrator.integrate_all(
                gas_data=market_data.get('gas_data'),
                kline_df=market_data.get('kline_df'),
                news_sentiment=market_data.get('news_sentiment'),
                market_sentiment=market_data.get('market_sentiment'),
                ai_predictions=market_data.get('ai_predictions'),
                hours=hours
            )
            
            features = integrated_data['features']
            
            # 获取当前价格和元数据
            current_price = features[4] if len(features) > 4 else 0
            metadata = {
                'current_price': current_price,
                'avg_volume': features[6] if len(features) > 6 else 0
            }
            
            # 步骤2.5: 应用动态权重调整
            logger.info("\n" + "=" * 80)
            logger.info("⚖️ 动态权重调整")
            logger.info("=" * 80)
            
            # 识别市场状态
            market_state = self.weight_manager.get_market_state(features)
            logger.info(f"   市场状态: {market_state}")
            
            # 获取推荐权重
            recommended_weights = self.weight_manager.get_weights(market_state)
            logger.info(f"   推荐权重: {recommended_weights}")
            
            # 根据特征微调权重
            adjusted_weights = self.weight_manager.adjust_weights_by_dimensions(
                recommended_weights, 
                features
            )
            logger.info(f"   调整后权重: {adjusted_weights}")
            
            # 将调整后的权重存储到元数据中供决策使用
            metadata['dynamic_weights'] = adjusted_weights
            metadata['market_state'] = market_state
            
            # 步骤3: AI决策层分析
            logger.info("\n" + "=" * 80)
            logger.info("🤖 AI决策层分析")
            logger.info("=" * 80)
            
            ai_decision = self.ai_decision_layer.make_final_decision(
                features=features,
                metadata=metadata,
                use_aggregation=False  # 使用最优策略选择
            )
            
            # 步骤4: 决策引擎验证
            logger.info("\n" + "=" * 80)
            logger.info("🎯 决策引擎验证")
            logger.info("=" * 80)
            
            engine_decision = self.decision_engine.analyze(
                features=features,
                news_data=market_data.get('news_list', [])
            )
            
            # 步骤5: 综合决策
            final_decision = self._merge_decisions(ai_decision, engine_decision, current_price)
            
            # 添加元数据到最终决策
            final_decision['metadata'] = metadata
            
            # 计算耗时
            elapsed = (datetime.now() - start_time).total_seconds()
            final_decision['elapsed_time'] = elapsed
            
            # 打印决策报告
            self._print_decision_report(final_decision)
            
            return final_decision
            
        except Exception as e:
            logger.error(f"\n❌ 决策过程出错: {e}", exc_info=True)
            return None
    
    def _merge_decisions(self, ai_decision, engine_decision, current_price):
        """
        综合AI决策层和决策引擎的结果
        
        决策逻辑：
        1. 决策引擎有否决权（安全检查）
        2. AI决策层提供方向建议
        3. 综合判断最终决策
        """
        # 提取关键信息
        ai_action = ai_decision['decision']['action']  # LONG/SHORT/NEUTRAL
        ai_confidence = ai_decision['decision']['confidence']
        
        engine_action = engine_decision['decision']['action']  # BUY/SELL/HOLD
        engine_confidence = engine_decision['decision']['confidence']
        engine_signals = engine_decision.get('signals', {})
        
        # 决策引擎的安全检查结果
        safety_passed = engine_decision.get('safety_checks', {}).get('passed', False)
        
        # 综合决策逻辑
        final_action = "HOLD"
        final_confidence = 0
        final_reason = ""
        position_info = None
        
        # 情况1: 安全检查未通过，强制HOLD
        if not safety_passed:
            final_action = "HOLD"
            final_confidence = 0
            final_reason = f"❌ 安全检查未通过: {engine_decision['safety_checks']['reason']}"
        
        # 情况2: 安全检查通过，综合AI和引擎的建议
        else:
            # AI建议做多 & 引擎允许买入
            if ai_action == "LONG" and engine_action in ["BUY", "HOLD"]:
                if engine_signals.get('total_score', 0) >= 65:  # 降低阈值到65
                    final_action = "LONG"
                    final_confidence = (ai_confidence + engine_signals['total_score']) / 2
                    final_reason = f"✅ AI建议做多 + 决策引擎支持 (AI置信度:{ai_confidence:.0f}%, 引擎评分:{engine_signals['total_score']:.0f}分)"
                    position_info = self._calculate_long_position(current_price, features=engine_decision)
                else:
                    final_action = "HOLD"
                    final_confidence = 50
                    final_reason = f"⚠️ AI建议做多，但引擎评分不足 (需要≥65分, 当前{engine_signals['total_score']:.0f}分)"
            
            # AI建议做空 & 引擎允许卖出
            elif ai_action == "SHORT" and engine_action in ["SELL", "HOLD"]:
                if engine_signals.get('total_score', 0) <= 55:  # 调整阈值到55（对称于做多的65）
                    final_action = "SHORT"
                    final_confidence = (ai_confidence + (100 - engine_signals['total_score'])) / 2
                    final_reason = f"✅ AI建议做空 + 决策引擎支持 (AI置信度:{ai_confidence:.0f}%, 引擎评分:{engine_signals['total_score']:.0f}分)"
                    position_info = self._calculate_short_position(current_price, features=engine_decision)
                else:
                    final_action = "HOLD"
                    final_confidence = 50
                    final_reason = f"⚠️ AI建议做空，但引擎评分不足 (需要≤55分, 当前{engine_signals['total_score']:.0f}分)"
            
            # AI中性 或 AI与引擎冲突
            else:
                final_action = "HOLD"
                final_confidence = 50
                if ai_action == "NEUTRAL":
                    final_reason = f"⚪ AI判断市场中性，建议观望"
                else:
                    final_reason = f"⚠️ AI({ai_action})与引擎({engine_action})信号冲突，保守观望"
        
        return {
            'final_decision': {
                'action': final_action,
                'confidence': final_confidence,
                'reason': final_reason,
                'position': position_info
            },
            'ai_decision': ai_decision,
            'engine_decision': engine_decision,
            'current_price': current_price
        }
    
    def _calculate_long_position(self, current_price, features):
        """计算做多仓位（保守策略）"""
        # 从决策引擎获取仓位信息
        pos = features.get('position')
        
        if pos and current_price > 0:
            # 调整为更保守的止盈止损（注意：stop_loss_percent是百分数，如3.0表示3%）
            stop_loss_pct = pos['stop_loss_percent'] / 100 * 0.8  # 从百分数转换回小数，并缩小20%（更紧的止损）
            stop_loss = current_price * (1 - stop_loss_pct)
            
            # 更保守的止盈：2%, 3.5%, 5%（原来是4.5%, 7.5%, 12%）
            take_profit_1 = current_price * 1.02   # 2%
            take_profit_2 = current_price * 1.035  # 3.5%
            take_profit_3 = current_price * 1.05   # 5%
            
            return {
                'direction': 'LONG',
                'entry_price': current_price,
                'position_size': pos['position_size'],
                'position_value': pos['position_value'],
                'position_percent': pos['position_percent'],
                'stop_loss': stop_loss,
                'stop_loss_percent': stop_loss_pct,
                'take_profit_1': take_profit_1,
                'take_profit_2': take_profit_2,
                'take_profit_3': take_profit_3,
                'max_loss': current_price * pos['position_size'] * stop_loss_pct,
                'expected_profit': pos['expected_profit'] * 0.6,  # 预期利润降低
                'risk_reward_ratio': 2.0  # 保守的2:1
            }
        
        # 如果决策引擎没有计算，我们自己计算
        from utils.decision_engine import DecisionEngine
        engine = DecisionEngine(account_balance=self.decision_engine.account_balance)
        volatility = features.get('signals', {}).get('price_score', 0.02) / 100
        
        position_info = engine.calculate_position_and_stops(
            entry_price=current_price,
            direction="BUY",
            volatility=max(0.015, volatility)
        )
        
        return {
            'direction': 'LONG',
            'entry_price': current_price,
            **position_info
        }
    
    def _calculate_short_position(self, current_price, features):
        """计算做空仓位（保守策略）"""
        # 从决策引擎获取仓位信息（针对做空调整）
        from utils.decision_engine import DecisionEngine
        engine = DecisionEngine(account_balance=self.decision_engine.account_balance)
        
        # 获取波动率
        volatility = 0.02  # 默认2%
        if features.get('signals'):
            # 从价格信号推算波动率
            price_score = features['signals'].get('price_score', 50)
            volatility = max(0.015, (100 - price_score) / 100 * 0.05)
        
        # 计算做空仓位（使用SELL方向）
        position_info = engine.calculate_position_and_stops(
            entry_price=current_price,
            direction="SELL",
            volatility=volatility
        )
        
        # 更保守的止盈止损（注意：stop_loss_percent已经是小数，如0.03表示3%）
        stop_loss_pct = position_info['stop_loss_percent'] / 100 * 0.8  # 从百分数转换回小数，并缩小20%
        stop_loss = current_price * (1 + stop_loss_pct)  # 做空止损在上方
        
        # 保守的止盈目标：-2%, -3.5%, -5%
        take_profit_1 = current_price * 0.98   # 下跌2%
        take_profit_2 = current_price * 0.965  # 下跌3.5%
        take_profit_3 = current_price * 0.95   # 下跌5%
        
        # 做空仓位信息
        return {
            'direction': 'SHORT',
            'entry_price': current_price,
            'position_size': position_info['position_size'],
            'position_value': position_info['position_value'],
            'position_percent': position_info['position_percent'],
            'stop_loss': stop_loss,  # 做空止损在上方
            'stop_loss_percent': stop_loss_pct,
            'take_profit_1': take_profit_1,  # 做空止盈在下方
            'take_profit_2': take_profit_2,
            'take_profit_3': take_profit_3,
            'max_loss': current_price * position_info['position_size'] * stop_loss_pct,
            'expected_profit': position_info['expected_profit'] * 0.6,
            'risk_reward_ratio': 2.0  # 保守的2:1
        }
    
    def _print_decision_report(self, result):
        """打印决策报告"""
        if not result:
            return
        
        print("\n")
        print("=" * 80)
        print("📊 综合决策报告")
        print("=" * 80)
        
        final = result['final_decision']
        ai = result['ai_decision']
        engine = result['engine_decision']
        
        # 当前市场状态
        print("\n【市场状态】")
        print(f"  当前价格: ${result['current_price']:,.2f}")
        
        # 显示动态权重信息
        if result.get('metadata', {}).get('market_state'):
            market_state = result['metadata']['market_state']
            state_name = {'bull': '牛市', 'bear': '熊市', 'sideways': '震荡'}.get(market_state, market_state)
            print(f"  市场状态: {state_name}")
            
            if result['metadata'].get('dynamic_weights'):
                weights = result['metadata']['dynamic_weights']
                print(f"  动态权重: ", end="")
                weight_items = [f"{k}={v:.1f}x" for k, v in list(weights.items())[:3]]
                print(", ".join(weight_items))
        
        if engine.get('signals'):
            signals = engine['signals']
            print(f"  新闻信号: {signals['news_score']:.0f}/100")
            print(f"  价格信号: {signals['price_score']:.0f}/100")
            print(f"  情绪信号: {signals['sentiment_score']:.0f}/100")
            print(f"  AI信号: {signals['ai_score']:.0f}/100")
            print(f"  综合评分: {signals['total_score']:.0f}/100")
            print(f"  信号一致性: {signals['consistency']*100:.0f}%")
        
        # AI决策层建议
        print("\n【AI决策层建议】")
        ai_dec = ai['decision']
        print(f"  建议操作: {ai_dec['action']}")
        print(f"  置信度: {ai_dec['confidence']:.0f}%")
        print(f"  理由: {ai_dec['reason']}")
        if ai.get('market_environment'):
            env = ai['market_environment']
            print(f"  市场环境: {env['description']} ({env['confidence']}%)")
        
        # 决策引擎验证
        print("\n【决策引擎验证】")
        eng_dec = engine['decision']
        print(f"  验证结果: {eng_dec['action']}")
        print(f"  置信度: {eng_dec['confidence']:.0f}%")
        print(f"  安全检查: {'✅ 通过' if engine['safety_checks']['passed'] else '❌ 未通过'}")
        
        # 最终决策
        print("\n【最终决策】")
        action_emoji = "🟢" if final['action'] == "LONG" else ("🔴" if final['action'] == "SHORT" else "⚪")
        print(f"  {action_emoji} 操作: {final['action']}")
        print(f"  置信度: {final['confidence']:.0f}%")
        print(f"  原因: {final['reason']}")
        
        # 仓位信息
        if final.get('position'):
            pos = final['position']
            print(f"\n【仓位管理】")
            print(f"  方向: {pos['direction']}")
            print(f"  入场价: ${pos['entry_price']:,.2f}")
            print(f"  仓位: {pos['position_size']:.8f} (${pos['position_value']:,.2f})")
            print(f"  止损: ${pos['stop_loss']:,.2f}")
            print(f"  止盈1: ${pos['take_profit_1']:,.2f}")
            print(f"  止盈2: ${pos['take_profit_2']:,.2f}")
            print(f"  止盈3: ${pos['take_profit_3']:,.2f}")
            print(f"  风险收益比: {pos['risk_reward_ratio']:.2f}:1")
        
        print("\n" + "=" * 80)
        print(f"⏱️ 分析耗时: {result.get('elapsed_time', 0):.2f}秒")
        print("=" * 80)


def main():
    """主函数"""
    print("\n")
    print("=" * 80)
    print("🌐 多币种交易决策系统")
    print("=" * 80)
    print("分析币种: BTC, ETH")
    print("分析周期: 12小时")
    print("策略: 双向交易（做多/做空）")
    print("=" * 80)
    
    # 创建决策系统
    system = RealTradingDecisionSystem(
        account_balance=10000,
        risk_percent=0.015
    )
    
    # 分析结果汇总
    results = {}
    
    # 1. 分析BTC
    print("\n" + "🔷" * 40)
    print("【1/2】分析 BTC (比特币)")
    print("🔷" * 40)
    btc_result = system.analyze_and_decide(symbol="BTCUSDT")
    if btc_result:
        results['BTC'] = btc_result
    
    # 2. 分析ETH
    print("\n" + "🔷" * 40)
    print("【2/2】分析 ETH (以太坊)")
    print("🔷" * 40)
    eth_result = system.analyze_and_decide(symbol="ETHUSDT")
    if eth_result:
        results['ETH'] = eth_result
    
    # 3. 综合对比
    print("\n")
    print("=" * 80)
    print("📊 综合对比分析")
    print("=" * 80)
    
    if 'BTC' in results and 'ETH' in results:
        btc_final = results['BTC']['final_decision']
        eth_final = results['ETH']['final_decision']
        
        print("\n【BTC vs ETH 对比】")
        print(f"\nBTC:")
        print(f"  操作: {btc_final['action']:6s}  置信度: {btc_final['confidence']:.0f}%")
        print(f"  价格: ${results['BTC']['current_price']:,.2f}")
        
        print(f"\nETH:")
        print(f"  操作: {eth_final['action']:6s}  置信度: {eth_final['confidence']:.0f}%")
        print(f"  价格: ${results['ETH']['current_price']:,.2f}")
        
        # 推荐决策
        print("\n【交易建议】")
        
        # 优先级：操作有效性 > 置信度
        btc_priority = 0
        eth_priority = 0
        
        if btc_final['action'] in ['LONG', 'SHORT']:
            btc_priority = btc_final['confidence']
        if eth_final['action'] in ['LONG', 'SHORT']:
            eth_priority = eth_final['confidence']
        
        if btc_priority > 0 or eth_priority > 0:
            if btc_priority > eth_priority:
                print(f"✅ 建议优先: BTC {btc_final['action']}")
                print(f"   理由: 置信度更高 ({btc_priority:.0f}% vs {eth_priority:.0f}%)")
            elif eth_priority > btc_priority:
                print(f"✅ 建议优先: ETH {eth_final['action']}")
                print(f"   理由: 置信度更高 ({eth_priority:.0f}% vs {btc_priority:.0f}%)")
            else:
                print(f"⚖️ BTC和ETH机会相当，可同时布局")
        else:
            print("⚠️ 两个币种都建议观望，等待更好的入场时机")
        
        print("\n" + "=" * 80)
        print("✅ 所有分析完成！")
        print("=" * 80)
    else:
        print("\n❌ 部分分析失败")


if __name__ == "__main__":
    main()
