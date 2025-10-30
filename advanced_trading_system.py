#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级交易决策系统
支持：杠杆交易、自定义参数、使用所有组件
"""

import sys
import os
import logging
from datetime import datetime
import pandas as pd
import argparse
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 导入所有组件
from utils.gas_monitor import GasFeeMonitor
from utils.data_fetcher import BinanceDataFetcher
from utils.multi_source_fetcher import MultiSourceDataFetcher
from utils.financial_news import FinancialNewsAggregator
from utils.news_processor import NewsProcessor
from utils.sentiment_analyzer import MarketSentimentAnalyzer
from utils.data_integrator import DataIntegrator
from utils.decision_engine import DecisionEngine
from ai_decision_layer import AIDecisionLayer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedTradingSystem:
    """高级交易决策系统 - 支持杠杆和自定义参数"""
    
    def __init__(self, capital_usdt=1000, leverage=1, risk_percent=2.0):
        """
        初始化系统
        
        Args:
            capital_usdt: 投入资金（U）
            leverage: 杠杆倍数（1-125）
            risk_percent: 风险百分比（建议1-3%）
        """
        logger.info("=" * 80)
        logger.info("🚀 高级交易决策系统")
        logger.info("=" * 80)
        
        self.capital_usdt = capital_usdt
        self.leverage = leverage
        self.risk_percent = risk_percent
        
        # 计算有效资金（考虑杠杆）
        self.effective_capital = capital_usdt * leverage
        
        logger.info(f"   投入资金: {capital_usdt} USDT")
        logger.info(f"   杠杆倍数: {leverage}x")
        logger.info(f"   有效资金: {self.effective_capital} USDT")
        logger.info(f"   风险比例: {risk_percent}%")
        
        # 获取API密钥（兼容两种格式）
        newsapi_key = os.getenv('NEWSAPI_KEY') or os.getenv('NEWS_API_KEY') or ''
        
        # 初始化所有组件
        self.gas_monitor = GasFeeMonitor()
        self.data_fetcher = BinanceDataFetcher()
        try:
            self.multi_source_fetcher = MultiSourceDataFetcher()
        except:
            self.multi_source_fetcher = None
            logger.warning("   ⚠️ 多数据源获取器初始化失败")
        
        self.news_api = FinancialNewsAggregator(newsapi_key=newsapi_key)
        self.news_processor = NewsProcessor()
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        self.data_integrator = DataIntegrator()
        
        # 决策组件
        self.decision_engine = DecisionEngine(
            account_balance=self.effective_capital,
            risk_percent=risk_percent / 100
        )
        self.ai_decision_layer = AIDecisionLayer(
            account_balance=self.effective_capital,
            risk_percent=risk_percent / 100
        )
        
        logger.info("✅ 所有组件初始化完成")
    
    def calculate_position_with_leverage(self, entry_price, stop_loss_percent):
        """
        计算杠杆仓位
        
        公式：
        - 风险金额 = 本金 × 风险比例
        - 仓位大小 = 风险金额 / 止损距离
        - 保证金 = 仓位价值 / 杠杆
        """
        # 单次风险金额（基于本金）
        risk_amount = self.capital_usdt * (self.risk_percent / 100)
        
        # 止损距离
        stop_loss_distance = entry_price * (stop_loss_percent / 100)
        
        # 仓位大小（币数）
        position_size = risk_amount / stop_loss_distance
        
        # 仓位价值
        position_value = position_size * entry_price
        
        # 保证金（实际占用的本金）
        margin_required = position_value / self.leverage
        
        # 仓位占比
        position_percent = (margin_required / self.capital_usdt) * 100
        
        return {
            'position_size': position_size,
            'position_value': position_value,
            'margin_required': margin_required,
            'position_percent': position_percent,
            'max_loss': risk_amount,
            'leverage': self.leverage
        }
    
    def calculate_take_profit_levels(self, entry_price, direction, stop_loss_percent):
        """计算止盈位置（风险收益比 2:1, 3:1, 4:1）"""
        risk_reward_ratios = [2, 3, 4]
        take_profits = {}
        
        for i, ratio in enumerate(risk_reward_ratios, 1):
            tp_percent = stop_loss_percent * ratio
            
            if direction == "LONG":
                tp_price = entry_price * (1 + tp_percent / 100)
            else:  # SHORT
                tp_price = entry_price * (1 - tp_percent / 100)
            
            take_profits[f'take_profit_{i}'] = {
                'price': tp_price,
                'percent': tp_percent,
                'ratio': f'{ratio}:1',
                'close_percent': [50, 30, 20][i-1]
            }
        
        return take_profits
    
    def fetch_market_data(self, symbol="BTCUSDT", hours=12):
        """获取市场数据（使用所有组件）"""
        logger.info("\n" + "=" * 80)
        logger.info(f"📊 获取 {symbol} 市场数据（{hours}小时）")
        logger.info("=" * 80)
        
        all_data = {}
        
        # 1. Gas费用
        logger.info("\n[1/5] 获取Gas费用...")
        try:
            gas_data = self.gas_monitor.get_all_fees()
            if gas_data:
                all_data['gas_data'] = {
                    'ETH': self.gas_monitor.should_trade_eth(),
                    'BTC': self.gas_monitor.should_trade_btc(),
                    'details': gas_data
                }
                logger.info(f"   ✓ 完成")
        except Exception as e:
            logger.error(f"   ✗ 失败: {e}")
            all_data['gas_data'] = None
        
        # 2. K线数据
        logger.info(f"\n[2/5] 获取K线数据...")
        try:
            kline_df = self.data_fetcher.fetch_klines(symbol=symbol, interval="1h", limit=100)
            all_data['kline_df'] = kline_df
            all_data['analysis_hours'] = hours
            
            if kline_df is not None and not kline_df.empty:
                current_price = kline_df.iloc[-1]['close']
                logger.info(f"   ✓ 当前价格: ${current_price:,.2f}")
        except Exception as e:
            logger.error(f"   ✗ 失败: {e}")
            all_data['kline_df'] = None
        
        # 3. 新闻数据（增强分析）
        logger.info("\n[3/5] 获取新闻（增强分析）...")
        try:
            news_list = self.news_api.get_all_news(
                crypto_limit=15,
                macro_limit=10,
                include_chinese=True
            )
            all_data['news_list'] = news_list
            
            if news_list:
                news_sentiment = self.news_api.analyze_sentiment(news_list)
                
                # 使用正确的方法名
                try:
                    processed_news = self.news_processor.process_news_list(news_list, filter_irrelevant=True)
                except Exception as e:
                    logger.warning(f"   ⚠️ 新闻深度处理失败: {e}")
                    processed_news = None
                
                all_data['news_sentiment'] = news_sentiment
                all_data['processed_news'] = processed_news
                
                logger.info(f"   ✓ 新闻: {len(news_list)}条")
                logger.info(f"   ✓ 情绪: {news_sentiment.get('sentiment', 'N/A')}")
        except Exception as e:
            logger.error(f"   ✗ 失败: {e}")
            all_data['news_list'] = []
            all_data['news_sentiment'] = None
        
        # 4. 市场情绪
        logger.info("\n[4/5] 分析市场情绪...")
        try:
            market_sentiment = self.sentiment_analyzer.get_comprehensive_sentiment(
                symbol=symbol.replace('USDT', '')
            )
            all_data['market_sentiment'] = market_sentiment
            logger.info(f"   ✓ 完成")
        except Exception as e:
            logger.error(f"   ✗ 失败: {e}")
            all_data['market_sentiment'] = None
        
        # 5. AI预测
        logger.info("\n[5/5] 生成AI预测...")
        ai_predictions = self._generate_ai_predictions(
            news_sentiment=all_data.get('news_sentiment'),
            market_sentiment=all_data.get('market_sentiment'),
            kline_df=all_data.get('kline_df')
        )
        all_data['ai_predictions'] = ai_predictions
        logger.info(f"   ✓ 完成")
        
        return all_data
    
    def _generate_ai_predictions(self, news_sentiment, market_sentiment, kline_df):
        """生成AI预测"""
        direction = 'up'
        confidence = 60
        
        bullish_signals = 0
        bearish_signals = 0
        
        if news_sentiment:
            sent = news_sentiment.get('sentiment', 'neutral')
            if sent == 'bullish':
                bullish_signals += 2
            elif sent == 'bearish':
                bearish_signals += 2
        
        if market_sentiment:
            sent = market_sentiment.get('overall_sentiment', 'neutral')
            if sent == 'bullish':
                bullish_signals += 2
            elif sent == 'bearish':
                bearish_signals += 2
        
        if kline_df is not None and not kline_df.empty and len(kline_df) >= 12:
            recent = kline_df.tail(12)
            price_change = ((recent.iloc[-1]['close'] - recent.iloc[0]['close']) / recent.iloc[0]['close']) * 100
            if price_change > 1.5:
                bullish_signals += 1
            elif price_change < -1.5:
                bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            direction = 'up'
            confidence = min(90, 60 + (bullish_signals - bearish_signals) * 10)
        elif bearish_signals > bullish_signals:
            direction = 'down'
            confidence = min(90, 60 + (bearish_signals - bullish_signals) * 10)
        
        return pd.DataFrame({
            'timestamp': [datetime.now()],
            'grok_direction': [direction],
            'grok_confidence': [confidence],
            'gemini_direction': [direction],
            'gemini_confidence': [max(50, confidence - 5)],
            'deepseek_direction': [direction],
            'deepseek_confidence': [min(90, confidence + 5)]
        })
    
    def analyze_with_leverage(self, symbol="BTCUSDT", stop_loss_pct=2.0):
        """执行杠杆交易分析"""
        start_time = datetime.now()
        
        print("\n")
        print("=" * 80)
        print("🎯 杠杆交易决策分析")
        print("=" * 80)
        print(f"交易对: {symbol}")
        print(f"杠杆: {self.leverage}x")
        print(f"本金: {self.capital_usdt} USDT")
        print(f"止损: {stop_loss_pct}%")
        print("=" * 80)
        
        try:
            # 1. 获取市场数据
            market_data = self.fetch_market_data(symbol, hours=12)
            
            # 2. 整合特征
            logger.info("\n" + "=" * 80)
            logger.info("🔄 整合特征向量")
            logger.info("=" * 80)
            
            integrated_data = self.data_integrator.integrate_all(
                gas_data=market_data.get('gas_data'),
                kline_df=market_data.get('kline_df'),
                news_sentiment=market_data.get('news_sentiment'),
                market_sentiment=market_data.get('market_sentiment'),
                ai_predictions=market_data.get('ai_predictions'),
                hours=12
            )
            
            features = integrated_data['features']
            current_price = features[4] if len(features) > 4 else 0
            
            # 3. AI决策
            logger.info("\n" + "=" * 80)
            logger.info("🤖 AI决策分析")
            logger.info("=" * 80)
            
            metadata = {
                'current_price': current_price,
                'avg_volume': features[6] if len(features) > 6 else 0
            }
            
            ai_decision = self.ai_decision_layer.make_final_decision(
                features=features,
                metadata=metadata,
                use_aggregation=False
            )
            
            # 4. 决策引擎验证
            logger.info("\n" + "=" * 80)
            logger.info("🎯 决策引擎验证")
            logger.info("=" * 80)
            
            engine_decision = self.decision_engine.analyze(
                features=features,
                news_data=market_data.get('news_list', [])
            )
            
            # 5. 计算杠杆仓位
            final_decision = self._merge_decisions_with_leverage(
                ai_decision, 
                engine_decision, 
                current_price,
                stop_loss_pct
            )
            
            # 打印报告
            self._print_leverage_report(final_decision, market_data)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            final_decision['elapsed_time'] = elapsed
            
            return final_decision
            
        except Exception as e:
            logger.error(f"\n❌ 分析出错: {e}", exc_info=True)
            return None
    
    def _merge_decisions_with_leverage(self, ai_decision, engine_decision, current_price, stop_loss_pct):
        """综合决策并计算杠杆仓位"""
        ai_action = ai_decision['decision']['action']
        ai_confidence = ai_decision['decision']['confidence']
        
        engine_action = engine_decision['decision']['action']
        engine_signals = engine_decision.get('signals', {})
        
        safety_passed = engine_decision.get('safety_checks', {}).get('passed', False)
        
        final_action = "HOLD"
        final_confidence = 0
        final_reason = ""
        detailed_reason = ""  # 新增：详细原因
        position_info = None
        
        # 生成市场诊断报告
        market_diagnosis = self._generate_market_diagnosis(engine_signals, ai_decision)
        
        if not safety_passed:
            final_action = "HOLD"
            final_confidence = 0
            final_reason = f"❌ 安全检查未通过"
        else:
            # 做多
            if ai_action == "LONG" and engine_action in ["BUY", "HOLD"]:
                # 调整为63分（更合理，给1-2分的容差）
                if engine_signals.get('total_score', 0) >= 63:
                    final_action = "LONG"
                    final_confidence = (ai_confidence + engine_signals['total_score']) / 2
                    final_reason = f"✅ AI建议做多 + 引擎支持（{self.leverage}x杠杆）"
                    position_info = self._calculate_leverage_position(
                        current_price, "LONG", stop_loss_pct
                    )
                else:
                    final_action = "HOLD"
                    final_confidence = 50
                    final_reason = f"⚠️ 评分不足（{engine_signals['total_score']:.0f}/63）"
            
            # 做空
            elif ai_action == "SHORT" and engine_action in ["SELL", "HOLD"]:
                # 调整为57分（更合理，给1-2分的容差）
                if engine_signals.get('total_score', 0) <= 57:
                    final_action = "SHORT"
                    final_confidence = (ai_confidence + (100 - engine_signals['total_score'])) / 2
                    final_reason = f"✅ AI建议做空 + 引擎支持（{self.leverage}x杠杆）"
                    position_info = self._calculate_leverage_position(
                        current_price, "SHORT", stop_loss_pct
                    )
                else:
                    final_action = "HOLD"
                    final_confidence = 50
                    final_reason = f"⚠️ 评分不足（{engine_signals['total_score']:.0f}/57）"
            else:
                final_action = "HOLD"
                final_confidence = 50
                final_reason = "⚠️ 信号不一致"
        
        return {
            'final_decision': {
                'action': final_action,
                'confidence': final_confidence,
                'reason': final_reason,
                'position': position_info
            },
            'market_diagnosis': market_diagnosis,  # 新增：市场诊断
            'ai_decision': ai_decision,
            'engine_decision': engine_decision,
            'current_price': current_price
        }
    
    def _generate_market_diagnosis(self, engine_signals, ai_decision):
        """
        生成详细的市场诊断报告
        
        分析当前市场状态，给出导致决策的具体原因
        """
        diagnosis = {
            'overall_state': '',
            'key_factors': [],
            'concerns': [],
            'opportunities': []
        }
        
        if not engine_signals:
            return diagnosis
        
        # 获取各维度评分
        total_score = engine_signals.get('total_score', 50)
        news_score = engine_signals.get('news_score', 50)
        price_score = engine_signals.get('price_score', 50)
        sentiment_score = engine_signals.get('sentiment_score', 50)
        ai_score = engine_signals.get('ai_score', 50)
        consistency = engine_signals.get('consistency', 0.5)
        
        # 判断整体市场状态
        if total_score >= 70:
            diagnosis['overall_state'] = "🟢 市场整体强势看涨"
        elif total_score >= 55:
            diagnosis['overall_state'] = "🟡 市场略微偏多，但信号不够强"
        elif total_score >= 45:
            diagnosis['overall_state'] = "⚪ 市场中性震荡，方向不明"
        elif total_score >= 30:
            diagnosis['overall_state'] = "🟠 市场略微偏空，但信号不够强"
        else:
            diagnosis['overall_state'] = "🔴 市场整体弱势看跌"
        
        # 分析关键因素
        scores = [
            ('新闻面', news_score, 30),
            ('价格面', price_score, 25),
            ('情绪面', sentiment_score, 25),
            ('AI信号', ai_score, 20)
        ]
        
        # 找出最强和最弱的信号
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        strongest = sorted_scores[0]
        weakest = sorted_scores[-1]
        
        # 关键驱动因素
        if strongest[1] >= 70:
            diagnosis['key_factors'].append(f"✅ {strongest[0]}强劲 ({strongest[1]:.0f}分)，成为主要驱动力")
        elif strongest[1] >= 55:
            diagnosis['key_factors'].append(f"🟢 {strongest[0]}偏多 ({strongest[1]:.0f}分)")
        
        if weakest[1] <= 30:
            diagnosis['key_factors'].append(f"❌ {weakest[0]}疲软 ({weakest[1]:.0f}分)，拖累整体表现")
        elif weakest[1] <= 45:
            diagnosis['key_factors'].append(f"🔴 {weakest[0]}偏空 ({weakest[1]:.0f}分)")
        
        # 具体分析各维度
        # 1. 新闻分析
        if news_score >= 70:
            diagnosis['opportunities'].append("📰 新闻面利好，市场情绪积极")
        elif news_score <= 30:
            diagnosis['concerns'].append("📰 新闻面利空，市场情绪悲观")
        elif news_score >= 45 and news_score <= 55:
            diagnosis['key_factors'].append("📰 新闻面平淡，缺乏催化剂")
        
        # 2. 价格分析
        if price_score >= 70:
            diagnosis['opportunities'].append("📈 价格走势强劲，技术面支持上涨")
        elif price_score <= 30:
            diagnosis['concerns'].append("📉 价格走势疲软，技术面支持下跌")
        elif price_score >= 45 and price_score <= 55:
            diagnosis['key_factors'].append("📊 价格横盘整理，等待方向选择")
        
        # 3. 情绪分析
        if sentiment_score >= 70:
            diagnosis['opportunities'].append("😊 市场情绪高涨，投资者信心充足")
        elif sentiment_score <= 30:
            diagnosis['concerns'].append("😰 市场情绪低迷，投资者恐慌")
        elif sentiment_score >= 45 and sentiment_score <= 55:
            diagnosis['key_factors'].append("😐 市场情绪中性，观望氛围浓厚")
        
        # 4. AI信号分析
        ai_action = ai_decision['decision']['action']
        ai_conf = ai_decision['decision']['confidence']
        
        if ai_conf >= 80:
            if ai_action == "LONG":
                diagnosis['opportunities'].append(f"🤖 AI强烈看涨 ({ai_conf:.0f}%置信度)")
            elif ai_action == "SHORT":
                diagnosis['concerns'].append(f"🤖 AI强烈看跌 ({ai_conf:.0f}%置信度)")
        elif ai_conf >= 60:
            if ai_action == "LONG":
                diagnosis['key_factors'].append(f"🤖 AI偏向看涨 ({ai_conf:.0f}%置信度)")
            elif ai_action == "SHORT":
                diagnosis['key_factors'].append(f"🤖 AI偏向看跌 ({ai_conf:.0f}%置信度)")
        
        # 5. 信号一致性分析
        if consistency >= 0.8:
            diagnosis['key_factors'].append(f"✅ 各维度信号高度一致 ({consistency*100:.0f}%)")
        elif consistency <= 0.5:
            diagnosis['concerns'].append(f"⚠️ 各维度信号分歧较大 ({consistency*100:.0f}%)，需谨慎")
        
        # 6. 市场环境分析
        if 'market_environment' in ai_decision:
            env = ai_decision['market_environment']
            env_type = env.get('type', 'unknown')
            env_desc = env.get('description', '')
            
            if env_type == 'strong_trend':
                diagnosis['key_factors'].append(f"📊 市场环境: {env_desc}")
            elif env_type == 'ranging':
                diagnosis['key_factors'].append(f"📊 市场环境: {env_desc}，不适合趋势交易")
        
        return diagnosis
    
    def _calculate_leverage_position(self, current_price, direction, stop_loss_pct):
        """计算杠杆仓位（完整信息）"""
        # 计算基础仓位
        base_position = self.calculate_position_with_leverage(current_price, stop_loss_pct)
        
        # 计算止损价
        if direction == "LONG":
            stop_loss = current_price * (1 - stop_loss_pct / 100)
        else:  # SHORT
            stop_loss = current_price * (1 + stop_loss_pct / 100)
        
        # 计算止盈
        take_profits = self.calculate_take_profit_levels(current_price, direction, stop_loss_pct)
        
        return {
            'direction': direction,
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'stop_loss_percent': stop_loss_pct,
            **base_position,
            **take_profits
        }
    
    def _print_leverage_report(self, result, market_data):
        """打印杠杆交易报告"""
        if not result:
            return
        
        print("\n")
        print("=" * 80)
        print("📊 杠杆交易决策报告")
        print("=" * 80)
        
        final = result['final_decision']
        ai = result['ai_decision']
        engine = result['engine_decision']
        diagnosis = result.get('market_diagnosis', {})
        
        # 市场诊断（新增）
        if diagnosis:
            print("\n【市场诊断】")
            if diagnosis.get('overall_state'):
                print(f"  {diagnosis['overall_state']}")
            
            if diagnosis.get('key_factors'):
                print("\n  关键因素：")
                for factor in diagnosis['key_factors']:
                    print(f"    • {factor}")
            
            if diagnosis.get('opportunities'):
                print("\n  机会：")
                for opp in diagnosis['opportunities']:
                    print(f"    ✅ {opp}")
            
            if diagnosis.get('concerns'):
                print("\n  风险：")
                for concern in diagnosis['concerns']:
                    print(f"    ⚠️ {concern}")
        
        # 市场状态
        print("\n【市场数据】")
        print(f"  当前价格: ${result['current_price']:,.2f}")
        if engine.get('signals'):
            signals = engine['signals']
            print(f"  综合评分: {signals['total_score']:.0f}/100")
            print(f"  信号一致性: {signals['consistency']*100:.0f}%")
            print(f"  各维度评分:")
            print(f"    📰 新闻: {signals.get('news_score', 0):.0f}/100")
            print(f"    📈 价格: {signals.get('price_score', 0):.0f}/100")
            print(f"    😊 情绪: {signals.get('sentiment_score', 0):.0f}/100")
            print(f"    🤖 AI: {signals.get('ai_score', 0):.0f}/100")
        
        # AI建议
        print("\n【AI决策层】")
        ai_dec = ai['decision']
        print(f"  建议: {ai_dec['action']}")
        print(f"  置信度: {ai_dec['confidence']:.0f}%")
        
        # 引擎验证
        print("\n【决策引擎】")
        eng_dec = engine['decision']
        print(f"  验证: {eng_dec['action']}")
        print(f"  安全检查: {'✅ 通过' if engine['safety_checks']['passed'] else '❌ 未通过'}")
        
        # 最终决策
        print("\n【最终决策】")
        action_emoji = "🟢" if final['action'] == "LONG" else ("🔴" if final['action'] == "SHORT" else "⚪")
        print(f"  {action_emoji} 操作: {final['action']}")
        print(f"  置信度: {final['confidence']:.0f}%")
        print(f"  原因: {final['reason']}")
        
        # 杠杆仓位
        if final.get('position'):
            pos = final['position']
            print(f"\n【杠杆仓位管理】")
            print(f"  🎯 杠杆: {self.leverage}x")
            print(f"  💰 本金: {self.capital_usdt} USDT")
            print(f"  📊 保证金: {pos['margin_required']:.2f} USDT ({pos['position_percent']:.1f}%)")
            print(f"  📈 仓位价值: {pos['position_value']:.2f} USDT")
            print(f"  🪙 币数: {pos['position_size']:.8f}")
            print(f"\n  🛑 止损: ${pos['stop_loss']:,.2f} (-{pos['stop_loss_percent']:.1f}%)")
            print(f"  💀 最大损失: {pos['max_loss']:.2f} USDT ({pos['max_loss']/self.capital_usdt*100:.2f}%本金)")
            
            if 'take_profit_1' in pos:
                print(f"\n  🎯 止盈计划:")
                for i in range(1, 4):
                    tp = pos[f'take_profit_{i}']
                    print(f"    TP{i}: ${tp['price']:,.2f} ({tp['ratio']}) → 平{tp['close_percent']}%")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='高级杠杆交易决策系统')
    parser.add_argument('--capital', type=float, default=1000, help='投入资金（USDT）')
    parser.add_argument('--leverage', type=int, default=10, help='杠杆倍数（1-125）')
    parser.add_argument('--risk', type=float, default=2.0, help='风险比例（%）')
    parser.add_argument('--stop-loss', type=float, default=2.0, help='止损比例（%）')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='交易对')
    
    args = parser.parse_args()
    
    print("\n")
    print("=" * 80)
    print("🚀 高级杠杆交易决策系统")
    print("=" * 80)
    print(f"版本: v2.0 增强版")
    print(f"特性: 杠杆交易、自定义参数、全组件集成")
    print("=" * 80)
    
    # 创建系统
    system = AdvancedTradingSystem(
        capital_usdt=args.capital,
        leverage=args.leverage,
        risk_percent=args.risk
    )
    
    # 执行分析
    result = system.analyze_with_leverage(
        symbol=args.symbol,
        stop_loss_pct=args.stop_loss
    )
    
    if result:
        print("\n✅ 分析完成！")
    else:
        print("\n❌ 分析失败！")


if __name__ == "__main__":
    main()
