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
                     orderbook_data=None, macro_data=None, futures_data=None):
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
    
    def format_for_ai_prompt(self, integrated_data):
        """
        格式化为AI Prompt友好的格式
        
        Returns:
            str: AI可读的数据描述
        """
        features = integrated_data['features']
        names = integrated_data['feature_names']
        summary = integrated_data['summary']
        
        # 构建简洁的数据描述
        prompt = "市场数据向量:\n"
        prompt += f"特征维度: {len(features)}\n\n"
        
        # 关键指标
        prompt += "关键指标:\n"
        for i, (name, value) in enumerate(zip(names, features)):
            if isinstance(value, float):
                prompt += f"[{i}] {name}: {value:.4f}\n"
            else:
                prompt += f"[{i}] {name}: {value}\n"
        
        prompt += f"\n数据摘要: {summary}\n"
        
        return prompt
    
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
