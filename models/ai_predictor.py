#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI预测模块 - 调用Grok, Gemini, DeepSeek进行价格预测
"""

import requests
import json
import time
import logging
import os
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd

# 导入Gemini SDK
try:
    from google import genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    GEMINI_SDK_AVAILABLE = False
    logging.warning("google-genai SDK未安装，Gemini功能将不可用")

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIPredictor:
    """AI价格预测器基类"""
    
    def __init__(self, api_key: str, model_name: str, endpoint: str):
        """
        初始化预测器
        
        Args:
            api_key: API密钥
            model_name: 模型名称
            endpoint: API端点
        """
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = endpoint
        self.headers = self._build_headers()
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头 - 子类可以重写"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def predict(
        self, 
        prompt: str, 
        temperature: float = 0.3, 
        max_tokens: int = 1000
    ) -> Optional[str]:
        """
        发送预测请求 - 子类需要实现
        
        Args:
            prompt: 输入提示词
            temperature: 温度参数（越低越确定）
            max_tokens: 最大token数
            
        Returns:
            模型响应文本，失败返回None
        """
        raise NotImplementedError("子类需要实现此方法")
    
    def extract_prediction(self, response_text: str) -> Optional[Dict]:
        """
        从模型响应中提取预测结果
        
        Args:
            response_text: 模型返回的文本
            
        Returns:
            包含预测价格、置信度和方向的字典
            格式: {"predicted_price": float, "confidence": float, "direction": str}
        """
        try:
            # 尝试查找JSON格式的预测结果
            # 通常在最后一行或者用```json包裹
            
            # 方法1: 查找最后一个JSON对象
            lines = response_text.strip().split('\n')
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        result = json.loads(line)
                        if 'predicted_price' in result:
                            return result
                    except json.JSONDecodeError:
                        continue
            
            # 方法2: 查找```json代码块
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                if end > start:
                    json_str = response_text[start:end].strip()
                    result = json.loads(json_str)
                    if 'predicted_price' in result:
                        return result
            
            # 方法3: 查找任何JSON对象
            import re
            json_pattern = r'\{[^{}]*"predicted_price"[^{}]*\}'
            matches = re.findall(json_pattern, response_text)
            if matches:
                result = json.loads(matches[-1])
                return result
            
            logger.warning(f"无法从响应中提取预测结果: {response_text[:200]}")
            return None
            
        except Exception as e:
            logger.error(f"提取预测结果错误: {e}")
            return None


class GrokPredictor(AIPredictor):
    """Grok预测器"""
    
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            model_name="grok-beta",
            endpoint="https://api.x.ai/v1/chat/completions"
        )
    
    def predict(
        self, 
        prompt: str, 
        temperature: float = 0.3, 
        max_tokens: int = 1000
    ) -> Optional[str]:
        """发送Grok预测请求"""
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional cryptocurrency analyst, expert in technical analysis and price prediction."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.info(f"正在调用 Grok 进行预测...")
            
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                logger.info(f"Grok 预测完成")
                return content
            else:
                logger.error(f"Grok API错误: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Grok 预测错误: {e}")
            return None


class GeminiPredictor(AIPredictor):
    """Gemini预测器 - 使用google-genai SDK"""
    
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            model_name="gemini-2.5-flash",  # 使用gemini-2.5-flash
            endpoint=""  # SDK不需要endpoint
        )
        
        if not GEMINI_SDK_AVAILABLE:
            raise ImportError("需要安装 google-genai: pip install google-genai")
        
        # 初始化Gemini客户端（传入API密钥）
        self.client = genai.Client(api_key=api_key)
    
    def predict(
        self, 
        prompt: str, 
        temperature: float = 0.3, 
        max_tokens: int = 1000
    ) -> Optional[str]:
        """发送Gemini预测请求"""
        try:
            logger.info(f"正在调用 Gemini (gemini-2.5-flash) 进行预测...")
            
            # 使用SDK调用 - 简化版本
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            # 获取响应文本
            result_text = response.text
            
            logger.info(f"Gemini 预测完成")
            return result_text
                
        except Exception as e:
            logger.error(f"Gemini 预测错误: {e}")
            import traceback
            traceback.print_exc()
            return None


class DeepSeekPredictor(AIPredictor):
    """DeepSeek预测器 - 使用OpenAI SDK（支持第三方代理）"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.probex.top/v1", model: str = "deepseek-v3.1"):
        super().__init__(
            api_key=api_key,
            model_name=model,
            endpoint=base_url
        )
        
        # 使用OpenAI SDK初始化DeepSeek客户端
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            logger.info(f"DeepSeek客户端初始化: {base_url} / {model}")
        except ImportError:
            raise ImportError("需要安装 openai: pip install openai")
    
    def predict(
        self, 
        prompt: str, 
        temperature: float = 0.3, 
        max_tokens: int = 1000
    ) -> Optional[str]:
        """发送DeepSeek预测请求"""
        try:
            logger.info(f"正在调用 DeepSeek 进行预测...")
            
            # 使用OpenAI SDK调用
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional cryptocurrency analyst, expert in technical analysis and price prediction."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            # 获取响应内容
            content = response.choices[0].message.content
            logger.info(f"DeepSeek 预测完成")
            return content
                
        except Exception as e:
            logger.error(f"DeepSeek 预测错误: {e}")
            import traceback
            traceback.print_exc()
            return None


class MultiModelPredictor:
    """多模型预测器 - 同时使用多个模型进行预测"""
    
    def __init__(self, api_keys: Dict[str, str]):
        """
        初始化多模型预测器
        
        Args:
            api_keys: 包含各模型API密钥的字典
                     格式: {"grok": "key1", "gemini": "key2", "deepseek": "key3"}
        """
        self.predictors = {}
        
        # 自动初始化所有有有效API密钥的预测器
        if "grok" in api_keys and api_keys["grok"] and api_keys["grok"].strip():
            try:
                self.predictors["grok"] = GrokPredictor(api_keys["grok"])
                logger.info("✓ Grok模型已初始化")
            except Exception as e:
                logger.warning(f"Grok模型初始化失败: {e}")
        
        if "gemini" in api_keys and api_keys["gemini"] and api_keys["gemini"].strip():
            try:
                self.predictors["gemini"] = GeminiPredictor(api_keys["gemini"])
                logger.info("✓ Gemini模型已初始化")
            except Exception as e:
                logger.warning(f"Gemini模型初始化失败: {e}")
        
        if "deepseek" in api_keys and api_keys["deepseek"] and api_keys["deepseek"].strip():
            try:
                self.predictors["deepseek"] = DeepSeekPredictor(api_keys["deepseek"])
                logger.info("✓ DeepSeek模型已初始化")
            except Exception as e:
                logger.warning(f"DeepSeek模型初始化失败: {e}")
        
        if not self.predictors:
            logger.error("没有可用的AI模型！请检查API密钥配置")
        else:
            logger.info(f"总共初始化了 {len(self.predictors)} 个预测模型: {list(self.predictors.keys())}")
    
    def predict_all(
        self, 
        prompt: str, 
        temperature: float = 0.3, 
        max_tokens: int = 1000
    ) -> Dict[str, Optional[Dict]]:
        """
        使用所有模型进行预测
        
        Args:
            prompt: 预测提示词
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            字典，键为模型名称，值为预测结果
            格式: {
                "grok": {"predicted_price": 50000, "confidence": 75, "direction": "up"},
                "gemini": {...},
                "deepseek": {...}
            }
        """
        results = {}
        
        for model_name, predictor in self.predictors.items():
            try:
                # 调用预测
                response = predictor.predict(prompt, temperature, max_tokens)
                
                if response:
                    # 提取预测结果
                    prediction = predictor.extract_prediction(response)
                    results[model_name] = prediction
                    
                    if prediction:
                        logger.info(
                            f"{model_name} 预测: ${prediction.get('predicted_price', 'N/A')} "
                            f"(置信度: {prediction.get('confidence', 'N/A')}%)"
                        )
                    else:
                        logger.warning(f"{model_name} 未能提取有效预测")
                else:
                    results[model_name] = None
                
                # 避免请求过快
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"{model_name} 预测失败: {e}")
                results[model_name] = None
        
        return results
    
    def predict_multiple_windows(
        self,
        prompt_template: str,
        windows: List[int],
        symbol: str,
        current_price: float,
        kline_data: str
    ) -> pd.DataFrame:
        """
        对多个时间窗口进行预测
        
        Args:
            prompt_template: 提示词模板
            windows: 时间窗口列表（分钟）
            symbol: 交易对符号
            current_price: 当前价格
            kline_data: K线数据文本
            
        Returns:
            预测结果DataFrame
        """
        all_predictions = []
        
        for window in windows:
            logger.info(f"\n{'='*60}")
            logger.info(f"预测 {symbol} 未来 {window} 分钟的价格")
            logger.info(f"{'='*60}")
            
            # 构建提示词
            prompt = prompt_template.format(
                window=window,
                symbol=symbol,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                current_price=f"{current_price:,.2f}",
                kline_data=kline_data
            )
            
            # 所有模型预测
            predictions = self.predict_all(prompt)
            
            # 构建结果行
            row = {
                "symbol": symbol,
                "window_minutes": window,
                "current_price": current_price,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 添加各模型的预测
            for model_name in ["grok", "gemini", "deepseek"]:
                if model_name in predictions and predictions[model_name]:
                    pred = predictions[model_name]
                    row[f"{model_name}_price"] = pred.get("predicted_price", None)
                    row[f"{model_name}_confidence"] = pred.get("confidence", None)
                    row[f"{model_name}_direction"] = pred.get("direction", None)
                else:
                    row[f"{model_name}_price"] = None
                    row[f"{model_name}_confidence"] = None
                    row[f"{model_name}_direction"] = None
            
            all_predictions.append(row)
            
            # 避免请求过快
            time.sleep(2)
        
        # 转换为DataFrame
        df = pd.DataFrame(all_predictions)
        
        return df


# ==================== 测试代码 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("测试 AI 预测模块")
    print("=" * 60)
    
    # 注意: 需要设置真实的API密钥才能运行测试
    test_api_keys = {
        "grok": "test-key",
        "gemini": "test-key",
        "deepseek": "test-key"
    }
    
    # 创建多模型预测器
    predictor = MultiModelPredictor(test_api_keys)
    
    # 模拟K线数据
    mock_kline = """
时间                  | 开盘价    | 最高价    | 最低价    | 收盘价    | 成交量
----------------------------------------------------------------------------------
2024-01-01 10:00 | $50,000.00 | $50,200.00 | $49,800.00 | $50,100.00 |    100.50
2024-01-01 10:01 | $50,100.00 | $50,300.00 | $50,000.00 | $50,250.00 |    120.30
2024-01-01 10:02 | $50,250.00 | $50,400.00 | $50,200.00 | $50,350.00 |    110.20
    """
    
    # 测试提示词
    test_prompt = f"""
你是一个专业的加密货币价格分析师。请根据以下K线数据，预测未来5分钟的价格。

当前币种: BTCUSDT
当前价格: $50,350.00

最近K线数据:
{mock_kline}

请输出JSON格式的预测: {{"predicted_price": 价格, "confidence": 置信度, "direction": "方向"}}
    """
    
    print("\n测试预测功能（需要真实API密钥）:")
    print("如果没有API密钥，此测试将跳过\n")
    
    # 这里只是演示结构，实际测试需要真实API密钥
    # results = predictor.predict_all(test_prompt)
    # print(f"预测结果: {results}")
    
    print("\n" + "=" * 60)
    print("模块加载成功! 设置API密钥后即可使用")
    print("=" * 60)
