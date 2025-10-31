"""
数据整合模块
将所有数据源整合为AI友好的结构化格式
"""

import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class DataIntegrator:
    """数据整合器 - 将多源数据转换为AI可理解的向量格式"""
    
    def __init__(self):
        self.feature_names = []
        self.feature_vector = []
    
    def integrate_gas_data(self, gas_data):
        """
        整合Gas费用数据
        
        Args:
            gas_data: Gas监控数据，可能是dict或bool
        
        Returns:
            特征向量 [eth_gas, btc_fee, eth_suitable, btc_suitable]
        """
        features = []
        names = []
        
        # 处理gas_data可能是check_trading_conditions返回的格式
        if gas_data and isinstance(gas_data, dict):
            # 检查是否有details键（来自check_trading_conditions）
            if "details" in gas_data:
                eth_data = gas_data["details"].get("ETH")
                btc_data = gas_data["details"].get("BTC")
                eth_suitable = 1 if gas_data.get("ETH", False) else 0
                btc_suitable = 1 if gas_data.get("BTC", False) else 0
            else:
                # 直接包含ETH和BTC数据
                eth_data = gas_data.get("ETH")
                btc_data = gas_data.get("BTC")
                eth_suitable = 1 if eth_data else 0
                btc_suitable = 1 if btc_data else 0
            
            # 提取ETH Gas
            if eth_data and isinstance(eth_data, dict):
                eth_gas = eth_data.get("latest_gas", eth_data.get("propose_gas", 0))
            else:
                eth_gas = 0
            
            # 提取BTC Fee
            if btc_data and isinstance(btc_data, dict):
                btc_fee = btc_data.get("half_hour_fee", btc_data.get("fastest_fee", 0))
            else:
                btc_fee = 0
        else:
            eth_gas = 0
            btc_fee = 0
            eth_suitable = 0
            btc_suitable = 0
        
        features.extend([eth_gas, btc_fee, eth_suitable, btc_suitable])
        names.extend(['eth_gas_gwei', 'btc_fee_sat', 'eth_tradeable', 'btc_tradeable'])
        
        return features, names
    
    def integrate_kline_data(self, kline_df, hours=12):
        """
        整合K线数据
        
        Args:
            kline_df: K线DataFrame
            hours: 分析的小时数（默认12小时）
        
        Returns:
            特征向量 [current_price, price_change_pct, volume, volatility, trend]
        """
        features = []
        names = []
        
        if kline_df is not None and not kline_df.empty:
            # 当前价格
            current_price = float(kline_df.iloc[-1]['close'])
            
            # 使用指定小时数的价格变化
            if len(kline_df) >= hours:
                recent_data = kline_df.tail(hours)
                price_change_pct = (recent_data.iloc[-1]['close'] - recent_data.iloc[0]['close']) / recent_data.iloc[0]['close'] * 100
            else:
                price_change_pct = (kline_df.iloc[-1]['close'] - kline_df.iloc[0]['close']) / kline_df.iloc[0]['close'] * 100
            
            # 成交量（最近10条平均）
            avg_volume = float(kline_df['volume'].tail(10).mean())
            
            # 波动率（基于指定小时数）
            if len(kline_df) >= hours:
                volatility = float(recent_data['close'].std() / recent_data['close'].mean())
            else:
                volatility = float(kline_df['close'].std() / kline_df['close'].mean())
            
            # 趋势 (1=上涨, 0=平稳, -1=下跌) - 基于指定小时数
            trend = 1 if price_change_pct > 1 else (-1 if price_change_pct < -1 else 0)
            
            # 最高最低价（指定小时数）
            if len(kline_df) >= hours:
                high_price = float(recent_data['high'].max())
                low_price = float(recent_data['low'].min())
            else:
                high_price = float(kline_df['high'].max())
                low_price = float(kline_df['low'].min())
            
            price_range_pct = (high_price - low_price) / low_price * 100
            
            features.extend([
                current_price,
                price_change_pct,
                avg_volume,
                volatility,
                trend,
                high_price,
                low_price,
                price_range_pct
            ])
            
            names.extend([
                'current_price',
                'price_change_pct',
                'avg_volume',
                'volatility',
                'trend',
                'high_price',
                'low_price',
                'price_range_pct'
            ])
        else:
            features.extend([0] * 8)
            names.extend([
                'current_price',
                'price_change_pct',
                'avg_volume',
                'volatility',
                'trend',
                'high_price',
                'low_price',
                'price_range_pct'
            ])
        
        return features, names
    
    def integrate_news_sentiment(self, news_sentiment):
        """
        整合新闻情绪数据
        
        Args:
            news_sentiment: 新闻情绪分析结果
        
        Returns:
            特征向量 [sentiment_score, positive_ratio, negative_ratio, total_news]
        """
        features = []
        names = []
        
        if news_sentiment:
            score = news_sentiment.get('score', 0)
            total = news_sentiment.get('total_news', 0)
            positive = news_sentiment.get('positive_count', 0)
            negative = news_sentiment.get('negative_count', 0)
            
            # 转换为比例
            pos_ratio = positive / total if total > 0 else 0
            neg_ratio = negative / total if total > 0 else 0
            
            # 情绪标签 (1=看涨, 0=中性, -1=看跌)
            sentiment_label = 1 if news_sentiment.get('sentiment') == 'bullish' else (-1 if news_sentiment.get('sentiment') == 'bearish' else 0)
            
            features.extend([score, pos_ratio, neg_ratio, total, sentiment_label])
            names.extend(['news_score', 'news_pos_ratio', 'news_neg_ratio', 'news_count', 'news_sentiment'])
        else:
            features.extend([0, 0, 0, 0, 0])
            names.extend(['news_score', 'news_pos_ratio', 'news_neg_ratio', 'news_count', 'news_sentiment'])
        
        return features, names
    
    def integrate_market_sentiment(self, market_sentiment):
        """
        整合市场情绪数据
        
        Args:
            market_sentiment: 市场情绪分析结果
        
        Returns:
            特征向量 [sentiment_score, confidence, fear_greed_index, sentiment_label]
        """
        features = []
        names = []
        
        if market_sentiment:
            weighted_score = market_sentiment.get('weighted_score', 0)
            confidence = market_sentiment.get('confidence', 0)
            
            # 提取恐惧贪婪指数
            fear_greed = 50  # 默认中性
            for source in market_sentiment.get('sources', []):
                if source.get('source') == 'fear_greed':
                    # 从-100~100转换回0~100
                    fear_greed = (source.get('score', 0) + 100) / 2
                    break
            
            # 情绪标签 (1=看涨, 0=中性, -1=看跌)
            sentiment_label = 1 if market_sentiment.get('overall_sentiment') == 'bullish' else (-1 if market_sentiment.get('overall_sentiment') == 'bearish' else 0)
            
            features.extend([weighted_score, confidence, fear_greed, sentiment_label])
            names.extend(['market_sentiment_score', 'market_confidence', 'fear_greed_index', 'market_sentiment_label'])
        else:
            features.extend([0, 0, 50, 0])
            names.extend(['market_sentiment_score', 'market_confidence', 'fear_greed_index', 'market_sentiment_label'])
        
        return features, names
    
    def integrate_ai_predictions(self, predictions_df):
        """
        整合AI预测数据
        
        Args:
            predictions_df: AI预测DataFrame
        
        Returns:
            特征向量 [avg_confidence, up_count, down_count, consensus_direction]
        """
        features = []
        names = []
        
        if predictions_df is not None and not predictions_df.empty:
            # 统计各模型预测方向
            up_count = 0
            down_count = 0
            total_confidence = 0
            count = 0
            
            for _, pred in predictions_df.iterrows():
                for model in ['grok', 'gemini', 'deepseek']:
                    direction = pred.get(f'{model}_direction')
                    confidence = pred.get(f'{model}_confidence', 0)
                    
                    if direction == 'up':
                        up_count += 1
                    elif direction == 'down':
                        down_count += 1
                    
                    if confidence > 0:
                        total_confidence += confidence
                        count += 1
            
            avg_confidence = total_confidence / count if count > 0 else 0
            total = up_count + down_count
            
            # 一致性比例
            agreement_ratio = max(up_count, down_count) / total if total > 0 else 0
            
            # 共识方向 (1=看涨, 0=不明确, -1=看跌)
            consensus = 1 if up_count > down_count * 1.5 else (-1 if down_count > up_count * 1.5 else 0)
            
            features.extend([avg_confidence, up_count, down_count, agreement_ratio, consensus])
            names.extend(['ai_avg_confidence', 'ai_up_count', 'ai_down_count', 'ai_agreement_ratio', 'ai_consensus'])
        else:
            features.extend([0, 0, 0, 0, 0])
            names.extend(['ai_avg_confidence', 'ai_up_count', 'ai_down_count', 'ai_agreement_ratio', 'ai_consensus'])
        
        return features, names
    
    def integrate_all(self, gas_data=None, kline_df=None, news_sentiment=None, 
                     market_sentiment=None, ai_predictions=None, hours=12,
                     orderbook_data=None, macro_data=None, futures_data=None,
                     technical_indicators=None, multi_timeframe=None, support_resistance=None):
        """
        整合所有数据（35维）
        
        Args:
            hours: 分析的小时数
            orderbook_data: 订单簿数据（新增）
            macro_data: 宏观指标（新增）
            futures_data: 期货数据（新增）
        """
        all_features = []
        all_names = []
        
        # 1. Gas数据
        gas_features, gas_names = self.integrate_gas_data(gas_data)
        all_features.extend(gas_features)
        all_names.extend(gas_names)
        
        # 2. K线数据
        kline_features, kline_names = self.integrate_kline_data(kline_df, hours=hours)
        all_features.extend(kline_features)
        all_names.extend(kline_names)
        
        # 3. 新闻情绪
        news_features, news_names = self.integrate_news_sentiment(news_sentiment)
        all_features.extend(news_features)
        all_names.extend(news_names)
        
        # 4. 市场情绪
        market_features, market_names = self.integrate_market_sentiment(market_sentiment)
        all_features.extend(market_features)
        all_names.extend(market_names)
        
        # 5. AI预测
        ai_features, ai_names = self.integrate_ai_predictions(ai_predictions)
        all_features.extend(ai_features)
        all_names.extend(ai_names)
        
        # 6. 订单簿（新增3维）
        if orderbook_data:
            all_features.extend([
                orderbook_data.get('orderbook_imbalance', 0),
                orderbook_data.get('support_strength', 50),
                orderbook_data.get('resistance_strength', 50)
            ])
            all_names.extend(['orderbook_imbalance', 'support_strength', 'resistance_strength'])
        else:
            all_features.extend([0, 50, 50])
            all_names.extend(['orderbook_imbalance', 'support_strength', 'resistance_strength'])
        
        # 7. 宏观指标（新增4维）
        if macro_data:
            all_features.extend([
                macro_data.get('dxy_change', 0),
                macro_data.get('sp500_change', 0),
                macro_data.get('vix_level', 20),
                macro_data.get('risk_appetite', 50)
            ])
            all_names.extend(['dxy_change', 'sp500_change', 'vix_level', 'risk_appetite'])
        else:
            all_features.extend([0, 0, 20, 50])
            all_names.extend(['dxy_change', 'sp500_change', 'vix_level', 'risk_appetite'])
        
        # 8. 期货数据（新增2维）
        if futures_data:
            all_features.extend([
                futures_data.get('oi_change', 0),
                futures_data.get('funding_trend', 0)
            ])
            all_names.extend(['oi_change', 'funding_trend'])
        else:
            all_features.extend([0, 0])
            all_names.extend(['oi_change', 'funding_trend'])
        
        # 9. 技术指标（Phase 2新增6维）
        if technical_indicators:
            all_features.extend([
                technical_indicators.get('macd_line', 0),
                technical_indicators.get('macd_signal', 0),
                technical_indicators.get('macd_hist', 0),
                technical_indicators.get('rsi', 50),
                technical_indicators.get('bb_position', 0.5),
                technical_indicators.get('ema_trend', 0)
            ])
            all_names.extend(['macd_line', 'macd_signal', 'macd_hist', 'rsi', 'bb_position', 'ema_trend'])
        else:
            all_features.extend([0, 0, 0, 50, 0.5, 0])
            all_names.extend(['macd_line', 'macd_signal', 'macd_hist', 'rsi', 'bb_position', 'ema_trend'])
        
        # 10. 多周期趋势（Phase 2新增4维）
        if multi_timeframe and 'timeframes' in multi_timeframe:
            tf = multi_timeframe['timeframes']
            all_features.extend([
                tf.get('1m', {}).get('trend', 0),
                tf.get('15m', {}).get('trend', 0),
                tf.get('1h', {}).get('trend', 0),
                tf.get('4h', {}).get('trend', 0)
            ])
            all_names.extend(['trend_1m', 'trend_15m', 'trend_1h', 'trend_4h'])
        else:
            all_features.extend([0, 0, 0, 0])
            all_names.extend(['trend_1m', 'trend_15m', 'trend_1h', 'trend_4h'])
        
        # 11. 支撑阻力（Phase 2新增2维）
        if support_resistance:
            all_features.extend([
                support_resistance.get('support_distance', 2.0),
                support_resistance.get('resistance_distance', 2.0)
            ])
            all_names.extend(['support_distance', 'resistance_distance'])
        else:
            all_features.extend([2.0, 2.0])
            all_names.extend(['support_distance', 'resistance_distance'])
        
        # 生成摘要
        summary = self._generate_summary(
            gas_data, kline_df, news_sentiment, 
            market_sentiment, ai_predictions
        )
        
        return {
            'features': all_features,
            'feature_names': all_names,
            'feature_count': len(all_features),
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_summary(self, gas_data, kline_df, news_sentiment, 
                         market_sentiment, ai_predictions):
        """生成关键指标摘要"""
        summary = {}
        
        # Gas费用
        if gas_data:
            summary['gas_suitable'] = gas_data.get('ETH', False) and gas_data.get('BTC', False)
        
        # 价格
        if kline_df is not None and not kline_df.empty:
            summary['price'] = float(kline_df.iloc[-1]['close'])
            summary['price_trend'] = 'up' if kline_df.iloc[-1]['close'] > kline_df.iloc[0]['close'] else 'down'
        
        # 情绪
        if market_sentiment:
            summary['sentiment'] = market_sentiment.get('overall_sentiment')
            summary['sentiment_score'] = market_sentiment.get('weighted_score')
        
        # AI共识
        if ai_predictions is not None and not ai_predictions.empty:
            up_count = 0
            down_count = 0
            for _, pred in ai_predictions.iterrows():
                for model in ['grok', 'gemini', 'deepseek']:
                    if pred.get(f'{model}_direction') == 'up':
                        up_count += 1
                    elif pred.get(f'{model}_direction') == 'down':
                        down_count += 1
            
            summary['ai_consensus'] = 'bullish' if up_count > down_count else ('bearish' if down_count > up_count else 'neutral')
        
        return summary
    
    def format_for_ai_prompt(self, integrated_data, technical_indicators=None, 
                              multi_timeframe=None, support_resistance=None):
        """
        格式化为AI Prompt友好的格式（包含Phase2技术指标）
        
        Args:
            integrated_data: 整合后的数据
            technical_indicators: 技术指标详细信息
            multi_timeframe: 多周期分析详细信息
            support_resistance: 支撑阻力详细信息
        
        Returns:
            str: AI可读的数据描述
        """
        features = integrated_data['features']
        names = integrated_data['feature_names']
        summary = integrated_data.get('summary', {})
        
        # 构建增强的数据描述
        prompt = "=" * 80 + "\n"
        prompt += "市场数据分析报告 (Phase 2增强版)\n"
        prompt += "=" * 80 + "\n\n"
        
        # 特征维度信息
        prompt += f"📊 特征维度: {len(features)}维\n"
        prompt += f"   - 基础数据: 26维\n"
        prompt += f"   - Phase1扩展: 9维 (订单簿+宏观+期货)\n"
        prompt += f"   - Phase2技术分析: 12维 (MACD+RSI+BB+多周期+支撑阻力)\n\n"
        
        # === 价格信息 ===
        prompt += "【💰 价格信息】\n"
        feature_dict = dict(zip(names, features))
        current_price = feature_dict.get('current_price', 0)
        price_change = feature_dict.get('price_change_pct', 0)
        volatility = feature_dict.get('volatility', 0)
        
        prompt += f"当前价格: ${current_price:,.2f}\n"
        prompt += f"价格变化: {price_change:+.2f}% ({self._get_trend_emoji(price_change)})\n"
        prompt += f"波动率: {volatility:.4f}\n"
        
        # 支撑阻力位
        if support_resistance:
            prompt += f"最近支撑: ${support_resistance.get('nearest_support', 0):,.2f} "
            prompt += f"(距离 {support_resistance.get('support_distance', 0):.2f}%)\n"
            prompt += f"最近阻力: ${support_resistance.get('nearest_resistance', 0):,.2f} "
            prompt += f"(距离 {support_resistance.get('resistance_distance', 0):.2f}%)\n"
        else:
            support_dist = feature_dict.get('support_distance', 2.0)
            resistance_dist = feature_dict.get('resistance_distance', 2.0)
            prompt += f"支撑距离: {support_dist:.2f}%, 阻力距离: {resistance_dist:.2f}%\n"
        
        prompt += "\n"
        
        # === 技术指标 ===
        prompt += "【📈 技术指标】\n"
        if technical_indicators:
            # MACD
            macd_line = technical_indicators.get('macd_line', 0)
            macd_signal = technical_indicators.get('macd_signal', 0)
            macd_hist = technical_indicators.get('macd_hist', 0)
            macd_signal_text = technical_indicators.get('macd_signal_text', 'neutral')
            
            prompt += f"MACD: {macd_line:.2f} (信号线: {macd_signal:.2f}, 柱: {macd_hist:.2f})\n"
            prompt += f"      状态: {self._translate_signal(macd_signal_text)} "
            prompt += f"{self._get_signal_emoji(macd_signal_text)}\n"
            
            # RSI
            rsi = technical_indicators.get('rsi', 50)
            rsi_signal = technical_indicators.get('rsi_signal', 'neutral')
            prompt += f"RSI(14): {rsi:.1f} - {self._translate_rsi(rsi_signal)} "
            prompt += f"{self._get_rsi_emoji(rsi)}\n"
            
            # 布林带
            bb_position = technical_indicators.get('bb_position', 0.5)
            bb_signal = technical_indicators.get('bb_signal', 'middle')
            prompt += f"布林带位置: {bb_position:.2f} ({self._translate_bb(bb_signal)}) "
            prompt += f"{self._get_bb_emoji(bb_position)}\n"
            
            # EMA
            ema_trend = technical_indicators.get('ema_trend', 0)
            prompt += f"EMA趋势: {self._translate_ema(ema_trend)} "
            prompt += f"{self._get_trend_emoji(ema_trend)}\n"
        else:
            prompt += f"MACD: {feature_dict.get('macd_line', 0):.2f}, "
            prompt += f"RSI: {feature_dict.get('rsi', 50):.1f}, "
            prompt += f"BB位置: {feature_dict.get('bb_position', 0.5):.2f}\n"
        
        prompt += "\n"
        
        # === 多周期趋势 ===
        prompt += "【⏱️ 多周期趋势分析】\n"
        if multi_timeframe and 'timeframes' in multi_timeframe:
            tf = multi_timeframe['timeframes']
            
            for period, label in [('1m', '1分钟'), ('15m', '15分钟'), 
                                  ('1h', '1小时'), ('4h', '4小时')]:
                trend = tf.get(period, {}).get('trend', 0)
                rsi = tf.get(period, {}).get('rsi', 50)
                prompt += f"{label:6s}: {self._translate_trend(trend)} "
                prompt += f"{self._get_trend_emoji(trend)} (RSI:{rsi:.0f})\n"
            
            consistency = multi_timeframe.get('trend_consistency', 0)
            overall = multi_timeframe.get('overall_trend', 0)
            prompt += f"\n趋势一致性: {consistency:.0%} "
            prompt += f"(主流方向: {self._translate_trend(overall)})\n"
        else:
            prompt += f"1分钟: {self._translate_trend(feature_dict.get('trend_1m', 0))}, "
            prompt += f"15分钟: {self._translate_trend(feature_dict.get('trend_15m', 0))}, "
            prompt += f"1小时: {self._translate_trend(feature_dict.get('trend_1h', 0))}, "
            prompt += f"4小时: {self._translate_trend(feature_dict.get('trend_4h', 0))}\n"
        
        prompt += "\n"
        
        # === 市场情绪 ===
        prompt += "【😊 市场情绪】\n"
        fear_greed = feature_dict.get('fear_greed_index', 50)
        prompt += f"恐惧贪婪指数: {fear_greed:.0f}/100 "
        prompt += f"({self._get_fear_greed_label(fear_greed)})\n"
        
        news_sentiment = feature_dict.get('news_sentiment', 0)
        news_count = feature_dict.get('news_count', 0)
        prompt += f"新闻情绪: {self._translate_sentiment(news_sentiment)} "
        prompt += f"(共{int(news_count)}条)\n"
        
        market_sentiment = feature_dict.get('market_sentiment_label', 0)
        prompt += f"市场情绪: {self._translate_sentiment(market_sentiment)}\n"
        
        prompt += "\n"
        
        # === Gas费用 ===
        prompt += "【⛽ Gas费用】\n"
        eth_gas = feature_dict.get('eth_gas_gwei', 0)
        btc_fee = feature_dict.get('btc_fee_sat', 0)
        eth_ok = feature_dict.get('eth_tradeable', 0)
        btc_ok = feature_dict.get('btc_tradeable', 0)
        
        prompt += f"ETH Gas: {eth_gas:.2f} Gwei {'✅' if eth_ok else '❌'}\n"
        prompt += f"BTC Fee: {btc_fee:.0f} sat/vB {'✅' if btc_ok else '❌'}\n"
        
        prompt += "\n"
        
        # === 完整特征向量 ===
        prompt += "【🔢 完整特征向量】\n"
        for i, (name, value) in enumerate(zip(names, features)):
            if isinstance(value, float):
                prompt += f"[{i:2d}] {name:25s}: {value:>10.4f}\n"
            else:
                prompt += f"[{i:2d}] {name:25s}: {value:>10}\n"
        
        prompt += "\n"
        prompt += "=" * 80 + "\n"
        
        return prompt
    
    def _get_trend_emoji(self, value):
        """获取趋势表情"""
        if value > 1:
            return "🚀"
        elif value > 0:
            return "📈"
        elif value < -1:
            return "💥"
        elif value < 0:
            return "📉"
        else:
            return "➡️"
    
    def _get_signal_emoji(self, signal):
        """获取信号表情"""
        if signal == 'bullish':
            return "🟢"
        elif signal == 'bearish':
            return "🔴"
        else:
            return "⚪"
    
    def _get_rsi_emoji(self, rsi):
        """获取RSI表情"""
        if rsi < 30:
            return "🟢 超卖"
        elif rsi > 70:
            return "🔴 超买"
        else:
            return "⚪ 中性"
    
    def _get_bb_emoji(self, position):
        """获取布林带表情"""
        if position < 0.2:
            return "⬇️"
        elif position > 0.8:
            return "⬆️"
        else:
            return "➡️"
    
    def _translate_signal(self, signal):
        """翻译信号"""
        mapping = {
            'bullish': '看多',
            'bearish': '看空',
            'neutral': '中性'
        }
        return mapping.get(signal, signal)
    
    def _translate_rsi(self, signal):
        """翻译RSI信号"""
        mapping = {
            'oversold': '超卖',
            'overbought': '超买',
            'neutral': '中性'
        }
        return mapping.get(signal, signal)
    
    def _translate_bb(self, signal):
        """翻译布林带信号"""
        mapping = {
            'lower': '接近下轨',
            'upper': '接近上轨',
            'middle': '中轨区域'
        }
        return mapping.get(signal, signal)
    
    def _translate_ema(self, trend):
        """翻译EMA趋势"""
        if trend == 1:
            return "金叉/多头"
        elif trend == -1:
            return "死叉/空头"
        else:
            return "震荡"
    
    def _translate_trend(self, trend):
        """翻译趋势"""
        if trend == 1:
            return "上涨"
        elif trend == -1:
            return "下跌"
        else:
            return "震荡"
    
    def _translate_sentiment(self, sentiment):
        """翻译情绪"""
        if sentiment == 1:
            return "看涨"
        elif sentiment == -1:
            return "看跌"
        else:
            return "中性"
    
    def _get_fear_greed_label(self, value):
        """恐惧贪婪标签"""
        if value < 25:
            return "极度恐惧"
        elif value < 45:
            return "恐惧"
        elif value < 55:
            return "中性"
        elif value < 75:
            return "贪婪"
        else:
            return "极度贪婪"
    
    def to_numpy_array(self, integrated_data):
        """转换为numpy数组"""
        return np.array(integrated_data['features'], dtype=np.float32)
    
    def to_dict(self, integrated_data):
        """转换为字典格式（特征名:值）"""
        return dict(zip(
            integrated_data['feature_names'],
            integrated_data['features']
        ))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 示例用法
    integrator = DataIntegrator()
    
    # 模拟数据
    gas_data = {
        'ETH': {'latest_gas': 0.08},
        'BTC': {'half_hour_fee': 1}
    }
    
    result = integrator.integrate_all(gas_data=gas_data)
    
    print("特征向量长度:", result['feature_count'])
    print("\n特征名称:", result['feature_names'])
    print("\n特征值:", result['features'])
    print("\n摘要:", result['summary'])
    
    # AI友好格式
    print("\n" + "="*60)
    print("AI Prompt格式:")
    print("="*60)
    print(integrator.format_for_ai_prompt(result))
