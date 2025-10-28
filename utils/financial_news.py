"""
金融新闻聚合模块
获取加密货币和宏观经济新闻
"""

import requests
from datetime import datetime
import logging
import xml.etree.ElementTree as ET
import re

logger = logging.getLogger(__name__)


class FinancialNewsAggregator:
    """金融新闻聚合器"""
    
    def __init__(self, newsapi_key="", cryptocompare_key=""):
        self.newsapi_key = newsapi_key
        self.cryptocompare_key = cryptocompare_key
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
    
    def get_cryptocompare_news(self, limit=10):
        """从CryptoCompare获取加密货币新闻（免费）"""
        try:
            url = "https://min-api.cryptocompare.com/data/v2/news/"
            params = {"lang": "EN"}
            
            if self.cryptocompare_key:
                params["api_key"] = self.cryptocompare_key
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("Type") == 100 and data.get("Data"):
                news_list = []
                for article in data["Data"][:limit]:
                    # 清洗标题和内容
                    title = self._clean_text(article.get("title", ""))
                    body = self._clean_text(article.get("body", ""))
                    
                    news_list.append({
                        "title": title,
                        "description": body[:200] if body else "",  # 限制长度
                        "source": article.get("source", "CryptoCompare"),
                        "url": article.get("url", ""),
                        "published_at": datetime.fromtimestamp(article.get("published_on", 0)).isoformat(),
                        "category": "crypto",
                        "tags": article.get("tags", "").split("|")[:3]  # 取前3个标签
                    })
                
                logger.info(f"CryptoCompare: 获取 {len(news_list)} 条新闻")
                return news_list
            
        except Exception as e:
            logger.error(f"获取CryptoCompare新闻失败: {e}")
            return []
    
    def get_odaily_news(self, limit=20):
        """从Odaily RSS获取中文加密新闻"""
        try:
            url = "https://rss.odaily.news/rss/newsflash"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            # 解析RSS
            root = ET.fromstring(response.content)
            
            news_list = []
            for item in root.findall('.//item')[:limit]:
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')
                
                # 清洗数据
                title_text = self._clean_text(title.text if title is not None else "")
                desc_text = self._clean_text(description.text if description is not None else "")
                
                # 跳过空内容
                if not title_text:
                    continue
                
                # 转换发布时间
                pub_date_str = pub_date.text if pub_date is not None else ""
                try:
                    # RSS日期格式: "Mon, 28 Oct 2024 12:00:00 +0800"
                    from email.utils import parsedate_to_datetime
                    pub_datetime = parsedate_to_datetime(pub_date_str)
                    published_at = pub_datetime.isoformat()
                except:
                    published_at = datetime.now().isoformat()
                
                news_list.append({
                    "title": title_text,
                    "description": desc_text[:200],  # 限制长度
                    "source": "Odaily",
                    "url": link.text if link is not None else "",
                    "published_at": published_at,
                    "category": "crypto",
                    "language": "zh"  # 中文标记
                })
            
            logger.info(f"Odaily: 获取 {len(news_list)} 条新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"获取Odaily新闻失败: {e}")
            return []
    
    def _clean_text(self, text):
        """清洗文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（保留中文、英文、数字、基本标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:\'\"()-]', '', text)
        
        # 去除首尾空格
        text = text.strip()
        
        return text
    
    def get_all_news(self, crypto_limit=10, macro_limit=5, include_chinese=True):
        """获取所有类型新闻"""
        all_news = []
        
        # 1. NewsAPI加密货币新闻
        crypto_news = self.get_crypto_news(limit=crypto_limit)
        if crypto_news:
            all_news.extend(crypto_news)
        
        # 2. NewsAPI宏观经济新闻
        macro_news = self.get_macro_news(limit=macro_limit)
        if macro_news:
            all_news.extend(macro_news)
        
        # 3. CryptoCompare专业新闻（免费）
        cc_news = self.get_cryptocompare_news(limit=crypto_limit)
        if cc_news:
            all_news.extend(cc_news)
        
        # 4. Odaily中文新闻（可选）
        if include_chinese:
            odaily_news = self.get_odaily_news(limit=15)
            if odaily_news:
                all_news.extend(odaily_news)
        
        # 按时间排序
        all_news.sort(key=lambda x: x["published_at"], reverse=True)
        
        # 去重（基于标题相似度）
        all_news = self._deduplicate_news(all_news)
        
        logger.info(f"总计获取 {len(all_news)} 条新闻")
        return all_news
    
    def _deduplicate_news(self, news_list):
        """去除重复新闻"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            # 简单去重：标题小写后比较
            title_key = news["title"].lower()[:50]  # 取前50个字符
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        return unique_news
    
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
