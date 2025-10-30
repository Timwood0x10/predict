"""
Polymarket数据获取器
获取Polymarket预测市场上关于BTC和ETH的态度
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class PolymarketFetcher:
    """Polymarket预测市场数据获取"""
    
    def __init__(self):
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.clob_api = "https://clob.polymarket.com"
        
    def get_markets(self, limit: int = 100) -> Optional[List[Dict]]:
        """获取市场列表"""
        try:
            url = f"{self.gamma_api}/markets"
            params = {
                "active": "true",
                "closed": "false",
                "limit": limit
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 处理不同的返回格式
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    if 'data' in data:
                        return data['data']
                    elif 'markets' in data:
                        return data['markets']
                
                logger.warning(f"未知的Polymarket响应格式: {type(data)}")
                return None
            else:
                logger.warning(f"Polymarket API返回: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求Polymarket失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取市场列表失败: {e}")
            return None
    
    def filter_crypto_markets(self, markets: List[Dict], symbol: str) -> List[Dict]:
        """筛选加密货币相关市场"""
        keywords = {
            'BTC': ['bitcoin', 'btc', 'BTC', 'Bitcoin'],
            'ETH': ['ethereum', 'eth', 'ETH', 'Ethereum']
        }
        
        search_terms = keywords.get(symbol, ['bitcoin'])
        filtered = []
        
        for market in markets:
            # 检查各个字段
            question = str(market.get('question', ''))
            description = str(market.get('description', ''))
            title = str(market.get('title', ''))
            
            # 检查是否包含关键词
            for term in search_terms:
                if (term in question or term in description or term in title):
                    # 确保是价格相关的市场
                    text_lower = (question + description).lower()
                    if any(word in text_lower for word in ['price', '$', 'usd', 'trade', 'reach', 'above', 'below']):
                        filtered.append(market)
                        break
        
        return filtered
    
    def extract_probability(self, market: Dict) -> float:
        """提取市场概率"""
        try:
            # 尝试多种字段
            if 'outcomePrices' in market:
                prices = market['outcomePrices']
                if isinstance(prices, str):
                    prices = json.loads(prices)
                if isinstance(prices, list) and len(prices) > 0:
                    return float(prices[0])
            
            if 'tokens' in market:
                tokens = market['tokens']
                if isinstance(tokens, list) and len(tokens) > 0:
                    token = tokens[0]
                    if 'price' in token:
                        return float(token['price'])
            
            if 'outcomes' in market:
                outcomes = market['outcomes']
                if isinstance(outcomes, list) and len(outcomes) > 0:
                    outcome = outcomes[0]
                    if 'price' in outcome:
                        return float(outcome['price'])
            
            # 默认返回0.5（中性）
            return 0.5
            
        except Exception as e:
            logger.debug(f"提取概率失败: {e}")
            return 0.5
    
    def analyze_market_direction(self, question: str) -> str:
        """分析市场方向（看涨/看跌）"""
        question_lower = question.lower()
        
        # 看涨关键词
        bullish_words = ['above', 'reach', 'exceed', 'hit', 'higher', 'rise', 'surge', 'rally']
        # 看跌关键词
        bearish_words = ['below', 'under', 'lower', 'fall', 'drop', 'crash', 'decline']
        
        bullish_count = sum(1 for word in bullish_words if word in question_lower)
        bearish_count = sum(1 for word in bearish_words if word in question_lower)
        
        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        else:
            return 'neutral'
    
    def get_market_sentiment(self, symbol: str = "BTC") -> Dict:
        """
        获取市场情绪
        
        Args:
            symbol: 币种符号（BTC, ETH）
            
        Returns:
            市场情绪数据
        """
        try:
            # 获取所有市场
            all_markets = self.get_markets(limit=100)
            
            if not all_markets:
                logger.warning(f"无法获取Polymarket市场列表")
                return self._get_fallback_sentiment(symbol)
            
            logger.info(f"获取到{len(all_markets)}个Polymarket市场")
            
            # 筛选相关市场
            crypto_markets = self.filter_crypto_markets(all_markets, symbol)
            
            if not crypto_markets:
                logger.warning(f"未找到{symbol}相关市场")
                return self._get_fallback_sentiment(symbol)
            
            logger.info(f"找到{len(crypto_markets)}个{symbol}相关市场")
            
            # 分析市场
            return self._analyze_sentiment(crypto_markets, symbol)
            
        except Exception as e:
            logger.error(f"获取{symbol}情绪失败: {e}")
            return self._get_fallback_sentiment(symbol)
    
    def _analyze_sentiment(self, markets: List[Dict], symbol: str) -> Dict:
        """分析市场情绪"""
        
        bullish_probs = []
        bearish_probs = []
        analyzed_markets = []
        
        for market in markets:
            question = market.get('question', '')
            
            if not question:
                continue
            
            # 提取概率
            prob = self.extract_probability(market)
            
            # 判断方向
            direction = self.analyze_market_direction(question)
            
            if direction == 'bullish':
                bullish_probs.append(prob)
            elif direction == 'bearish':
                bearish_probs.append(prob)
            else:
                # 中性问题，根据概率判断
                if prob > 0.5:
                    bullish_probs.append(prob)
                    direction = 'bullish'
                else:
                    bearish_probs.append(1 - prob)
                    direction = 'bearish'
            
            analyzed_markets.append({
                'question': question[:80] + '...' if len(question) > 80 else question,
                'probability': prob,
                'type': direction
            })
        
        if not analyzed_markets:
            logger.warning(f"未找到有效的{symbol}市场")
            return self._get_fallback_sentiment(symbol)
        
        # 计算平均概率
        avg_bullish = sum(bullish_probs) / len(bullish_probs) if bullish_probs else 0
        avg_bearish = sum(bearish_probs) / len(bearish_probs) if bearish_probs else 0
        
        # 净情绪
        net_sentiment = (avg_bullish * len(bullish_probs) - avg_bearish * len(bearish_probs)) / len(analyzed_markets)
        
        # 整体态度
        if net_sentiment > 0.1:
            overall = 'bullish'
        elif net_sentiment < -0.1:
            overall = 'bearish'
        else:
            overall = 'neutral'
        
        # 评分（0-100）
        score = 50 + (net_sentiment * 50)
        score = max(0, min(100, score))
        
        return {
            'symbol': symbol,
            'overall_sentiment': overall,
            'bullish_probability': avg_bullish,
            'bearish_probability': avg_bearish,
            'net_sentiment': net_sentiment,
            'score': score,
            'confidence': abs(net_sentiment) * 100,
            'market_count': len(analyzed_markets),
            'bullish_markets': len(bullish_probs),
            'bearish_markets': len(bearish_probs),
            'markets': analyzed_markets[:5],
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_fallback_sentiment(self, symbol: str) -> Dict:
        """备用数据"""
        return {
            'symbol': symbol,
            'overall_sentiment': 'neutral',
            'bullish_probability': 0.5,
            'bearish_probability': 0.5,
            'net_sentiment': 0.0,
            'score': 50.0,
            'confidence': 0.0,
            'market_count': 0,
            'bullish_markets': 0,
            'bearish_markets': 0,
            'markets': [],
            'timestamp': datetime.now().isoformat(),
            'note': 'Polymarket数据不可用，使用默认值'
        }
    
    def get_comprehensive_prediction(self, symbol: str = "BTC") -> Dict:
        """获取综合预测（主接口）"""
        return self.get_market_sentiment(symbol)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    fetcher = PolymarketFetcher()
    
    print("\n" + "="*80)
    print("🎲 Polymarket预测市场数据测试")
    print("="*80)
    
    for symbol in ['BTC', 'ETH']:
        print(f"\n【{symbol}预测】")
        data = fetcher.get_comprehensive_prediction(symbol)
        
        print(f"  整体态度: {data.get('overall_sentiment')}")
        print(f"  Polymarket评分: {data.get('score', 0):.1f}/100")
        print(f"  看涨市场: {data.get('bullish_markets', 0)}个 (平均概率 {data.get('bullish_probability', 0)*100:.1f}%)")
        print(f"  看跌市场: {data.get('bearish_markets', 0)}个 (平均概率 {data.get('bearish_probability', 0)*100:.1f}%)")
        print(f"  净情绪: {data.get('net_sentiment', 0):+.3f}")
        
        if data.get('markets'):
            print(f"  相关市场示例:")
            for i, m in enumerate(data['markets'][:3], 1):
                print(f"    {i}. [{m['type']}] {m['question']}")
                print(f"       概率: {m['probability']*100:.0f}%")
    
    print("\n" + "="*80)
