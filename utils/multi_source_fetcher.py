"""
多数据源K线获取模块
支持Binance, CoinGecko, CryptoCompare等数据源
"""

import requests
import pandas as pd
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class MultiSourceDataFetcher:
    """多数据源K线获取器"""
    
    def __init__(self, cryptocompare_key=""):
        self.cryptocompare_key = cryptocompare_key
        self.sources = {
            "binance": self._fetch_binance,
            "coingecko": self._fetch_coingecko,
            "cryptocompare": self._fetch_cryptocompare
        }
    
    def _fetch_binance(self, symbol, interval="5m", limit=100):
        """从Binance获取数据"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if isinstance(data, list):
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = df[col].astype(float)
                
                df['source'] = 'binance'
                logger.info(f"Binance: {len(df)} 条数据")
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'source']]
            
        except Exception as e:
            logger.error(f"Binance获取失败: {e}")
            return None
    
    def _fetch_coingecko(self, symbol, interval="5m", limit=100):
        """从CoinGecko获取数据"""
        try:
            coin_id = symbol.replace("USDT", "").lower()
            if coin_id == "btc":
                coin_id = "bitcoin"
            elif coin_id == "eth":
                coin_id = "ethereum"
            
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": "1",
                "interval": "5minute"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "prices" in data:
                prices = data["prices"]
                volumes = data["total_volumes"]
                
                df = pd.DataFrame({
                    'timestamp': [datetime.fromtimestamp(p[0]/1000) for p in prices],
                    'close': [p[1] for p in prices],
                    'volume': [v[1] for v in volumes]
                })
                
                df['open'] = df['close'].shift(1).fillna(df['close'])
                df['high'] = df[['open', 'close']].max(axis=1) * 1.001
                df['low'] = df[['open', 'close']].min(axis=1) * 0.999
                df['source'] = 'coingecko'
                
                df = df.tail(limit)
                logger.info(f"CoinGecko: {len(df)} 条数据")
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'source']]
            
        except Exception as e:
            logger.error(f"CoinGecko获取失败: {e}")
            return None
    
    def _fetch_cryptocompare(self, symbol, interval="5m", limit=100):
        """从CryptoCompare获取数据"""
        try:
            coin = symbol.replace("USDT", "")
            
            url = "https://min-api.cryptocompare.com/data/v2/histominute"
            params = {
                "fsym": coin,
                "tsym": "USD",
                "limit": limit
            }
            
            if self.cryptocompare_key:
                params["api_key"] = self.cryptocompare_key
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("Response") == "Success":
                prices = data["Data"]["Data"]
                
                df = pd.DataFrame(prices)
                df['timestamp'] = pd.to_datetime(df['time'], unit='s')
                df = df.rename(columns={'volumefrom': 'volume'})
                df['source'] = 'cryptocompare'
                
                logger.info(f"CryptoCompare: {len(df)} 条数据")
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'source']]
            
        except Exception as e:
            logger.error(f"CryptoCompare获取失败: {e}")
            return None
    
    def fetch_from_all_sources(self, symbol, interval="5m", limit=100):
        """并发从所有数据源获取"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            for source_name, fetch_func in self.sources.items():
                future = executor.submit(fetch_func, symbol, interval, limit)
                futures[future] = source_name
            
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    df = future.result()
                    if df is not None and not df.empty:
                        results[source_name] = df
                except Exception as e:
                    logger.error(f"{source_name} 异常: {e}")
        
        return results
    
    def aggregate_and_validate(self, symbol, interval="5m", limit=100):
        """聚合并验证数据"""
        logger.info(f"从多数据源获取 {symbol} 数据...")
        
        all_data = self.fetch_from_all_sources(symbol, interval, limit)
        
        if not all_data:
            logger.error("所有数据源获取失败")
            return None
        
        logger.info(f"成功获取 {len(all_data)} 个数据源")
        
        # 选择最佳数据源（优先Binance）
        if "binance" in all_data:
            best_df = all_data["binance"]
            logger.info("选择 Binance 作为主数据源")
        elif "cryptocompare" in all_data:
            best_df = all_data["cryptocompare"]
            logger.info("选择 CryptoCompare 作为主数据源")
        elif "coingecko" in all_data:
            best_df = all_data["coingecko"]
            logger.info("选择 CoinGecko 作为主数据源")
        else:
            return None
        
        return best_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    fetcher = MultiSourceDataFetcher()
    df = fetcher.aggregate_and_validate("BTCUSDT", limit=50)
    
    if df is not None:
        print(f"\n获取到 {len(df)} 条数据")
        print(df.tail(5))
