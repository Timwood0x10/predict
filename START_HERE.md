# 🚀 从这里开始！

## 快速启动（推荐）

```bash
# 进入项目目录
cd crypto_price_prediction

# 运行快速启动脚本（交互式菜单）
./quick_start.sh
```

**脚本会自动：**
- ✅ 检查Python环境
- ✅ 安装缺失依赖
- ✅ 提供交互式菜单
- ✅ 引导你完成配置

---

## 或者直接运行

### 1️⃣ 单次分析（最简单）

```bash
python main_enhanced.py
```

### 2️⃣ 持续监控

```bash
python main_enhanced.py --mode monitor --interval 5
```

### 3️⃣ 启动API服务器

```bash
python main_enhanced.py --mode api --port 5000
```

---

## 查看帮助

```bash
python main_enhanced.py --help
```

---

## 阅读文档

- **快速入门**: [MAIN_INTEGRATION_README.md](MAIN_INTEGRATION_README.md)
- **详细指南**: [MAIN_ENHANCED_GUIDE.md](MAIN_ENHANCED_GUIDE.md)
- **决策引擎**: [DECISION_ENGINE_README.md](DECISION_ENGINE_README.md)

---

## 测试系统

```bash
# 测试所有功能
python test_all.py

# 测试决策引擎
python test_decision_engine.py

# 测试杠杆计算
python test_leverage.py
```

---

**提示**: 首次使用建议运行 `./quick_start.sh`，选择菜单选项4运行测试，确保系统正常。

**支持**: Linux & macOS ✅
