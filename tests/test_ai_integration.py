#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI集成测试 - 演示AI如何调用决策引擎

包含:
1. 直接调用方式
2. API调用方式
3. AI助手集成示例
"""

import sys
import os
import json
import requests
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_enhanced import EnhancedTradingSystem


def test_direct_call():
    """测试1: 直接调用决策引擎"""
    print("="*80)
    print("测试1: 直接调用决策引擎")
    print("="*80)
    
    # 创建系统实例
    system = EnhancedTradingSystem(account_balance=10000, risk_percent=0.015)
    
    # 执行分析
    success = system.run_single_analysis("BTCUSDT")
    
    if success:
        print("\n✅ 分析成功！")
        
        # 获取JSON格式结果
        print("\n" + "="*80)
        print("JSON格式结果（供AI解析）:")
        print("="*80)
        print(system.get_latest_decision_json())
        
        # 获取文本摘要
        print("\n" + "="*80)
        print("文本摘要（供AI阅读）:")
        print("="*80)
        print(system.get_latest_decision_summary())
    else:
        print("\n❌ 分析失败")


def test_api_call():
    """测试2: 通过API调用（需要先启动API服务器）"""
    print("\n\n" + "="*80)
    print("测试2: 通过API调用")
    print("="*80)
    
    base_url = "http://localhost:5000"
    
    # 1. 健康检查
    print("\n1️⃣ 健康检查:")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"  状态: {response.json()}")
    except Exception as e:
        print(f"  ❌ API服务器未启动: {e}")
        print(f"  💡 请先运行: python main_enhanced.py --mode api")
        return
    
    # 2. 执行分析
    print("\n2️⃣ 执行分析:")
    try:
        response = requests.post(
            f"{base_url}/api/analyze",
            json={"symbol": "BTCUSDT"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ 分析成功")
            print(f"  决策: {result['data']['decision']['action']}")
            print(f"  置信度: {result['data']['decision']['confidence']}%")
        else:
            print(f"  ❌ 分析失败: {response.text}")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
    
    # 3. 获取决策
    print("\n3️⃣ 获取最新决策:")
    try:
        response = requests.get(f"{base_url}/api/decision", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            decision = result['data']['decision']
            print(f"  动作: {decision['action']}")
            print(f"  置信度: {decision['confidence']}%")
            print(f"  原因: {decision['reason']}")
        else:
            print(f"  ❌ 获取失败: {response.text}")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
    
    # 4. 获取摘要
    print("\n4️⃣ 获取决策摘要:")
    try:
        response = requests.get(f"{base_url}/api/summary", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(result['summary'])
        else:
            print(f"  ❌ 获取失败: {response.text}")
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")


def simulate_ai_assistant():
    """测试3: 模拟AI助手调用"""
    print("\n\n" + "="*80)
    print("测试3: 模拟AI助手集成")
    print("="*80)
    
    print("""
AI助手可以这样集成决策引擎:

示例1: 用户询问 "现在应该买比特币吗？"

AI助手的处理流程:
1. 识别用户意图 → 需要交易建议
2. 调用决策引擎API
3. 解析返回结果
4. 用自然语言回答用户

代码示例:
```python
import requests

def get_trading_advice(symbol="BTCUSDT"):
    # 执行分析
    response = requests.post(
        "http://localhost:5000/api/analyze",
        json={"symbol": symbol}
    )
    
    if response.status_code == 200:
        decision = response.json()['data']['decision']
        
        # 根据决策生成自然语言回答
        if decision['action'] == 'BUY':
            return f"根据分析，现在是买入的好时机！置信度{decision['confidence']}%。原因：{decision['reason']}"
        elif decision['action'] == 'SELL':
            return f"建议卖出或观望。置信度{decision['confidence']}%。原因：{decision['reason']}"
        else:
            return f"建议暂时观望。原因：{decision['reason']}"
    else:
        return "抱歉，无法获取交易建议。"

# AI回答用户
answer = get_trading_advice("BTCUSDT")
print(answer)
```

示例2: 用户询问 "帮我分析一下以太坊"

AI助手可以:
1. 调用 POST /api/analyze {"symbol": "ETHUSDT"}
2. 获取完整分析报告
3. 提取关键信息
4. 用图表或文字展示给用户

示例3: 用户询问 "我有1000U，用100x杠杆安全吗？"

AI助手可以:
1. 识别到杠杆风险问题
2. 调用杠杆计算器
3. 展示风险数据
4. 给出专业建议

代码示例:
```python
from test_leverage import LeverageCalculator

calc = LeverageCalculator(capital=1000, leverage=100)
plan = calc.calculate_position(entry_price=50000, stop_loss_percent=0.005)

if plan['capital_loss_percent'] > 50:
    return "⚠️ 警告：100x杠杆风险极高！价格波动0.5%就会损失50%本金，不建议使用。建议使用5-10x杠杆。"
```
""")
    
    print("\n💡 AI助手集成的优势:")
    print("  ✅ 实时数据分析")
    print("  ✅ 科学决策依据")
    print("  ✅ 自动风险控制")
    print("  ✅ 24/7 不间断服务")
    print("  ✅ 多语言自然交互")


def create_ai_integration_examples():
    """创建AI集成示例代码"""
    print("\n\n" + "="*80)
    print("生成AI集成示例代码")
    print("="*80)
    
    examples = {
        "example_1_simple.py": """#!/usr/bin/env python3
'''简单示例: AI助手获取交易建议'''

import requests

def ai_get_trading_advice(symbol="BTCUSDT"):
    '''AI助手函数: 获取交易建议'''
    try:
        # 调用决策引擎API
        response = requests.post(
            "http://localhost:5000/api/analyze",
            json={"symbol": symbol},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            decision = data['decision']
            
            # 生成自然语言回答
            advice = f"📊 {symbol} 交易分析\\n\\n"
            advice += f"🎯 建议: {decision['action']}\\n"
            advice += f"📈 置信度: {decision['confidence']:.0f}%\\n"
            advice += f"💡 原因: {decision['reason']}\\n"
            
            # 如果有仓位信息
            if data['position']:
                pos = data['position']
                advice += f"\\n💰 仓位建议:\\n"
                advice += f"  - 仓位: {pos['position_size']:.6f} BTC\\n"
                advice += f"  - 止损: ${pos['stop_loss']:,.2f}\\n"
                advice += f"  - 止盈: ${pos['take_profit_1']:,.2f}\\n"
            
            return advice
        else:
            return "❌ 无法获取分析结果"
            
    except Exception as e:
        return f"❌ 错误: {str(e)}"

# 使用示例
if __name__ == "__main__":
    print(ai_get_trading_advice("BTCUSDT"))
""",
        
        "example_2_chatbot.py": """#!/usr/bin/env python3
'''示例2: AI聊天机器人集成'''

import requests

class TradingChatbot:
    '''交易AI聊天机器人'''
    
    def __init__(self, api_base="http://localhost:5000"):
        self.api_base = api_base
    
    def process_user_query(self, user_input: str) -> str:
        '''处理用户查询'''
        
        # 识别意图
        if "买" in user_input or "购买" in user_input:
            return self.handle_buy_query(user_input)
        elif "卖" in user_input:
            return self.handle_sell_query(user_input)
        elif "分析" in user_input or "建议" in user_input:
            return self.handle_analysis_query(user_input)
        elif "风险" in user_input or "杠杆" in user_input:
            return self.handle_risk_query(user_input)
        else:
            return "我可以帮你分析交易机会、评估风险。你想了解什么？"
    
    def handle_buy_query(self, query: str) -> str:
        '''处理买入询问'''
        symbol = self.extract_symbol(query)
        
        # 调用API分析
        response = requests.post(
            f"{self.api_base}/api/analyze",
            json={"symbol": symbol}
        )
        
        if response.status_code == 200:
            decision = response.json()['data']['decision']
            
            if decision['action'] == 'BUY':
                return f"✅ 现在是买入{symbol}的好时机！\\n置信度: {decision['confidence']:.0f}%\\n原因: {decision['reason']}"
            elif decision['action'] == 'SELL':
                return f"⚠️ 建议不要买入{symbol}。\\n原因: {decision['reason']}"
            else:
                return f"🤔 建议观望{symbol}。\\n原因: {decision['reason']}"
        
        return "抱歉，无法获取分析结果。"
    
    def handle_analysis_query(self, query: str) -> str:
        '''处理分析请求'''
        symbol = self.extract_symbol(query)
        
        response = requests.get(f"{self.api_base}/api/summary")
        
        if response.status_code == 200:
            return response.json()['summary']
        
        return "抱歉，无法获取分析报告。"
    
    def handle_risk_query(self, query: str) -> str:
        '''处理风险询问'''
        return "杠杆交易风险极高！\\n建议:\\n- 新手: 5-10x\\n- 进阶: 10-20x\\n- 专业: 20-50x\\n避免使用100x杠杆！"
    
    def extract_symbol(self, query: str) -> str:
        '''从查询中提取交易对'''
        if "BTC" in query.upper() or "比特币" in query:
            return "BTCUSDT"
        elif "ETH" in query.upper() or "以太坊" in query:
            return "ETHUSDT"
        else:
            return "BTCUSDT"  # 默认

# 使用示例
if __name__ == "__main__":
    bot = TradingChatbot()
    
    # 模拟对话
    queries = [
        "现在应该买比特币吗？",
        "帮我分析一下以太坊",
        "100倍杠杆安全吗？"
    ]
    
    for query in queries:
        print(f"\\n用户: {query}")
        print(f"AI: {bot.process_user_query(query)}")
""",
        
        "example_3_telegram_bot.py": """#!/usr/bin/env python3
'''示例3: Telegram机器人集成'''

# 需要安装: pip install python-telegram-bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

TELEGRAM_TOKEN = "your_telegram_bot_token"
API_BASE = "http://localhost:5000"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''处理 /start 命令'''
    await update.message.reply_text(
        "你好！我是加密货币交易助手🤖\\n\\n"
        "我可以帮你:\\n"
        "- /analyze BTC - 分析比特币\\n"
        "- /summary - 获取最新决策\\n"
        "- /risk - 风险教育\\n"
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''处理 /analyze 命令'''
    # 获取交易对参数
    symbol = context.args[0] + "USDT" if context.args else "BTCUSDT"
    
    await update.message.reply_text(f"正在分析 {symbol}，请稍候...")
    
    try:
        # 调用API
        response = requests.post(
            f"{API_BASE}/api/analyze",
            json={"symbol": symbol},
            timeout=60
        )
        
        if response.status_code == 200:
            decision = response.json()['data']['decision']
            
            message = f"📊 {symbol} 分析结果\\n\\n"
            message += f"🎯 建议: {decision['action']}\\n"
            message += f"📈 置信度: {decision['confidence']:.0f}%\\n"
            message += f"💡 {decision['reason']}\\n"
            
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ 分析失败")
            
    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''处理 /summary 命令'''
    try:
        response = requests.get(f"{API_BASE}/api/summary")
        
        if response.status_code == 200:
            summary = response.json()['summary']
            await update.message.reply_text(summary)
        else:
            await update.message.reply_text("❌ 无法获取摘要")
            
    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

def main():
    '''启动Telegram机器人'''
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("summary", summary))
    
    print("Telegram机器人启动...")
    app.run_polling()

if __name__ == "__main__":
    main()
"""
    }
    
    # 保存示例代码
    examples_dir = "ai_integration_examples"
    os.makedirs(examples_dir, exist_ok=True)
    
    for filename, code in examples.items():
        filepath = os.path.join(examples_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"  ✅ 已生成: {filepath}")
    
    print(f"\n💡 AI集成示例已保存到 {examples_dir}/ 目录")


def main():
    """主函数"""
    print("="*80)
    print("🤖 AI集成测试套件")
    print("="*80)
    
    import argparse
    parser = argparse.ArgumentParser(description='AI集成测试')
    parser.add_argument('--test', type=str, choices=['direct', 'api', 'simulate', 'examples', 'all'],
                        default='all', help='测试类型')
    args = parser.parse_args()
    
    if args.test in ['direct', 'all']:
        test_direct_call()
    
    if args.test in ['api', 'all']:
        test_api_call()
    
    if args.test in ['simulate', 'all']:
        simulate_ai_assistant()
    
    if args.test in ['examples', 'all']:
        create_ai_integration_examples()
    
    print("\n" + "="*80)
    print("✅ 测试完成！")
    print("="*80)


if __name__ == "__main__":
    main()
