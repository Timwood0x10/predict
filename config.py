#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - 包含所有API密钥和系统配置
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ==================== API配置 ====================
# 加密货币数据API (使用Binance公开API，无需密钥)
BINANCE_API_BASE = "https://api.binance.com"

# AI模型API密钥 (从.env文件读取)
API_KEYS = {
    "grok": os.getenv("GROK_API_KEY", ""),
    "gemini": os.getenv("GEMINI_API_KEY", ""),
    "deepseek": os.getenv("DEEPSEEK_API_KEY", "")
}

# API端点
API_ENDPOINTS = {
    "grok": "https://api.x.ai/v1/chat/completions",  # Grok API
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",  # Gemini API
    "deepseek": "https://api.deepseek.com"  # DeepSeek API
}

# ==================== 加密货币配置 ====================
# 交易对列表
SYMBOLS = ["BTCUSDT", "ETHUSDT"]

# K线时间间隔 (Binance格式)
KLINE_INTERVALS = {
    "1m": "1m",    # 1分钟
    "3m": "3m",    # 3分钟
    "5m": "5m",    # 5分钟
    "15m": "15m"   # 15分钟
}

# 获取的K线数量 (最近N根K线)
KLINE_LIMIT = 100  # 最近100根K线

# ==================== 预测配置 ====================
# 预测时间窗口 (分钟)
PREDICTION_WINDOWS: List[int] = [3, 5, 8, 10, 12, 15, 30]

# ==================== 数据存储配置 ====================
# 数据目录
DATA_DIR = "data"
LOGS_DIR = "logs"

# CSV文件路径
KLINE_DATA_FILE = f"{DATA_DIR}/kline_data.csv"
PREDICTIONS_FILE = f"{DATA_DIR}/predictions.csv"
COMPARISON_FILE = f"{DATA_DIR}/model_comparison.csv"

# ==================== 系统配置 ====================
# 请求超时时间 (秒)
REQUEST_TIMEOUT = 30

# 重试次数
MAX_RETRIES = 3

# 请求间隔 (秒，避免频率限制)
REQUEST_DELAY = 1

# 日志级别
LOG_LEVEL = "INFO"

# ==================== Prompt模板 ====================
PREDICTION_PROMPT_TEMPLATE = """
You are a professional cryptocurrency price analyst. Based on the following candlestick data, predict the price in {window} minutes.

Current Symbol: {symbol}
Current Time: {current_time}
Current Price: ${current_price}

Recent 15-minute candlestick data:
{kline_data}

Data explanation:
- Time: Candlestick start time
- Open: Opening price
- High: Highest price in the period
- Low: Lowest price in the period
- Close: Closing price
- Volume: Trading volume

Please analyze and predict:
1. Current price trend (upward/downward/sideways)
2. Key support and resistance levels
3. Volume change trend
4. Price prediction for next {window} minutes

**IMPORTANT**: Output ONLY the JSON result in the last line:
{{"predicted_price": your_predicted_price, "confidence": confidence_0_to_100, "direction": "up/down/stable"}}

Output ONLY JSON, no other text.
"""

# ==================== 模型配置 ====================
MODEL_CONFIGS = {
    "grok": {
        "model": "grok-4",
        "temperature": 0.3,
        "max_tokens": 1000
    },
    "gemini": {
        "model": "gemini-flash-latest",
        "temperature": 0.3,
        "max_output_tokens": 1000
    },
    "deepseek": {
        "model": "deepseek-chat",
        "temperature": 0.3,
        "max_tokens": 1000
    }
}

# ==================== 辅助函数 ====================
def validate_config():
    """验证配置是否完整"""
    # 检查目录
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # 检查API密钥
    configured_models = []
    missing_models = []
    
    for model, key in API_KEYS.items():
        if key and key.strip():
            configured_models.append(model.upper())
        else:
            missing_models.append(model.upper())
    
    # 显示配置状态
    print("=" * 60)
    print("API密钥配置状态:")
    print("=" * 60)
    
    if configured_models:
        print(f"✓ 已配置的模型: {', '.join(configured_models)}")
    
    if missing_models:
        print(f"⚠ 未配置的模型: {', '.join(missing_models)}")
        print("\n提示: 在项目根目录创建 .env 文件并添加:")
        for model in missing_models:
            print(f"   {model}_API_KEY=your-api-key-here")
    
    print("=" * 60)
    
    # 至少需要一个模型配置
    if not configured_models:
        print("\n❌ 错误: 至少需要配置一个AI模型的API密钥")
        print("\n请在 .env 文件中设置至少一个API密钥:")
        print("   DEEPSEEK_API_KEY=your-key")
        print("   GEMINI_API_KEY=your-key")
        return False
    
    return True


if __name__ == "__main__":
    print("配置验证:")
    if validate_config():
        print("✓ 配置完整")
    else:
        print("✗ 配置不完整")
