# 📂 项目文件结构（精简版）

## ✅ 核心文档（7个）

### 📖 使用文档（用户必看）
1. **README.md** - 项目主文档
2. **HOW_TO_USE.md** - 完整使用指南 ⭐**推荐先看**
3. **QUICK_START.md** - 快速开始（1分钟上手）
4. **PARAMETERS_GUIDE.md** - 参数详细说明

### 📚 技术文档（开发参考）
5. **docs/AI_DECISION_STRATEGY.md** - AI决策策略设计
6. **docs/FINAL_SUMMARY.md** - 项目完整总结

### 🚀 核心脚本
7. **run_trading_analysis.sh** - 主要分析脚本 ⭐**主要使用**

---

## 🎯 快速导航

### 我是新手，想快速上手
```bash
# 1. 先看这个
cat HOW_TO_USE.md

# 2. 再看这个
cat QUICK_START.md

# 3. 直接运行
bash run_trading_analysis.sh
```

### 我想详细了解参数
```bash
cat PARAMETERS_GUIDE.md
```

### 我想了解技术细节
```bash
cat docs/AI_DECISION_STRATEGY.md
cat docs/FINAL_SUMMARY.md
```

---

## 📊 核心系统文件

### Python主程序（2个）
- `real_trading_decision.py` - 双币种对比分析
- `advanced_trading_system.py` - 高级杠杆交易系统

### Shell脚本（1个）
- `run_trading_analysis.sh` - 主要使用脚本

### 核心组件（utils/）
- `decision_engine.py` - 决策引擎
- `data_integrator.py` - 数据整合
- `financial_news.py` - 新闻聚合
- `sentiment_analyzer.py` - 情绪分析
- `gas_monitor.py` - Gas费监控
- `data_fetcher.py` - 数据获取
- 等等...

### AI决策层
- `ai_decision_layer.py` - AI智能决策

### 交易策略（strategies/）
- `trend_following.py` - 趋势跟踪
- `mean_reversion.py` - 均值回归
- `breakout_strategy.py` - 突破策略
- `grid_strategy.py` - 网格策略
- `scalping_strategy.py` - 剥头皮策略

---

## 🗑️ 已删除的冗余文件（25个）

以下文件已被删除，内容已整合到核心文档中：

### 根目录删除的文件
- AI_AUTO_TRADING_GUIDE.md
- DECISION_ENGINE_README.md
- MAIN_ENHANCED_GUIDE.md
- MAIN_INTEGRATION_README.md
- PROJECT_SUMMARY.md
- START_HERE.md
- QUICKSTART.md
- TODO.md
- quick_start.sh

### docs/删除的文件
- ADVANCED_SYSTEM_GUIDE.md
- AI_INTEGRATION_GUIDE.md
- DATA_INTEGRATOR_SUMMARY.md
- DECISION_ENGINE_GUIDE.md
- DECISION_ENGINE_PLAN.md
- ENHANCEMENT_PLAN.md
- ENV_SETUP_GUIDE.md
- FINAL_REPORT.md
- IMPLEMENTATION_COMPLETE.md
- INTEGRATION_PLAN.md
- INTEGRATION_SUMMARY.md
- NEWS_PROCESSOR_SUMMARY.md
- REAL_DECISION_DEMO_SUMMARY.md
- REAL_TRADING_SYSTEM_SUMMARY.md
- TRADING_STRATEGY_DESIGN.md

**删除原因**: 内容重复、过时、或已整合到核心文档

---

## 📖 文档阅读顺序建议

### 新手路径
1. HOW_TO_USE.md（必读）
2. QUICK_START.md（必读）
3. PARAMETERS_GUIDE.md（重要）
4. 开始使用 `run_trading_analysis.sh`

### 进阶路径
1. docs/AI_DECISION_STRATEGY.md（理解策略）
2. docs/FINAL_SUMMARY.md（完整了解）
3. 阅读源代码

---

## ✨ 总结

**精简后的项目**：
- ✅ 7个核心文档（清晰明了）
- ✅ 1个主要脚本（易于使用）
- ✅ 2个Python程序（功能完整）
- ✅ 删除25个冗余文件（减少混乱）

**现在你只需要**：
```bash
bash run_trading_analysis.sh
```

就可以开始使用了！🚀
