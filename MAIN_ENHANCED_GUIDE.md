# 🚀 增强版主程序使用指南

> 集成决策引擎，让AI能直接调用的完整交易系统

---

## 📋 概述

`main_enhanced.py` 是原 `main.py` 的增强版本，**完全集成**了决策引擎和26维特征分析，提供三种运行模式和API接口，让AI助手可以直接调用。

### 🆕 相比原版的改进

| 功能 | 原版 main.py | 增强版 main_enhanced.py |
|------|-------------|------------------------|
| 数据获取 | ✅ Binance K线 | ✅ 多源数据（Gas、新闻、情绪、AI） |
| 特征整合 | ❌ 无 | ✅ 26维特征向量 |
| 决策引擎 | ❌ 无 | ✅ 四层决策架构 |
| 仓位计算 | ❌ 无 | ✅ 科学风控 |
| 运行模式 | 单次运行 | ✅ 单次/持续监控/API服务 |
| AI调用 | ❌ 不支持 | ✅ REST API接口 |
| 输出格式 | CSV表格 | ✅ JSON + 文本 + 交易计划 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install flask requests pandas numpy
```

### 2. 三种运行模式

#### 模式1: 单次分析（默认）

```bash
# 分析BTC，默认10000U账户，1.5%风险
python main_enhanced.py

# 自定义参数
python main_enhanced.py --symbol ETHUSDT --balance 50000 --risk 0.02
```

**输出**：
- 完整的决策报告（终端）
- JSON文件（data/decision_*.json）
- 特征数据（data/features_*.json）
- 交易日志（data/trading_log.csv）

#### 模式2: 持续监控

```bash
# 每5分钟检查一次BTC
python main_enhanced.py --mode monitor --symbol BTCUSDT --interval 5

# 每10分钟检查ETH
python main_enhanced.py --mode monitor --symbol ETHUSDT --interval 10
```

**特点**：
- 24/7持续运行
- 自动定时分析
- 记录所有决策
- Ctrl+C 停止

#### 模式3: API服务器（供AI调用）

```bash
# 启动API服务器，监听5000端口
python main_enhanced.py --mode api --port 5000

# 自定义账户参数
python main_enhanced.py --mode api --balance 100000 --risk 0.01 --port 8080
```

**API端点**：
- `POST /api/analyze` - 执行分析
- `GET /api/decision` - 获取最新决策
- `GET /api/summary` - 获取决策摘要
- `GET /api/health` - 健康检查

---

## 🔌 API接口详解

### 1. POST /api/analyze - 执行分析

**请求**：
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT"}'
```

**响应**：
```json
{
  "status": "success",
  "data": {
    "timestamp": "2025-10-29 15:30:00",
    "decision": {
      "action": "BUY",
      "confidence": 77.5,
      "reason": "多维度强烈看涨信号（一致性85%）"
    },
    "signals": {
      "news_score": 80,
      "price_score": 75,
      "sentiment_score": 70,
      "ai_score": 85,
      "total_score": 77.5,
      "consistency": 0.85
    },
    "position": {
      "position_size": 0.15,
      "position_value": 7500.0,
      "stop_loss": 49000.0,
      "take_profit_1": 51500.0,
      "take_profit_2": 52500.0,
      "take_profit_3": 54000.0,
      "expected_profit": 345.0,
      "risk_reward_ratio": 2.3
    }
  }
}
```

### 2. GET /api/decision - 获取最新决策

**请求**：
```bash
curl http://localhost:5000/api/decision
```

**响应**：与 `/api/analyze` 相同格式

### 3. GET /api/summary - 获取决策摘要

**请求**：
```bash
curl http://localhost:5000/api/summary
```

**响应**：
```json
{
  "status": "success",
  "summary": "📊 交易决策摘要\n🎯 决策: BUY\n📈 置信度: 77%\n..."
}
```

### 4. GET /api/health - 健康检查

**请求**：
```bash
curl http://localhost:5000/api/health
```

**响应**：
```json
{
  "status": "ok",
  "system": "Enhanced Trading System",
  "timestamp": "2025-10-29T15:30:00"
}
```

---

## 🤖 AI集成示例

### 示例1: Python脚本调用

```python
import requests

def get_trading_advice(symbol="BTCUSDT"):
    """AI助手函数：获取交易建议"""
    response = requests.post(
        "http://localhost:5000/api/analyze",
        json={"symbol": symbol},
        timeout=60
    )
    
    if response.status_code == 200:
        decision = response.json()['data']['decision']
        
        if decision['action'] == 'BUY':
            return f"✅ 建议买入！置信度{decision['confidence']:.0f}%"
        elif decision['action'] == 'SELL':
            return f"⚠️ 建议卖出或观望"
        else:
            return f"🤔 建议暂时观望"
    
    return "❌ 无法获取建议"

# 使用
advice = get_trading_advice("BTCUSDT")
print(advice)
```

### 示例2: AI聊天机器人

```python
class TradingChatbot:
    """交易AI聊天机器人"""
    
    def __init__(self):
        self.api_base = "http://localhost:5000"
    
    def process_query(self, user_input: str) -> str:
        """处理用户查询"""
        
        # 识别意图
        if "买" in user_input or "购买" in user_input:
            symbol = self.extract_symbol(user_input)
            response = requests.post(
                f"{self.api_base}/api/analyze",
                json={"symbol": symbol}
            )
            
            if response.status_code == 200:
                decision = response.json()['data']['decision']
                return f"根据分析，{decision['action']}，置信度{decision['confidence']:.0f}%"
        
        elif "分析" in user_input:
            response = requests.get(f"{self.api_base}/api/summary")
            return response.json()['summary']
        
        return "我可以帮你分析交易机会！"
    
    def extract_symbol(self, text: str) -> str:
        """提取交易对"""
        if "BTC" in text.upper() or "比特币" in text:
            return "BTCUSDT"
        elif "ETH" in text.upper() or "以太坊" in text:
            return "ETHUSDT"
        return "BTCUSDT"

# 使用
bot = TradingChatbot()
print(bot.process_query("现在应该买比特币吗？"))
```

### 示例3: Telegram Bot

```python
from telegram.ext import Application, CommandHandler

async def analyze(update, context):
    """处理 /analyze 命令"""
    symbol = context.args[0] + "USDT" if context.args else "BTCUSDT"
    
    await update.message.reply_text(f"正在分析 {symbol}...")
    
    response = requests.post(
        "http://localhost:5000/api/analyze",
        json={"symbol": symbol},
        timeout=60
    )
    
    if response.status_code == 200:
        decision = response.json()['data']['decision']
        message = f"📊 {symbol} 分析\n\n"
        message += f"🎯 {decision['action']}\n"
        message += f"📈 置信度: {decision['confidence']:.0f}%\n"
        message += f"💡 {decision['reason']}"
        
        await update.message.reply_text(message)

# 启动bot
app = Application.builder().token("YOUR_TOKEN").build()
app.add_handler(CommandHandler("analyze", analyze))
app.run_polling()
```

---

## 📊 工作流程

### 完整流程图

```
用户/AI请求
    ↓
[步骤1: 数据获取]
├─ Gas费用 (Etherscan/Mempool)
├─ 价格数据 (Binance)
├─ 新闻情绪 (CoinGecko/CMC)
├─ 市场情绪 (Fear & Greed)
└─ AI预测 (Grok/Gemini/DeepSeek)
    ↓
[步骤2: 数据整合]
└─ IntegratedDataFetcher.get_26d_features()
   → 输出26维特征向量
    ↓
[步骤3: 决策分析]
├─ Layer 1: 安全检查 (5项)
├─ Layer 2: 信号评分 (4维度)
├─ Layer 3: 保守决策
└─ Layer 4: 仓位计算
    ↓
[步骤4: 输出结果]
├─ 终端打印报告
├─ 保存JSON文件
├─ 更新交易日志
└─ 返回API响应
    ↓
用户/AI获得结果
```

### 数据流示例

```python
# 1. 原始数据
{
  "gas": {"eth": 15, "btc": 8},
  "price": {"current": 50000, "change_24h": 2.5},
  "news": {"positive": 0.4, "negative": 0.1, "total": 15},
  "sentiment": {"fear_greed": 58},
  "ai": [{"direction": "up", "confidence": 0.8}, ...]
}

# 2. 26维特征向量
[15.0, 8.0, 1, 1, 50000, 2.5, 1000000, 0.02, 1, ...]

# 3. 决策结果
{
  "action": "BUY",
  "confidence": 77.5,
  "position_size": 0.15,
  "stop_loss": 49000,
  ...
}
```

---

## 📁 文件输出

### 1. 决策结果 JSON

**位置**: `data/decision_BTCUSDT_20251029_153000.json`

```json
{
  "timestamp": "2025-10-29 15:30:00",
  "decision": {...},
  "signals": {...},
  "position": {...},
  "risk_management": {...},
  "safety_checks": {...}
}
```

### 2. 特征数据 JSON

**位置**: `data/features_BTCUSDT_20251029_153000.json`

```json
{
  "features": [15.0, 8.0, ...],
  "metadata": {
    "current_price": 50000,
    "gas": {...},
    "news": {...},
    "sentiment": {...},
    "ai": {...}
  }
}
```

### 3. 交易日志 CSV

**位置**: `data/trading_log.csv`

```csv
timestamp,symbol,action,confidence,total_score,current_price,stop_loss,take_profit_1,position_size
2025-10-29 15:30:00,BTCUSDT,BUY,77.5,77.5,50000,49000,51500,0.15
2025-10-29 15:35:00,BTCUSDT,HOLD,50.0,65.0,50100,,,
```

---

## ⚙️ 配置参数

### 命令行参数

```bash
python main_enhanced.py \
  --mode single \          # 运行模式: single/monitor/api
  --symbol BTCUSDT \       # 交易对
  --balance 10000 \        # 账户余额
  --risk 0.015 \          # 单笔风险比例 (1.5%)
  --interval 5 \          # 监控间隔（分钟，monitor模式）
  --port 5000             # API端口（api模式）
```

### 决策引擎参数

可在代码中修改：

```python
system = EnhancedTradingSystem(
    account_balance=10000,  # 账户余额
    risk_percent=0.015      # 单笔风险1.5%
)

# 调整权重
system.decision_engine.weights = {
    'news': 0.30,
    'price': 0.25,
    'sentiment': 0.25,
    'ai': 0.20
}

# 调整阈值
system.decision_engine.thresholds = {
    'buy_score': 75,
    'sell_score': 25,
    'min_consistency': 0.80
}
```

---

## 🧪 测试

### 测试AI集成

```bash
# 测试所有功能
python test_ai_integration.py --test all

# 测试直接调用
python test_ai_integration.py --test direct

# 测试API调用（需要先启动API服务器）
python test_ai_integration.py --test api

# 生成AI集成示例代码
python test_ai_integration.py --test examples
```

### 完整系统测试

```bash
# 1. 测试所有模块
python test_all.py

# 2. 测试决策引擎
python test_decision_engine.py

# 3. 测试杠杆计算
python test_leverage.py

# 4. 测试增强版主程序
python main_enhanced.py --symbol BTCUSDT
```

---

## 🎯 使用场景

### 场景1: 个人交易者

```bash
# 早上执行一次分析
python main_enhanced.py --symbol BTCUSDT

# 根据报告手动交易
# 查看 data/decision_*.json 获取详细信息
```

### 场景2: 量化交易

```bash
# 启动持续监控
python main_enhanced.py --mode monitor --interval 5

# 配合自动化交易脚本
# 读取 data/trading_log.csv 执行交易
```

### 场景3: AI助手服务

```bash
# 启动API服务器
python main_enhanced.py --mode api --port 5000

# 让AI助手调用API
# 用户通过聊天机器人获取建议
```

### 场景4: 多币种监控

```bash
# 终端1: 监控BTC
python main_enhanced.py --mode monitor --symbol BTCUSDT --interval 5

# 终端2: 监控ETH
python main_enhanced.py --mode monitor --symbol ETHUSDT --interval 5

# 终端3: 监控BNB
python main_enhanced.py --mode monitor --symbol BNBUSDT --interval 5
```

---

## 📊 输出示例

### 终端输出

```
================================================================================
📊 交易决策报告
================================================================================
时间: 2025-10-29 15:30:00

🟢 决策: BUY
   置信度: 77%
   原因: 多维度强烈看涨信号（一致性85%）

📡 信号分析:
   新闻信号: 80/100 (权重30%)
   价格信号: 75/100 (权重25%)
   情绪信号: 70/100 (权重25%)
   AI信号: 85/100 (权重20%)
   总分: 77/100
   一致性: 85%

💰 仓位管理:
   仓位大小: 0.15000000 ($7,500.00)
   仓位占比: 15.00%
   止损价: $49,000.00 (-2.00%)
   止盈目标:
      目标1 (50%): $51,500.00
      目标2 (30%): $52,500.00
      目标3 (20%): $54,000.00
   最大亏损: $-150.00
   期望盈利: $345.00
   风险收益比: 2.3:1

🛡️ 风险管理:
   账户余额: $10,000.00
   单笔风险: 1.50%
   最大风险金额: $150.00
   当前持仓数: 0

🔒 安全检查: ✅ 通过
   所有安全检查通过 ✅

================================================================================
```

---

## 🔄 与原版对比

### 运行方式对比

**原版 main.py**:
```bash
python main.py
# 输出: CSV文件，AI预测对比表格
```

**增强版 main_enhanced.py**:
```bash
# 方式1: 单次分析
python main_enhanced.py
# 输出: 完整决策报告 + JSON + 交易日志

# 方式2: 持续监控
python main_enhanced.py --mode monitor

# 方式3: API服务
python main_enhanced.py --mode api
```

### 功能对比

| 功能 | 原版 | 增强版 |
|------|------|--------|
| 数据源 | Binance | Binance + Gas + 新闻 + 情绪 |
| AI预测 | ✅ 3个模型 | ✅ 3个模型 + 整合分析 |
| 决策逻辑 | ❌ 无 | ✅ 四层决策引擎 |
| 风险管理 | ❌ 无 | ✅ 科学仓位计算 |
| 止盈止损 | ❌ 无 | ✅ 分批止盈策略 |
| 运行模式 | 单次 | 单次/监控/API |
| AI调用 | ❌ 不支持 | ✅ REST API |
| 输出格式 | CSV | JSON + CSV + 文本 |

---

## 💡 最佳实践

### 1. 测试流程

```bash
# 第一次使用
1. python test_all.py              # 测试系统
2. python test_decision_engine.py  # 理解决策
3. python main_enhanced.py         # 单次分析
4. 阅读输出报告，理解逻辑
5. python main_enhanced.py --mode api  # 启动API
6. python test_ai_integration.py   # 测试AI集成
```

### 2. 实盘使用

```bash
# 保守策略
python main_enhanced.py \
  --balance 10000 \
  --risk 0.01 \
  --symbol BTCUSDT

# 如果决策是BUY，严格按照止损止盈执行
```

### 3. AI助手集成

```python
# 1. 启动API服务器
# Terminal 1:
python main_enhanced.py --mode api

# 2. AI助手调用
# Terminal 2:
python ai_integration_examples/example_1_simple.py
```

### 4. 多币种策略

```bash
# 使用supervisor或systemd管理多个进程
# btc_monitor.sh
python main_enhanced.py --mode monitor --symbol BTCUSDT --interval 5

# eth_monitor.sh
python main_enhanced.py --mode monitor --symbol ETHUSDT --interval 5
```

---

## ⚠️ 注意事项

### 1. API限制

- Binance API有请求频率限制
- 建议监控模式interval >= 5分钟
- 使用API密钥可提高限额

### 2. 数据依赖

- 需要网络连接获取实时数据
- Gas数据可能偶尔获取失败（会降级处理）
- 新闻和情绪数据每天有限额

### 3. 风险控制

- 决策引擎非常保守，大部分时候会HOLD
- 这是正常的，好机会需要耐心等待
- 不要因为HOLD次数多而修改参数
- 严格执行止损，不要心存侥幸

### 4. 性能优化

- 单次分析需要30-60秒（获取多源数据）
- API模式下保持服务常驻，响应更快
- 可以缓存部分数据（如Gas、情绪）

---

## 🐛 故障排查

### 问题1: 模块导入失败

```bash
# 解决方案
export PYTHONPATH="${PYTHONPATH}:/path/to/crypto_price_prediction"
# 或
cd crypto_price_prediction
python main_enhanced.py
```

### 问题2: API服务器无法访问

```bash
# 检查服务器是否运行
curl http://localhost:5000/api/health

# 检查端口占用
lsof -i :5000

# 更换端口
python main_enhanced.py --mode api --port 8080
```

### 问题3: 数据获取失败

```bash
# 检查网络连接
ping api.binance.com

# 检查API密钥（如果使用）
cat config.py | grep API_KEY

# 查看详细日志
tail -f logs/main_enhanced_*.log
```

### 问题4: 决策总是HOLD

```
这是正常的！决策引擎非常保守。

如果想看到更多BUY/SELL，可以：
1. 降低阈值（不推荐）
2. 调整权重
3. 等待更好的市场时机

建议：保持保守策略，避免频繁交易
```

---

## 📚 相关文档

- [DECISION_ENGINE_GUIDE.md](DECISION_ENGINE_GUIDE.md) - 决策引擎详细指南
- [DECISION_ENGINE_README.md](DECISION_ENGINE_README.md) - 决策引擎快速入门
- [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - 整合完成报告
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总体概述

---

## 🤝 贡献

发现问题或有改进建议？

1. 运行测试: `python test_all.py`
2. 描述问题和复现步骤
3. 提供日志文件
4. 建议解决方案

---

## 📞 支持

- 📧 Email: support@example.com
- 💬 Discord: [加入社区](#)
- 📱 Telegram: [@crypto_predict](#)

---

**免责声明**: 本系统仅供教育和研究目的，不构成投资建议。加密货币交易存在巨大风险，请谨慎使用。

---

*最后更新: 2025-10-29*  
*版本: v1.0.0*  
*作者: Crypto Prediction Team*
