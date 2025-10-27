#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型模块初始化文件
"""

from .ai_predictor import (
    AIPredictor,
    GrokPredictor,
    GeminiPredictor,
    DeepSeekPredictor,
    MultiModelPredictor
)

__all__ = [
    'AIPredictor',
    'GrokPredictor',
    'GeminiPredictor',
    'DeepSeekPredictor',
    'MultiModelPredictor'
]
