# 🤖 加密货币交易决策系统

> 一个基于真实市场数据的交易辅助决策系统，支持双向交易（做多/做空）和杠杆交易

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 项目简介

这是一个**交易辅助决策系统**，不是自动交易机器人。它通过收集和分析多维度市场数据，为交易者提供参考建议。

### ⚠️ 重要声明

- ❌ **不保证盈利** - 这是辅助工具，不是圣杯
- ❌ **不能预测未来** - 基于历史和当前数据分析
- ❌ **需要人工判断** - 建议仅供参考，需结合自己的判断
- ✅ **风险自负** - 加密货币交易有高风险，请谨慎使用

---

## ✨ 核心功能

### 1. 真实数据收集

系统从以下来源获取**真实数据**：

| 数据类型 | 数据源 | 更新频率 |
|---------|--------|---------|
| 📈 **K线数据** | Binance API | 实时 |
| 💰 **Gas费用** | Etherscan + Mempool.space | 实时 |
| 📰 **新闻资讯** | NewsAPI + CryptoCompare + Odaily | 每小时 |
| 😊 **市场情绪** | Fear & Greed Index | 每小时 |

**注意**：AI预测部分目前使用基于市场情绪的算法，未集成真实的LLM API。

### 2. 决策策略

系统采用**三层验证框架**：

```
Layer 1: 安全检查 (5项前置条件)
    ├─ Gas费用是否合理
    ├─ 数据是否完整
    ├─ 市场是否极端
    ├─ 波动率是否可控
    └─ 账户状态是否正常
    
Layer 2: 多维度评分 (4个维度)
    ├─ 📰 新闻信号 (30%权重)
    ├─ 📈 价格信号 (25%权重)
    ├─ 😊 情绪信号 (25%权重)
    └─ 🤖 AI信号 (20%权重)
    
Layer 3: 最终决策
    ├─ 做多(LONG): 评分≥63 + AI支持
    ├─ 做空(SHORT): 评分≤57 + AI支持
    └─ 观望(HOLD): 其他情况
```

### 3. 交易策略

内置5种经典交易策略：

| 策略 | 适用场景 | 实现状态 |
|------|---------|---------|
| 趋势跟踪 | 明确的上涨或下跌趋势 | ✅ 已实现 |
| 均值回归 | 价格偏离均值 | ✅ 已实现 |
| 突破策略 | 突破关键支撑/阻力位 | ✅ 已实现 |
| 网格策略 | 震荡市场 | ✅ 已实现 |
| 剥头皮 | 短线快速交易 | ✅ 已实现 |

**AI决策层**会根据市场环境自动选择最适合的策略。

### 4. 风险管理

- **固定风险比例**：每笔交易风险固定（默认2%本金）
- **动态止损止盈**：基于波动率和风险收益比计算
- **杠杆仓位计算**：考虑杠杆倍数的科学仓位管理
- **分批止盈**：三级止盈（2:1, 3:1, 4:1风险收益比）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制.env.example到.env
cp .env.example .env

# 编辑.env文件，添加API密钥
nano .env
```

需要的API密钥：
- `NEWSAPI_KEY` - 新闻数据（可选，不设置会跳过新闻分析）
- 其他API免费，无需配置

### 3. 运行分析

```bash
# 一键分析BTC和ETH（推荐）
bash run_trading_analysis.sh
```

**就这么简单！**

---

## 📊 使用示例

### 默认分析

```bash
bash run_trading_analysis.sh
```

**默认配置**：
- 本金：1000 USDT
- 杠杆：10x
- 风险：2%
- 止损：2%
- 币种：BTC + ETH

### 自定义参数

```bash
# 编辑脚本
nano run_trading_analysis.sh

# 修改这些参数
CAPITAL=1000                    # 你的本金
LEVERAGE=10                     # 杠杆倍数
RISK=2.0                        # 风险比例（%）
STOP_LOSS=2.0                   # 止损比例（%）
SYMBOLS="BTCUSDT ETHUSDT"       # 要分析的币种
```

### 输出示例

```
================================================================================
📊 [1/2] 分析 BTCUSDT
================================================================================
当前价格: $110,667

【决策结果】
  🔴 操作: SHORT (做空)
  置信度: 72%
  原因: AI建议做空 + 引擎支持（10x杠杆）

【仓位管理】
  杠杆: 10x
  本金: 1000 USDT
  保证金: 100 USDT (10%)
  止损: $112,881 (+2%)
  止盈1: $106,240 (-4%, 2:1) → 平50%
  止盈2: $104,027 (-6%, 3:1) → 平30%
  止盈3: $101,814 (-8%, 4:1) → 平20%

================================================================================
📊 综合对比分析
================================================================================
  🔴 BTCUSDT    SHORT
  ⚪ ETHUSDT    HOLD

💡 交易建议：
  ✅ 有做空机会，优先选择置信度高的币种（BTC）
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [HOW_TO_USE.md](HOW_TO_USE.md) | 完整使用指南 ⭐**推荐** |
| [QUICK_START.md](QUICK_START.md) | 快速开始（1分钟上手） |
| [PARAMETERS_GUIDE.md](PARAMETERS_GUIDE.md) | 参数详细说明 |
| [docs/AI_DECISION_STRATEGY.md](docs/AI_DECISION_STRATEGY.md) | AI决策策略设计 |
| [docs/FINAL_SUMMARY.md](docs/FINAL_SUMMARY.md) | 项目完整总结 |
| [PROJECT_FILES.md](PROJECT_FILES.md) | 文件结构说明 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     数据收集层                               │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Gas费用监控   │ K线数据获取   │ 新闻聚合     │ 市场情绪分析    │
│ GasFeeMonitor│ DataFetcher  │ NewsAPI     │ SentimentAnalyzer│
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       └──────────────┴──────────────┴────────────────┘
                            │
                    ┌───────▼────────┐
                    │   数据整合器    │
                    │ DataIntegrator │
                    │  (26维特征)    │
                    └───────┬────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
        ┌───────▼────────┐      ┌──────▼──────┐
        │  AI决策层       │      │  决策引擎    │
        │ AIDecisionLayer│      │DecisionEngine│
        │  (策略选择)     │      │  (风险评估)  │
        └───────┬────────┘      └──────┬──────┘
                │                       │
                └───────────┬───────────┘
                            │
                    ┌───────▼────────┐
                    │   最终决策      │
                    │ LONG/SHORT/HOLD│
                    └────────────────┘
```

---

## 🔧 核心组件

### 数据层
- `utils/gas_monitor.py` - Gas费用监控
- `utils/data_fetcher.py` - Binance数据获取
- `utils/financial_news.py` - 新闻聚合
- `utils/news_processor.py` - 新闻深度处理
- `utils/sentiment_analyzer.py` - 市场情绪分析
- `utils/data_integrator.py` - 数据整合（26维特征）

### 决策层
- `ai_decision_layer.py` - AI智能决策层
- `utils/decision_engine.py` - 决策引擎（三层验证）

### 策略层
- `strategies/trend_following.py` - 趋势跟踪
- `strategies/mean_reversion.py` - 均值回归
- `strategies/breakout_strategy.py` - 突破策略
- `strategies/grid_strategy.py` - 网格策略
- `strategies/scalping_strategy.py` - 剥头皮策略

### 应用层
- `real_trading_decision.py` - 双币种对比分析
- `advanced_trading_system.py` - 高级杠杆交易系统
- `run_trading_analysis.sh` - 主要使用脚本

---

## 📊 数据处理流程

### 26维特征向量

系统将市场数据整合为26维特征向量：

```python
[0-3]   Gas费用特征 (4维)
  ├─ ETH Gas价格
  ├─ BTC Fee价格
  ├─ ETH是否适合交易
  └─ BTC是否适合交易

[4-11]  价格特征 (8维)
  ├─ 当前价格
  ├─ 价格变化率
  ├─ 平均成交量
  ├─ 波动率
  ├─ 趋势方向
  ├─ 最高价
  ├─ 最低价
  └─ 价格区间

[12-16] 新闻特征 (5维)
  ├─ 新闻情绪分数
  ├─ 正面新闻比例
  ├─ 负面新闻比例
  ├─ 新闻数量
  └─ 新闻情绪标签

[17-20] 市场情绪特征 (4维)
  ├─ 市场情绪分数
  ├─ 市场置信度
  ├─ 恐惧贪婪指数
  └─ 市场情绪标签

[21-25] AI预测特征 (5维)
  ├─ AI平均置信度
  ├─ 看涨模型数量
  ├─ 看跌模型数量
  ├─ AI一致性比例
  └─ AI共识方向
```

---

## ⚙️ 配置参数

| 参数 | 说明 | 默认值 | 推荐范围 |
|------|------|--------|---------|
| `CAPITAL` | 投入本金（USDT） | 1000 | 100-10000 |
| `LEVERAGE` | 杠杆倍数 | 10 | 5-20 |
| `RISK` | 单笔风险比例（%） | 2.0 | 1.0-3.0 |
| `STOP_LOSS` | 止损比例（%） | 2.0 | 1.5-3.0 |
| `SYMBOLS` | 交易对列表 | "BTCUSDT ETHUSDT" | 任意币安交易对 |

### 风险等级参考

| 杠杆 | 爆仓距离 | 风险等级 |
|------|---------|---------|
| 5x | 20% | 🟢 低风险 |
| 10x | 10% | 🟡 中等风险 |
| 20x | 5% | 🔴 高风险 |
| 50x | 2% | ⚫ 危险 |

---

## 🧪 测试

```bash
# 运行决策引擎测试
python -m pytest tests/test_decision_engine.py -v

# 运行策略测试
python -m pytest tests/test_strategies.py -v

# 运行所有测试
python -m pytest tests/ -v
```

**测试覆盖**：
- 决策引擎：8个核心场景
- 交易策略：25个测试用例
- 覆盖率：>80%

---

## 🔐 数据隐私

- ✅ 所有市场数据通过公开API获取
- ✅ 不收集用户个人信息
- ✅ 不上传交易数据到服务器
- ✅ 完全本地运行

---

## ⚠️ 风险提示

### 市场风险
- 加密货币市场**波动极大**
- 价格可能在短时间内大幅变动
- 过去表现**不代表未来结果**

### 杠杆风险
- 杠杆会放大盈利，**也会放大亏损**
- 10倍杠杆：价格反向10%就爆仓
- 建议新手使用**低杠杆**（5-10倍）

### 系统局限
- ❌ 不能预测黑天鹅事件
- ❌ 不能应对突发新闻
- ❌ 不能保证100%准确
- ❌ 依赖数据源稳定性

### 使用建议
1. ✅ 先用小资金测试
2. ✅ 严格执行止损
3. ✅ 不要重仓单个币种
4. ✅ 分批止盈，不贪婪
5. ✅ 保持理性，不情绪化

---

## 📈 实际表现

**免责声明**：以下数据仅为系统测试结果，不代表实际交易表现。

### 测试环境
- 时间：2025-10-30
- 币种：BTC, ETH
- 周期：12小时
- 策略：趋势跟踪 + 均值回归

### 决策准确性
- 安全检查通过率：95%
- 信号一致性：75%
- 趋势识别准确度：~70%（估计）

**注意**：实际表现受市场环境、参数设置、执行时机等多种因素影响。

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献方向
- 🐛 Bug修复
- ✨ 新功能建议
- 📚 文档改进
- 🧪 测试用例
- 🌐 多语言支持

---

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 👨‍💻 作者

不愿透露姓名的佚名
---

## 🙏 致谢

感谢以下开源项目和数据提供商：

- [Binance API](https://binance-docs.github.io/apidocs/) - K线数据
- [Etherscan API](https://etherscan.io/apis) - ETH Gas数据
- [Mempool.space API](https://mempool.space/docs/api) - BTC Fee数据
- [NewsAPI](https://newsapi.org/) - 新闻数据
- [Alternative.me](https://alternative.me/crypto/fear-and-greed-index/) - 恐惧贪婪指数
- [CryptoCompare](https://www.cryptocompare.com/) - 加密货币新闻
- [Odaily](https://www.odaily.news/) - 中文加密货币新闻

---

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 💬 Issue: [GitHub Issues](https://github.com/Timwood0x10/predict/issues)

---

## 🎓 学习资源

推荐学习资源：

- [Binance Academy](https://academy.binance.com/) - 加密货币基础知识
- [Investopedia](https://www.investopedia.com/) - 交易和投资教育
- [TradingView](https://www.tradingview.com/) - 技术分析学习

---

**最后提醒**：交易有风险，入市需谨慎！本系统仅为辅助工具，不构成投资建议。请在充分了解风险的情况下使用。

**祝交易顺利！** 🚀
