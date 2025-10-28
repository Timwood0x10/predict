"""
金融新闻聚合模块
获取加密货币和宏观经济新闻
"""

import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FinancialNewsAggregator:
    """金融新闻聚合器"""
    
    def __init__(self, newsapi_key=""):
        self.newsapi_key = newsapi_key
        self.crypto_keywords = ["bitcoin", "ethereum", "BTC", "ETH", "crypto", "cryptocurrency"]
        self.macro_keywords = ["federal reserve", "interest rate", "inflation", "economy"]
    
    def get_crypto_news(self, limit=10):
        """获取加密货币新闻"""
        if not self.newsapi_key:
            logger.warning("未配置NewsAPI密钥")
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": "bitcoin OR ethereum OR crypto",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": limit,
                "apiKey": self.newsapi_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data["status"] == "ok":
                news_list = []
                for article in data["articles"]:
                    news_list.append({
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "source": article["source"]["name"],
                        "url": article["url"],
                        "published_at": article["publishedAt"],
                        "category": "crypto"
                    })
                
                logger.info(f"获取 {len(news_list)} 条加密货币新闻")
                return news_list
            
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            return []
    
    def get_macro_news(self, limit=10):
        """获取宏观经济新闻"""
        if not self.newsapi_key:
            logger.warning("未配置NewsAPI密钥")
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": "economy OR \"federal reserve\" OR inflation",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": limit,
                "apiKey": self.newsapi_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data["status"] == "ok":
                news_list = []
                for article in data["articles"]:
                    news_list.append({
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "source": article["source"]["name"],
                        "url": article["url"],
                        "published_at": article["publishedAt"],
                        "category": "macro"
                    })
                
                logger.info(f"获取 {len(news_list)} 条宏观经济新闻")
                return news_list
            
        except Exception as e:
            logger.error(f"获取宏观新闻失败: {e}")
            return []
    
    def get_all_news(self, crypto_limit=10, macro_limit=5):
        """获取所有类型新闻"""
        all_news = []
        
        crypto_news = self.get_crypto_news(limit=crypto_limit)
        all_news.extend(crypto_news)
        
        macro_news = self.get_macro_news(limit=macro_limit)
        all_news.extend(macro_news)
        
        all_news.sort(key=lambda x: x["published_at"], reverse=True)
        
        return all_news
    
    def analyze_sentiment(self, news_list):
        """分析新闻情绪"""
        positive_words = ["surge", "rally", "gain", "bullish", "up", "rise", "growth", "profit"]
        negative_words = ["crash", "drop", "fall", "bearish", "down", "decline", "loss", "fear"]
        
        positive_count = 0
        negative_count = 0
        
        for news in news_list:
            text = (news["title"] + " " + news.get("description", "")).lower()
            
            has_positive = any(word in text for word in positive_words)
            has_negative = any(word in text for word in negative_words)
            
            if has_positive:
                positive_count += 1
            if has_negative:
                negative_count += 1
        
        total = positive_count + negative_count
        
        if total == 0:
            sentiment = "neutral"
            score = 0
        else:
            score = (positive_count - negative_count) / total * 100
            
            if score > 20:
                sentiment = "bullish"
            elif score < -20:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "total_news": len(news_list)
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    aggregator = FinancialNewsAggregator(newsapi_key="YOUR_KEY")
    news = aggregator.get_all_news()
    
    print(f"获取到 {len(news)} 条新闻")
    for item in news[:3]:
        print(f"[{item['category']}] {item['title']}")
    
    sentiment = aggregator.analyze_sentiment(news)
    print(f"\n情绪分析: {sentiment}")
