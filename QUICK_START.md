# ⚡ 快速开始指南

## 🚀 一分钟上手

### 最简单的方式
```bash
# 使用快速脚本（推荐）
bash quick_trade.sh
```

### 修改参数
```bash
# 编辑脚本
nano quick_trade.sh

# 修改这5个参数：
CAPITAL=1000        # 本金（U）
LEVERAGE=10         # 杠杆倍数
RISK=2.0            # 风险比例（%）
STOP_LOSS=2.0       # 止损比例（%）
SYMBOL=BTCUSDT      # 交易对

# 保存后运行
bash quick_trade.sh
```

---

## 📋 参数速查表

| 参数 | 含义 | 推荐值 | 示例 |
|------|------|--------|------|
| **CAPITAL** | 本金（U） | 1000 | `CAPITAL=1000` |
| **LEVERAGE** | 杠杆倍数 | 5-10 | `LEVERAGE=10` |
| **RISK** | 风险比例（%） | 1-2 | `RISK=2.0` |
| **STOP_LOSS** | 止损比例（%） | 2 | `STOP_LOSS=2.0` |
| **SYMBOL** | 交易对 | BTCUSDT | `SYMBOL=BTCUSDT` |

---

## 🎯 快速场景

### 场景1：我是新手
```bash
CAPITAL=500         # 小资金测试
LEVERAGE=5          # 低杠杆
RISK=1.0            # 保守风险
STOP_LOSS=2.0       # 标准止损
SYMBOL=BTCUSDT      # 比特币
```

### 场景2：标准交易（推荐）
```bash
CAPITAL=1000        # 标准资金
LEVERAGE=10         # 中等杠杆
RISK=2.0            # 标准风险
STOP_LOSS=2.0       # 标准止损
SYMBOL=BTCUSDT      # 比特币
```

### 场景3：分析以太坊
```bash
CAPITAL=1000
LEVERAGE=10
RISK=2.0
STOP_LOSS=2.0
SYMBOL=ETHUSDT      # 改成以太坊
```

---

## 💡 参数含义（一句话版）

- **CAPITAL**：你有多少钱（U）
- **LEVERAGE**：放大多少倍（1-125）
- **RISK**：单笔最多亏多少本金的百分比（1-3%推荐）
- **STOP_LOSS**：价格反向多少就止损（1-3%推荐）
- **SYMBOL**：分析哪个币（BTC、ETH等）

---

## ⚠️ 重要提示

### 杠杆风险
- 5倍：价格反向20%爆仓 🟢
- 10倍：价格反向10%爆仓 🟡
- 20倍：价格反向5%爆仓 🔴
- 50倍：价格反向2%爆仓 ⚫

### 风险建议
- 新手：1%风险 + 5倍杠杆
- 进阶：2%风险 + 10倍杠杆
- 老手：2%风险 + 20倍杠杆

---

## 📚 详细文档

需要了解更多？查看：
- `PARAMETERS_GUIDE.md` - 参数详细说明
- `docs/ADVANCED_SYSTEM_GUIDE.md` - 系统使用指南
- `docs/FINAL_SUMMARY.md` - 完整总结

---

## 🆘 常见问题

**Q: 脚本卡住不动？**
A: 等1-2分钟，可能在获取数据

**Q: 如何修改参数？**
A: 编辑 `quick_trade.sh` 文件

**Q: 如何分析多个币种？**
A: 运行多次，每次改 SYMBOL

**Q: 杠杆越大越好吗？**
A: ❌ 不是！杠杆越大，爆仓越容易

---

**祝交易顺利！** 🚀
