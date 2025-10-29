#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易策略基类
所有策略都继承这个基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """交易策略基类"""
    
    def __init__(self, name: str):
        """
        初始化策略
        
        Args:
            name: 策略名称
        """
        self.name = name
        self.enabled = True
        self.min_confidence = 70  # 最低置信度要求
    
    @abstractmethod
    def analyze(self, features: List[float], metadata: Dict) -> Dict:
        """
        分析市场并生成信号
        
        Args:
            features: 26维特征向量
            metadata: 元数据（价格、K线等）
        
        Returns:
            {
                'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
                'confidence': 0-100,
                'reason': 'xxx',
                'entry_price': float,
                'stop_loss': float,
                'take_profit': [float, float, float],
                'position_size_ratio': float  # 建议仓位占比
            }
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """返回策略描述"""
        pass
    
    def is_enabled(self) -> bool:
        """策略是否启用"""
        return self.enabled
    
    def set_enabled(self, enabled: bool):
        """设置策略启用状态"""
        self.enabled = enabled
    
    def validate_signal(self, signal: Dict) -> bool:
        """验证信号是否有效"""
        if not signal:
            return False
        
        required_fields = ['signal', 'confidence', 'reason']
        for field in required_fields:
            if field not in signal:
                logger.warning(f"策略 {self.name} 信号缺少字段: {field}")
                return False
        
        if signal['confidence'] < self.min_confidence:
            logger.debug(f"策略 {self.name} 置信度不足: {signal['confidence']}")
            return False
        
        return True
    
    def format_signal(self, signal: Dict) -> str:
        """格式化信号为可读文本"""
        if not signal:
            return "无信号"
        
        text = f"[{self.name}]\n"
        text += f"  信号: {signal['signal']}\n"
        text += f"  置信度: {signal['confidence']:.0f}%\n"
        text += f"  原因: {signal['reason']}\n"
        
        if 'entry_price' in signal:
            text += f"  入场价: ${signal['entry_price']:,.2f}\n"
        
        if 'stop_loss' in signal:
            text += f"  止损: ${signal['stop_loss']:,.2f}\n"
        
        if 'take_profit' in signal and signal['take_profit']:
            text += f"  止盈: ${signal['take_profit'][0]:,.2f} / "
            text += f"${signal['take_profit'][1]:,.2f} / "
            text += f"${signal['take_profit'][2]:,.2f}\n"
        
        return text
