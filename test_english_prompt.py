#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试英文Prompt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import config
from models.ai_predictor import DeepSeekPredictor

# 测试数据
mock_kline = """
Time                | Open      | High      | Low       | Close     | Volume
------------------------------------------------------------------------------------------
2024-01-01 10:00 | $50,000.00 | $50,200.00 | $49,800.00 | $50,100.00 |    100.50
2024-01-01 10:01 | $50,100.00 | $50,300.00 | $50,000.00 | $50,250.00 |    120.30
2024-01-01 10:02 | $50,250.00 | $50,400.00 | $50,200.00 | $50,350.00 |    110.20
"""

# 构建英文prompt
prompt = config.PREDICTION_PROMPT_TEMPLATE.format(
    window=5,
    symbol="BTCUSDT",
    current_time="2024-01-01 10:03:00",
    current_price="50,350.00",
    kline_data=mock_kline
)

print("=" * 80)
print("英文Prompt测试")
print("=" * 80)
print("\n生成的Prompt:")
print("-" * 80)
print(prompt)
print("-" * 80)

# 测试DeepSeek
api_key = os.getenv("DEEPSEEK_API_KEY")
if api_key:
    print("\n正在调用 DeepSeek 测试...")
    predictor = DeepSeekPredictor(api_key)
    result = predictor.predict(prompt, temperature=0.3, max_tokens=500)
    
    if result:
        print(f"\n✓ DeepSeek响应成功!")
        print(f"\n模型响应:\n{result}")
        
        # 尝试提取预测
        prediction = predictor.extract_prediction(result)
        if prediction:
            print(f"\n✓ 成功提取预测结果:")
            print(f"  预测价格: ${prediction.get('predicted_price', 'N/A')}")
            print(f"  置信度: {prediction.get('confidence', 'N/A')}%")
            print(f"  方向: {prediction.get('direction', 'N/A')}")
        else:
            print("\n⚠ 未能提取预测结果")
    else:
        print("\n✗ DeepSeek响应失败")
else:
    print("\n⚠ 未配置DEEPSEEK_API_KEY，跳过实际测试")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
