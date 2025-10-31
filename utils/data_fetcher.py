#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取模块 - 从Binance获取实时K线数据
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BinanceDataFetcher:
    """Binance数据获取器 - 获取实时K线数据"""
    
    def __init__(self, base_url: str = "https://api.binance.com"):
        """
        初始化数据获取器
        
        Args:
            base_url: Binance API基础URL
        """
        self.base_url = base_url
        self.klines_endpoint = f"{base_url}/api/v3/klines"
        
    def fetch_klines(
        self, 
        symbol: str, 
        interval: str = "1m", 
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对符号，如 "BTCUSDT"
            interval: K线间隔，如 "1m", "5m", "15m"
            limit: 获取的K线数量，默认100
            
        Returns:
            包含K线数据的DataFrame，如果失败返回None
            
        DataFrame列说明:
            - open_time: 开盘时间
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - close_time: 收盘时间
            - quote_volume: 成交额
            - trades: 成交笔数
            - taker_buy_base: 主动买入成交量
            - taker_buy_quote: 主动买入成交额
        """
        try:
            # 构造请求参数
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            logger.info(f"正在获取 {symbol} 的 {interval} K线数据，数量: {limit}")
            
            # 发送请求
            response = requests.get(
                self.klines_endpoint,
                params=params,
                timeout=10
            )
            
            # 检查响应
            if response.status_code != 200:
                logger.error(f"API请求失败: {response.status_code} - {response.text}")
                return None
            
            # 解析数据
            klines = response.json()
            
            if not klines:
                logger.warning(f"未获取到 {symbol} 的数据")
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # 数据类型转换
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # 价格和成交量转为浮点数
            price_columns = ['open', 'high', 'low', 'close', 'volume', 
                           'quote_volume', 'taker_buy_base', 'taker_buy_quote']
            for col in price_columns:
                df[col] = df[col].astype(float)
            
            df['trades'] = df['trades'].astype(int)
            
            # 删除不需要的列
            df.drop('ignore', axis=1, inplace=True)
            
            logger.info(f"成功获取 {len(df)} 条 {symbol} K线数据")
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求错误: {e}")
            return None
        except Exception as e:
            logger.error(f"数据获取错误: {e}")
            return None
    
    def fetch_recent_klines(
        self, 
        symbol: str, 
        minutes: int = 15
    ) -> Optional[pd.DataFrame]:
        """
        获取最近N分钟的1分钟K线数据
        
        Args:
            symbol: 交易对符号
            minutes: 最近的分钟数，默认15分钟
            
        Returns:
            最近N分钟的K线DataFrame
        """
        # 直接获取N分钟的数据，不进行时间过滤
        # Binance API返回的就是最新的K线，按时间倒序
        df = self.fetch_klines(symbol, interval="1m", limit=minutes)
        
        if df is None:
            return None
        
        logger.info(f"获取最近 {minutes} 分钟的 {len(df)} 条K线数据")
        
        return df
    
    def fetch_multi_symbols(
        self, 
        symbols: List[str], 
        interval: str = "1m", 
        limit: int = 100
    ) -> Dict[str, pd.DataFrame]:
        """
        批量获取多个交易对的K线数据
        
        Args:
            symbols: 交易对列表
            interval: K线间隔
            limit: 每个交易对的K线数量
            
        Returns:
            字典，键为交易对符号，值为K线DataFrame
        """
        result = {}
        
        for symbol in symbols:
            df = self.fetch_klines(symbol, interval, limit)
            
            if df is not None:
                result[symbol] = df
            
            # 避免请求过于频繁
            time.sleep(0.5)
        
        logger.info(f"成功获取 {len(result)}/{len(symbols)} 个交易对的数据")
        
        return result
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        获取当前价格（最新成交价）
        
        Args:
            symbol: 交易对符号
            
        Returns:
            当前价格，如果失败返回None
        """
        try:
            endpoint = f"{self.base_url}/api/v3/ticker/price"
            params = {"symbol": symbol}
            
            response = requests.get(endpoint, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                logger.info(f"{symbol} 当前价格: ${price:,.2f}")
                return price
            else:
                logger.error(f"获取价格失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取价格错误: {e}")
            return None
    
    def save_to_csv(
        self, 
        data: Dict[str, pd.DataFrame], 
        filepath: str
    ) -> bool:
        """
        将K线数据保存到CSV文件
        
        Args:
            data: 字典，键为交易对，值为DataFrame
            filepath: CSV文件路径
            
        Returns:
            是否保存成功
        """
        try:
            # 合并所有交易对的数据
            all_data = []
            
            for symbol, df in data.items():
                df_copy = df.copy()
                df_copy['symbol'] = symbol
                all_data.append(df_copy)
            
            if not all_data:
                logger.warning("没有数据可保存")
                return False
            
            # 合并DataFrame
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # 重新排列列顺序
            columns_order = ['symbol', 'open_time', 'open', 'high', 'low', 
                           'close', 'volume', 'close_time', 'quote_volume', 
                           'trades', 'taker_buy_base', 'taker_buy_quote']
            combined_df = combined_df[columns_order]
            
            # 保存到CSV
            combined_df.to_csv(filepath, index=False)
            
            logger.info(f"数据已保存到: {filepath}")
            logger.info(f"总共保存 {len(combined_df)} 条记录")
            
            return True
            
        except Exception as e:
            logger.error(f"保存CSV错误: {e}")
            return False


def format_klines_for_prompt(df: pd.DataFrame, limit: int = 15) -> str:
    """
    将K线数据格式化为适合AI模型的文本格式（英文）
    
    Args:
        df: K线DataFrame
        limit: 显示最近的N条数据
        
    Returns:
        格式化后的文本（英文）
    """
    if df is None or len(df) == 0:
        return "No data"
    
    # 只取最近的N条
    df_recent = df.tail(limit).copy()
    
    # 格式化输出（英文表头）
    lines = []
    lines.append("Time                | Open      | High      | Low       | Close     | Volume")
    lines.append("-" * 90)
    
    for _, row in df_recent.iterrows():
        lines.append(
            f"{row['open_time'].strftime('%Y-%m-%d %H:%M')} | "
            f"${row['open']:>8,.2f} | "
            f"${row['high']:>8,.2f} | "
            f"${row['low']:>8,.2f} | "
            f"${row['close']:>8,.2f} | "
            f"{row['volume']:>10,.2f}"
        )
    
    return "\n".join(lines)


# ==================== 测试代码 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("测试 Binance 数据获取模块")
    print("=" * 60)
    
    # 创建数据获取器
    fetcher = BinanceDataFetcher()
    
    # 测试1: 获取BTC当前价格
    print("\n[测试1] 获取BTC当前价格")
    btc_price = fetcher.get_current_price("BTCUSDT")
    
    # 测试2: 获取最近15分钟的BTC K线数据
    print("\n[测试2] 获取BTC最近15分钟K线")
    btc_klines = fetcher.fetch_recent_klines("BTCUSDT", minutes=15)
    
    if btc_klines is not None:
        print(f"\n获取到 {len(btc_klines)} 条数据")
        print("\n最近5条K线:")
        print(btc_klines[['open_time', 'open', 'high', 'low', 'close', 'volume']].tail())
    
    # 测试3: 批量获取BTC和ETH数据
    print("\n[测试3] 批量获取BTC和ETH数据")
    multi_data = fetcher.fetch_multi_symbols(["BTCUSDT", "ETHUSDT"], limit=20)
    
    for symbol, df in multi_data.items():
        print(f"\n{symbol}: {len(df)} 条数据")
    
    # 测试4: 保存到CSV
    print("\n[测试4] 保存数据到CSV")
    if multi_data:
        fetcher.save_to_csv(multi_data, "test_klines.csv")
    
    # 测试5: 格式化为Prompt
    print("\n[测试5] 格式化为AI Prompt")
    if btc_klines is not None:
        formatted = format_klines_for_prompt(btc_klines, limit=10)
        print(formatted)
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

    def get_futures_open_interest(self, symbol: str) -> dict:
        """
        获取期货未平仓合约(OI)数据
        
        Returns:
            {
                'oi_change': OI变化率(%),
                'funding_trend': 资金费率趋势(-1到1)
            }
        """
        try:
            # 获取当前OI
            oi_data = self.futures_client.futures_open_interest(symbol=symbol)
            current_oi = float(oi_data['openInterest'])
            
            # 获取历史OI计算变化率（简化：与24小时前对比）
            # 实际应该获取历史数据，这里简化处理
            oi_change = 0  # 需要历史数据才能计算，暂时返回0
            
            # 获取资金费率
            funding_rate = self._get_funding_rate_trend(symbol)
            
            return {
                'oi_change': oi_change,
                'funding_trend': funding_rate
            }
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"期货OI获取失败: {e}")
            return {
                'oi_change': 0,
                'funding_trend': 0
            }
    
    def _get_funding_rate_trend(self, symbol: str) -> float:
        """
        计算资金费率趋势 (-1到1)
        
        逻辑:
        - 连续正费率 -> 趋势为正
        - 连续负费率 -> 趋势为负
        """
        try:
            # 获取最近资金费率历史
            funding_history = self.futures_client.futures_funding_rate(
                symbol=symbol,
                limit=8  # 最近8次（约1天）
            )
            
            if not funding_history:
                return 0
            
            # 计算正负费率比例
            rates = [float(f['fundingRate']) for f in funding_history]
            positive_count = sum(1 for r in rates if r > 0)
            negative_count = sum(1 for r in rates if r < 0)
            
            total = len(rates)
            if total == 0:
                return 0
            
            # 趋势：正费率占比 - 负费率占比
            trend = (positive_count - negative_count) / total
            return round(trend, 4)
            
        except Exception as e:
            return 0
    
    def get_order_book(self, symbol: str, limit: int = 20) -> dict:
        """获取订单簿"""
        endpoint = f"{self.base_url}/api/v3/depth"
        params = {'symbol': symbol, 'limit': limit}
        response = requests.get(endpoint, params=params)
        return response.json()
    
    def get_futures_open_interest(self, symbol: str) -> dict:
        """
        获取期货OI和资金费率
        Returns: {'oi_change': float, 'funding_trend': float}
        """
        try:
            # 资金费率历史
            endpoint = f"{self.base_url}/fapi/v1/fundingRate"
            params = {'symbol': symbol, 'limit': 8}
            response = requests.get(endpoint, params=params)
            funding_history = response.json()
            
            # 计算资金费率趋势
            if funding_history:
                rates = [float(f['fundingRate']) for f in funding_history]
                positive = sum(1 for r in rates if r > 0)
                negative = sum(1 for r in rates if r < 0)
                trend = (positive - negative) / len(rates) if rates else 0
            else:
                trend = 0
            
            return {'oi_change': 0, 'funding_trend': round(trend, 4)}
        except Exception as e:
            logger.warning(f"期货数据获取失败: {e}")
            return {'oi_change': 0, 'funding_trend': 0}
