#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宏观经济指标获取器
"""

import yfinance as yf
from typing import Dict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MacroIndicators:
    """宏观经济指标"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1小时缓存
    
    def get_indicators(self) -> Dict:
        """
        获取宏观指标返回4个维度
        
        Returns:
            {
                'dxy_change': 美元指数变化率(%),
                'sp500_change': 美股变化率(%),
                'vix_level': VIX指数,
                'risk_appetite': 风险偏好(0-100)
            }
        """
        # 检查缓存
        if self._is_cache_valid():
            return self.cache['data']
        
        try:
            # 美元指数
            dxy_change = self._get_ticker_change("DX-Y.NYB", "美元指数")
            
            # S&P 500
            sp500_change = self._get_ticker_change("^GSPC", "S&P500")
            
            # VIX恐慌指数
            vix_level = self._get_vix_level()
            
            # 风险偏好综合指标
            risk_appetite = self._calculate_risk_appetite(sp500_change, vix_level)
            
            result = {
                'dxy_change': dxy_change,
                'sp500_change': sp500_change,
                'vix_level': vix_level,
                'risk_appetite': risk_appetite
            }
            
            # 更新缓存
            self.cache = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"宏观指标获取失败: {e}")
            return {
                'dxy_change': 0,
                'sp500_change': 0,
                'vix_level': 20,
                'risk_appetite': 50
            }
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self.cache:
            return False
        
        elapsed = (datetime.now() - self.cache['timestamp']).total_seconds()
        return elapsed < self.cache_duration
    
    def _get_ticker_change(self, ticker: str, name: str) -> float:
        """获取标的变化率"""
        try:
            data = yf.Ticker(ticker).history(period="5d")
            if len(data) < 2:
                return 0
            
            change = data['Close'].pct_change().iloc[-1] * 100
            return round(change, 4)
        except Exception as e:
            logger.warning(f"{name}获取失败: {e}")
            return 0
    
    def _get_vix_level(self) -> float:
        """获取VIX指数"""
        try:
            vix = yf.Ticker("^VIX").history(period="1d")
            if len(vix) == 0:
                return 20
            return round(vix['Close'].iloc[-1], 2)
        except Exception as e:
            logger.warning(f"VIX获取失败: {e}")
            return 20
    
    def _calculate_risk_appetite(self, sp500_change: float, vix_level: float) -> float:
        """
        计算风险偏好指标 (0-100)
        
        逻辑:
        - S&P500上涨 + VIX低 = 风险偏好高
        - S&P500下跌 + VIX高 = 风险偏好低
        """
        # S&P500贡献（-50到50）
        sp500_score = max(-50, min(50, sp500_change * 10))
        
        # VIX贡献（VIX低风险偏好高，VIX高风险偏好低）
        # VIX正常范围12-30，极端0-80
        vix_score = 50 - (vix_level - 15) * 2  # VIX=15时得分50
        vix_score = max(-50, min(50, vix_score))
        
        # 综合得分（0-100）
        risk_appetite = 50 + (sp500_score + vix_score) / 2
        return round(max(0, min(100, risk_appetite)), 2)
