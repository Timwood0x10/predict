#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单簿分析器 - 分析买卖盘深度
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OrderbookAnalyzer:
    """订单簿深度分析"""
    
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher
    
    def analyze(self, symbol: str, depth: int = 20) -> Dict:
        """
        分析订单簿返回3个维度
        
        Args:
            symbol: 交易对
            depth: 深度档位
            
        Returns:
            {
                'orderbook_imbalance': -1到1,
                'support_strength': 0到100,
                'resistance_strength': 0到100
            }
        """
        try:
            import requests
            # 直接调用Binance API
            url = f"{self.data_fetcher.base_url}/api/v3/depth"
            params = {'symbol': symbol, 'limit': depth}
            response = requests.get(url, params=params)
            orderbook = response.json()
            
            bids = orderbook['bids']  # 买单 [[price, quantity], ...]
            asks = orderbook['asks']  # 卖单
            
            # 1. 买卖盘失衡度
            imbalance = self._calculate_imbalance(bids, asks)
            
            # 2. 支撑强度（买盘）
            support = self._calculate_support_strength(bids)
            
            # 3. 阻力强度（卖盘）
            resistance = self._calculate_resistance_strength(asks)
            
            return {
                'orderbook_imbalance': imbalance,
                'support_strength': support,
                'resistance_strength': resistance
            }
            
        except Exception as e:
            logger.error(f"订单簿分析失败: {e}")
            return {
                'orderbook_imbalance': 0,
                'support_strength': 50,
                'resistance_strength': 50
            }
    
    def _calculate_imbalance(self, bids, asks) -> float:
        """计算买卖盘失衡度 (-1到1)"""
        bid_volume = sum([float(b[1]) for b in bids])
        ask_volume = sum([float(a[1]) for a in asks])
        
        total = bid_volume + ask_volume
        if total == 0:
            return 0
        
        imbalance = (bid_volume - ask_volume) / total
        return max(-1, min(1, imbalance))  # 限制在[-1, 1]
    
    def _calculate_support_strength(self, bids) -> float:
        """计算支撑强度 (0到100)"""
        if not bids:
            return 50
        
        volumes = [float(b[1]) for b in bids]
        avg_volume = sum(volumes) / len(volumes)
        
        # 识别大单墙（>平均10倍）
        big_walls = [v for v in volumes if v > avg_volume * 10]
        
        # 支撑强度：大单墙数量和总体买盘深度
        wall_score = min(len(big_walls) * 20, 50)  # 最多50分
        depth_score = min(sum(volumes) / (avg_volume * len(volumes)) * 50, 50)  # 最多50分
        
        return wall_score + depth_score
    
    def _calculate_resistance_strength(self, asks) -> float:
        """计算阻力强度 (0到100)"""
        if not asks:
            return 50
        
        volumes = [float(a[1]) for a in asks]
        avg_volume = sum(volumes) / len(volumes)
        
        # 识别大单墙（>平均10倍）
        big_walls = [v for v in volumes if v > avg_volume * 10]
        
        # 阻力强度：大单墙数量和总体卖盘深度
        wall_score = min(len(big_walls) * 20, 50)
        depth_score = min(sum(volumes) / (avg_volume * len(volumes)) * 50, 50)
        
        return wall_score + depth_score
