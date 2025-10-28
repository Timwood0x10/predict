"""
市场情绪分析模块
整合多个情绪数据源进行综合分析
"""

import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MarketSentimentAnalyzer:
    """市场情绪分析器"""
    
    def __init__(self, cryptoracle_key=""):
        self.cryptoracle_key = cryptoracle_key
        self.cryptoracle_url = "https://service.cryptoracle.network/openapi/v2"
        self.sentiment_history = []
    
    def get_fear_greed_index(self):
        """获取恐惧贪婪指数"""
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("data"):
                fng_data = data["data"][0]
                value = int(fng_data["value"])
                
                if value < 25:
                    sentiment = "extreme_fear"
                elif value < 45:
                    sentiment = "fear"
                elif value < 55:
                    sentiment = "neutral"
                elif value < 75:
                    sentiment = "greed"
                else:
                    sentiment = "extreme_greed"
                
                result = {
                    "timestamp": datetime.fromtimestamp(int(fng_data["timestamp"])),
                    "value": value,
                    "sentiment": sentiment,
                    "classification": fng_data["value_classification"],
                    "source": "fear_greed_index"
                }
                
                logger.info(f"恐惧贪婪指数: {value} ({sentiment})")
                return result
            
        except Exception as e:
            logger.error(f"获取恐惧贪婪指数失败: {e}")
            return None
    
    def get_cryptoracle_sentiment(self, symbol="BTC"):
        """从CryptOracle获取市场情绪"""
        if not self.cryptoracle_key:
            logger.warning("未配置CryptOracle API密钥")
            return None
        
        try:
            url = f"{self.cryptoracle_url}/sentiment/{symbol}"
            headers = {"Authorization": f"Bearer {self.cryptoracle_key}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                sentiment_data = {
                    "symbol": symbol,
                    "timestamp": datetime.now(),
                    "sentiment": data.get("sentiment", "neutral"),
                    "score": data.get("score", 0),
                    "confidence": data.get("confidence", 0),
                    "source": "cryptoracle"
                }
                
                logger.info(f"CryptOracle情绪: {sentiment_data['sentiment']}")
                return sentiment_data
            
        except Exception as e:
            logger.error(f"CryptOracle获取失败: {e}")
            return None
    
    def get_comprehensive_sentiment(self, symbol="BTC"):
        """获取综合市场情绪"""
        logger.info(f"分析 {symbol} 市场情绪...")
        
        sentiments = []
        
        # 恐惧贪婪指数
        fng = self.get_fear_greed_index()
        if fng:
            fng_score = (fng["value"] - 50) * 2  # 转换为-100到100
            sentiments.append({
                "source": "fear_greed",
                "score": fng_score,
                "weight": 0.6
            })
        
        # CryptOracle
        oracle = self.get_cryptoracle_sentiment(symbol)
        if oracle:
            sentiments.append({
                "source": "cryptoracle",
                "score": oracle["score"],
                "weight": 0.4
            })
        
        if not sentiments:
            logger.warning("无法获取情绪数据")
            return None
        
        # 计算加权分数
        total_weight = sum(s["weight"] for s in sentiments)
        weighted_score = sum(s["score"] * s["weight"] for s in sentiments) / total_weight
        
        if weighted_score > 20:
            overall_sentiment = "bullish"
        elif weighted_score < -20:
            overall_sentiment = "bearish"
        else:
            overall_sentiment = "neutral"
        
        result = {
            "symbol": symbol,
            "timestamp": datetime.now(),
            "overall_sentiment": overall_sentiment,
            "weighted_score": weighted_score,
            "confidence": abs(weighted_score),
            "sources": sentiments,
            "interpretation": self._interpret(weighted_score)
        }
        
        logger.info(f"综合情绪: {overall_sentiment} (分数: {weighted_score:.1f})")
        
        self.sentiment_history.append(result)
        if len(self.sentiment_history) > 100:
            self.sentiment_history.pop(0)
        
        return result
    
    def _interpret(self, score):
        """解释情绪分数"""
        if score > 60:
            return "极度看涨 - 警惕过度贪婪"
        elif score > 20:
            return "看涨 - 市场情绪积极"
        elif score > -20:
            return "中性 - 观望为主"
        elif score > -60:
            return "看跌 - 市场情绪消极"
        else:
            return "极度看跌 - 恐慌情绪严重"
    
    def should_trade_based_on_sentiment(self, symbol="BTC", min_confidence=50):
        """根据情绪判断是否交易"""
        sentiment = self.get_comprehensive_sentiment(symbol)
        
        if not sentiment:
            return False, None, "无法获取情绪数据"
        
        if sentiment["confidence"] < min_confidence:
            return False, None, f"置信度过低: {sentiment['confidence']:.1f}"
        
        overall = sentiment["overall_sentiment"]
        score = sentiment["weighted_score"]
        
        if overall == "bullish" and score > 30:
            return True, "BUY", f"市场看涨 (分数: {score:.1f})"
        elif overall == "bearish" and score < -30:
            return True, "SELL", f"市场看跌 (分数: {score:.1f})"
        else:
            return False, None, f"情绪不明确 (分数: {score:.1f})"


class SentimentIntegrator:
    """情绪集成器"""
    
    def __init__(self, sentiment_analyzer):
        self.sentiment_analyzer = sentiment_analyzer
    
    def enhance_trading_signal(self, signal, symbol="BTC"):
        """用情绪增强交易信号"""
        if not signal:
            return None
        
        sentiment = self.sentiment_analyzer.get_comprehensive_sentiment(symbol)
        
        if not sentiment:
            return signal
        
        enhanced = signal.copy()
        enhanced["sentiment"] = sentiment["overall_sentiment"]
        enhanced["sentiment_score"] = sentiment["weighted_score"]
        
        signal_action = signal.get("action")
        sentiment_dir = sentiment["overall_sentiment"]
        
        # 检查一致性
        if signal_action == "BUY" and sentiment_dir == "bearish":
            enhanced["warning"] = "⚠️ 信号与情绪相反"
            enhanced["adjusted_confidence"] = signal.get("confidence", 100) * 0.7
        elif signal_action == "SELL" and sentiment_dir == "bullish":
            enhanced["warning"] = "⚠️ 信号与情绪相反"
            enhanced["adjusted_confidence"] = signal.get("confidence", 100) * 0.7
        else:
            enhanced["adjusted_confidence"] = min(100, signal.get("confidence", 100) * 1.2)
            enhanced["note"] = "✅ 信号与情绪一致"
        
        return enhanced


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = MarketSentimentAnalyzer()
    sentiment = analyzer.get_comprehensive_sentiment("BTC")
    
    if sentiment:
        print(f"\n情绪: {sentiment['overall_sentiment']}")
        print(f"分数: {sentiment['weighted_score']:.1f}")
        print(f"解释: {sentiment['interpretation']}")
