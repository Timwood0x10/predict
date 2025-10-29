"""
新闻增强处理模块
- 关键词提取
- 中文翻译为英文（可选）
- 智能摘要
- Token优化
"""

import re
import logging

logger = logging.getLogger(__name__)

# 尝试导入翻译库（可选）
try:
    from googletrans import Translator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    logger.warning("googletrans未安装，翻译功能不可用")


class NewsProcessor:
    """新闻处理器 - 提取关键词、翻译、摘要"""
    
    # 加密货币关键词词典
    CRYPTO_KEYWORDS = {
        # 主流币种
        'btc', 'bitcoin', 'eth', 'ethereum', 'usdt', 'tether', 'bnb', 'binance',
        'sol', 'solana', 'ada', 'cardano', 'xrp', 'ripple', 'doge', 'dogecoin',
        'matic', 'polygon', 'avax', 'avalanche', 'dot', 'polkadot',
        
        # DeFi/NFT
        'defi', 'nft', 'dao', 'dex', 'cefi', 'web3', 'metaverse', 'gamefi',
        'yield', 'liquidity', 'amm', 'swap', 'uniswap', 'pancakeswap',
        
        # 交易行为
        'pump', 'dump', 'surge', 'crash', 'rally', 'dip', 'moon', 'bullish', 
        'bearish', 'halving', 'fork', 'airdrop', 'staking', 'mining',
        'whale', 'accumulation', 'distribution',
        
        # 金融机构
        'sec', 'fed', 'federal reserve', 'treasury', 'cftc', 'finra',
        'blackrock', 'grayscale', 'fidelity', 'vanguard', 'jpmorgan',
        'goldman sachs', 'morgan stanley', 'citadel',
        
        # 交易所
        'coinbase', 'binance', 'kraken', 'ftx', 'okx', 'huobi', 'bybit',
        'gemini', 'bitfinex', 'bitstamp',
        
        # 机构/公司
        'microstrategy', 'tesla', 'square', 'paypal', 'visa', 'mastercard',
        
        # 金融产品
        'etf', 'futures', 'options', 'derivatives', 'spot', 'perpetual',
        
        # 技术/概念
        'blockchain', 'layer2', 'validator', 'consensus', 'smart contract',
        'gas', 'gwei', 'wallet', 'cold wallet', 'hot wallet',
        
        # 监管/政策
        'regulation', 'compliance', 'ban', 'approval', 'license', 'cbdc',
        'money laundering', 'kyc', 'aml'
    }
    
    # 价格相关词
    PRICE_WORDS = {
        'surge', 'pump', 'moon', 'ath', 'all-time high', 'high', 'rally', 'gain', 'up', 'rise',
        'crash', 'dump', 'dip', 'drop', 'fall', 'down', 'loss', 'low', 'plunge', 'decline'
    }
    
    # 金融相关关键词（重点关注宏观政策）
    FINANCE_KEYWORDS = {
        # 美联储相关（高优先级）
        'fed', 'federal reserve', 'powell', 'jerome powell', 'fomc', 'federal open market',
        'interest rate', 'rate hike', 'rate cut', 'rate decision', 'fed meeting',
        'monetary policy', 'quantitative easing', 'qe', 'taper', 'tapering',
        'fed minutes', 'dot plot', 'fed fund rate',
        
        # 中美关系（高优先级）
        'china', 'us-china', 'sino-us', 'trade war', 'tariff', 'tariffs',
        'china us', 'beijing', 'washington', 'xi jinping', 'biden', 'trump',
        'export control', 'sanctions', 'import', 'export', 'trade deal',
        'semiconductor', 'tech war', 'huawei', 'taiwan', 'strait',
        
        # 关税贸易政策（高优先级）
        'customs', 'duty', 'trade policy', 'protectionism', 'free trade',
        'trade agreement', 'wto', 'trade deficit', 'trade surplus',
        
        # 通胀与经济指标
        'inflation', 'cpi', 'pce', 'deflation', 'stagflation',
        'gdp', 'unemployment', 'job report', 'nonfarm payroll',
        'recession', 'economic growth', 'consumer confidence',
        
        # 货币与外汇
        'dollar', 'dxy', 'dollar index', 'currency', 'yuan', 'rmb', 'renminbi',
        'exchange rate', 'forex', 'devaluation', 'appreciation',
        
        # 债券与利率
        'treasury', 'bond', 'yield', 'yield curve', '10-year', 'bond market',
        
        # 其他央行
        'ecb', 'european central bank', 'lagarde',
        'bank of japan', 'boj', 'bank of england', 'boe',
        'pboc', 'people bank of china'
    }
    
    # 高优先级关键词（影响最大的）
    HIGH_PRIORITY_KEYWORDS = {
        'fed', 'federal reserve', 'powell', 'fomc', 'rate hike', 'rate cut',
        'tariff', 'tariffs', 'china', 'us-china', 'trade war',
        'inflation', 'cpi', 'interest rate'
    }
    
    def __init__(self, enable_translation=True):
        """
        初始化
        
        Args:
            enable_translation: 是否启用翻译
        """
        self.enable_translation = enable_translation and TRANSLATION_AVAILABLE
        
        if enable_translation and not TRANSLATION_AVAILABLE:
            logger.warning("翻译已禁用：googletrans未安装")
        
        self.translator = Translator() if self.enable_translation else None
        self.translation_cache = {}  # 翻译缓存
    
    def is_relevant_news(self, text):
        """
        判断新闻是否与金融/加密货币相关
        
        Args:
            text: 新闻文本（标题+描述）
        
        Returns:
            True=相关, False=无关
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # 检查是否包含加密货币关键词
        crypto_match = any(kw in text_lower for kw in self.CRYPTO_KEYWORDS)
        
        # 检查是否包含金融关键词
        finance_match = any(kw in text_lower for kw in self.FINANCE_KEYWORDS)
        
        # 任一匹配即认为相关
        return crypto_match or finance_match
    
    def extract_keywords(self, text, max_keywords=5):
        """
        提取加密货币和金融关键词（优先高优先级）
        
        Args:
            text: 文本内容
            max_keywords: 最大关键词数
        
        Returns:
            关键词列表
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        # 查找加密货币关键词
        for keyword in self.CRYPTO_KEYWORDS:
            if keyword in text_lower:
                count = text_lower.count(keyword)
                weight = 1
                
                # 价格相关词加权
                if keyword in self.PRICE_WORDS:
                    weight = 2
                
                found_keywords.append((keyword, count * weight, 'crypto'))
        
        # 查找金融关键词
        for keyword in self.FINANCE_KEYWORDS:
            if keyword in text_lower:
                count = text_lower.count(keyword)
                weight = 1
                
                # 高优先级关键词（美联储、中美、关税）加权
                if keyword in self.HIGH_PRIORITY_KEYWORDS:
                    weight = 3  # 3倍权重
                
                found_keywords.append((keyword, count * weight, 'finance'))
        
        # 按加权频率排序
        found_keywords.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N个（只返回关键词）
        return [kw[0] for kw in found_keywords[:max_keywords]]
    
    def translate_to_english(self, text, source_lang='zh-cn'):
        """
        翻译为英文
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
        
        Returns:
            英文文本
        """
        if not text or not self.enable_translation:
            return text
        
        # 检查缓存
        cache_key = f"{source_lang}:{text[:100]}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            result = self.translator.translate(text, src=source_lang, dest='en')
            translated = result.text
            
            # 缓存结果
            self.translation_cache[cache_key] = translated
            
            logger.info(f"翻译: {text[:30]}... → {translated[:30]}...")
            return translated
            
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return text  # 返回原文
    
    def detect_language(self, text):
        """
        检测文本语言
        
        Args:
            text: 文本
        
        Returns:
            语言代码 ('zh'/'en'/...)
        """
        if not text:
            return 'en'
        
        # 简单检测：是否包含中文字符
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        else:
            return 'en'
    
    def extract_key_sentence(self, text, max_length=100):
        """
        提取关键句子（摘要）
        
        Args:
            text: 文本
            max_length: 最大长度
        
        Returns:
            摘要文本
        """
        if not text:
            return ""
        
        # 按句子分割
        sentences = re.split(r'[。！？.!?]', text)
        
        if not sentences:
            return text[:max_length]
        
        # 评分：包含关键词的句子优先
        scored_sentences = []
        for sent in sentences:
            if len(sent.strip()) < 10:  # 太短的跳过
                continue
            
            score = 0
            sent_lower = sent.lower()
            
            # 关键词加分
            for keyword in self.CRYPTO_KEYWORDS:
                if keyword in sent_lower:
                    score += 1
            
            # 价格词加分
            for word in self.PRICE_WORDS:
                if word in sent_lower:
                    score += 2
            
            scored_sentences.append((sent.strip(), score))
        
        if not scored_sentences:
            return text[:max_length]
        
        # 返回得分最高的句子
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        best_sentence = scored_sentences[0][0]
        
        # 截断到最大长度
        if len(best_sentence) > max_length:
            best_sentence = best_sentence[:max_length] + "..."
        
        return best_sentence
    
    def process_single_news(self, news_item):
        """
        处理单条新闻
        
        Args:
            news_item: {
                'title': '标题',
                'description': '描述',
                'source': '来源',
                'published_at': '时间',
                'language': 'zh'|'en' (可选)
            }
        
        Returns:
            处理后的新闻
        """
        title = news_item.get('title', '')
        desc = news_item.get('description', '')
        source = news_item.get('source', '')
        
        # 检测语言
        lang = news_item.get('language')
        if not lang:
            lang = self.detect_language(title)
        
        # 原始内容
        original_title = title
        original_desc = desc
        
        # 1. 翻译（如果是中文）
        if lang == 'zh' and self.enable_translation:
            try:
                title = self.translate_to_english(title, 'zh-cn')
                if desc:
                    desc = self.translate_to_english(desc, 'zh-cn')
            except Exception as e:
                logger.error(f"翻译失败: {e}")
        
        # 2. 提取关键词
        full_text = f"{title} {desc}"
        keywords = self.extract_keywords(full_text, max_keywords=5)
        
        # 3. 提取关键句（摘要）
        summary = self.extract_key_sentence(desc if desc else title, max_length=100)
        
        # 4. 计算Token数（粗略估计）
        simplified_text = f"{title} {' '.join(keywords)} {summary}"
        token_count = len(simplified_text.split())
        
        processed = {
            'original_title': original_title,
            'original_description': original_desc,
            'title': title,
            'description': desc,
            'keywords': keywords,
            'summary': summary,
            'source': source,
            'published_at': news_item.get('published_at', ''),
            'language': lang,
            'token_count': token_count
        }
        
        return processed
    
    def process_news_list(self, news_list, filter_irrelevant=True):
        """
        批量处理新闻
        
        Args:
            news_list: 新闻列表
            filter_irrelevant: 是否过滤无关新闻
        
        Returns:
            处理后的新闻列表
        """
        processed_list = []
        filtered_count = 0
        
        for news in news_list:
            try:
                # 过滤：只保留金融/加密货币相关新闻
                if filter_irrelevant:
                    title = news.get('title', '')
                    desc = news.get('description', '')
                    full_text = f"{title} {desc}"
                    
                    if not self.is_relevant_news(full_text):
                        filtered_count += 1
                        logger.debug(f"过滤无关新闻: {title[:50]}...")
                        continue
                
                processed = self.process_single_news(news)
                processed_list.append(processed)
            except Exception as e:
                logger.error(f"处理新闻失败: {e}")
                continue
        
        logger.info(f"成功处理 {len(processed_list)}/{len(news_list)} 条新闻 (过滤 {filtered_count} 条无关)")
        return processed_list
    
    def generate_compact_prompt(self, processed_news_list, max_news=10):
        """
        生成紧凑的AI Prompt（省Token）
        
        Args:
            processed_news_list: 处理后的新闻列表
            max_news: 最多包含新闻数
        
        Returns:
            紧凑的Prompt文本
        """
        if not processed_news_list:
            return "No recent news"
        
        # 只取最新的N条
        news_subset = processed_news_list[:max_news]
        
        # 收集所有关键词
        all_keywords = []
        for news in news_subset:
            all_keywords.extend(news.get('keywords', []))
        
        # 去重并统计频率
        keyword_freq = {}
        for kw in all_keywords:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
        
        # 按频率排序
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [kw[0] for kw in top_keywords[:10]]
        
        # 格式1: 超精简版（仅关键词+数量）
        prompt = f"News: {len(news_subset)} items, Hot topics: {', '.join(top_keywords)}\n"
        
        # 格式2: 标题+关键词（前5条）
        prompt += "Headlines:\n"
        for i, news in enumerate(news_subset[:5], 1):
            keywords_str = ','.join(news.get('keywords', [])[:3])
            title = news['title'][:60]  # 截断标题
            prompt += f"{i}. {title}... [{keywords_str}]\n"
        
        return prompt
    
    def generate_detailed_summary(self, processed_news_list, max_news=5):
        """
        生成详细摘要（包含更多信息）
        
        Args:
            processed_news_list: 处理后的新闻列表
            max_news: 最多包含新闻数
        
        Returns:
            详细摘要文本
        """
        if not processed_news_list:
            return "No recent news available"
        
        news_subset = processed_news_list[:max_news]
        
        summary = f"📰 Latest {len(news_subset)} News Updates:\n\n"
        
        for i, news in enumerate(news_subset, 1):
            summary += f"[{i}] {news['title']}\n"
            summary += f"    Keywords: {', '.join(news.get('keywords', []))}\n"
            summary += f"    Summary: {news.get('summary', 'N/A')}\n"
            summary += f"    Source: {news['source']} | {news['published_at'][:10]}\n\n"
        
        return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试
    processor = NewsProcessor(enable_translation=True)
    
    # 测试新闻
    test_news = {
        'title': '某巨鲸过去5天从Kraken囤积894枚BTC价值1.02亿美元',
        'description': '据Lookonchain监测，某巨鲸地址在过去5天内从Kraken提取了894枚BTC',
        'source': 'Odaily',
        'published_at': '2024-10-28',
        'language': 'zh'
    }
    
    print("原始新闻:")
    print(f"  标题: {test_news['title']}")
    print()
    
    processed = processor.process_single_news(test_news)
    
    print("处理后:")
    print(f"  英文标题: {processed['title']}")
    print(f"  关键词: {processed['keywords']}")
    print(f"  摘要: {processed['summary']}")
    print(f"  Token数: {processed['token_count']}")
    print()
    
    # 测试批量处理
    news_list = [test_news] * 3
    processed_list = processor.process_news_list(news_list)
    
    print("紧凑Prompt:")
    print(processor.generate_compact_prompt(processed_list))
