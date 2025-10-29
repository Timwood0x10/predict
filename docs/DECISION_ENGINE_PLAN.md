# 🎯 决策引擎设计方案 - 稳健保守版

## 📋 设计原则

**核心理念**: **风险第一，收益第二，稳中求胜**

- ✅ 严格风险控制（每笔1-2%）
- ✅ 科学止损止盈
- ✅ 仓位反推计算
- ✅ 保守决策逻辑
- ✅ 多重安全验证

---

## 🛡️ 风险管理核心

### 1. 仓位计算公式（科学方法）

```python
# 核心公式
仓位大小 = (总资金 × 风险比例) / (入场价 - 止损价)

# 示例
总资金 = $10,000
风险比例 = 0.015 (1.5%)
入场价 = $50,000
止损价 = $49,000 (2%止损)

仓位 = (10,000 × 0.015) / (50,000 - 49,000)
     = 150 / 1,000
     = 0.15 BTC
     = $7,500

验证：如果止损，亏损 = 0.15 × 1000 = $150 = 1.5%总资金 ✅
```

### 2. 止损设置策略

#### 方案A: 固定百分比（简单稳健）⭐

```python
STOP_LOSS_RULES = {
    "超低风险": 1.5%,    # 波动率 < 1%
    "低风险": 2.0%,      # 波动率 1-2%
    "中等风险": 2.5%,    # 波动率 2-3%
    "高风险": 3.0%       # 波动率 > 3%
}

# 根据波动率选择止损
if volatility < 0.01:
    stop_loss_percent = 0.015  # 1.5%
elif volatility < 0.02:
    stop_loss_percent = 0.020  # 2%
elif volatility < 0.03:
    stop_loss_percent = 0.025  # 2.5%
else:
    stop_loss_percent = 0.030  # 3%
```

#### 方案B: ATR动态止损（专业）

```python
# 使用ATR（平均真实波幅）
ATR = calculate_atr(kline_data, period=14)

# 止损距离 = 1.5倍ATR（保守）
stop_loss_distance = ATR * 1.5

# 止损价
if direction == "BUY":
    stop_loss_price = entry_price - stop_loss_distance
else:
    stop_loss_price = entry_price + stop_loss_distance
```

### 3. 止盈设置策略

#### 保守止盈原则

```python
# 风险收益比至少 2:1
TAKE_PROFIT_RATIO = {
    "保守": 2.5,    # 止损1%，止盈2.5%
    "标准": 2.0,    # 止损2%，止盈4%
    "积极": 1.5     # 止损3%，止盈4.5%
}

# 计算止盈
risk_amount = entry_price - stop_loss_price
reward_amount = risk_amount * 2.5  # 2.5倍风险

if direction == "BUY":
    take_profit_price = entry_price + reward_amount
else:
    take_profit_price = entry_price - reward_amount
```

#### 分批止盈（更稳健）⭐

```python
# 三段止盈法
TIERED_TAKE_PROFIT = {
    "第一目标": {
        "比例": 0.5,     # 卖出50%
        "盈利": 1.5%     # 1.5%时卖出一半
    },
    "第二目标": {
        "比例": 0.3,     # 再卖30%
        "盈利": 3.0%     # 3%时再卖
    },
    "第三目标": {
        "比例": 0.2,     # 剩余20%
        "盈利": 5.0%     # 5%时全部卖出
    }
}

# 优势：降低回撤风险，锁定利润
```

---

## 🎯 决策引擎架构

### 总体流程

```
输入: 26维特征向量
  ↓
Layer 1: 安全检查 (5项必须全过)
  ├─ Gas费用检查
  ├─ 数据完整性检查
  ├─ 市场状态检查
  ├─ 波动率检查
  └─ 账户状态检查
  ↓ 任一不过 → HOLD
  
Layer 2: 信号评分 (0-100分)
  ├─ 新闻信号 (30%) - 美联储/中美/关税
  ├─ 价格信号 (25%) - 趋势/涨跌
  ├─ 情绪信号 (25%) - 恐惧贪婪
  └─ AI信号 (20%) - 预测共识
  ↓ 加权总分
  
Layer 3: 保守决策 (高标准)
  ├─ 总分 > 75 且 一致性 > 80% → 考虑BUY
  ├─ 总分 < 25 且 一致性 > 80% → 考虑SELL
  └─ 其他 → HOLD
  ↓
  
Layer 4: 仓位计算
  ├─ 根据波动率选择止损
  ├─ 计算止损价格
  ├─ 反推仓位大小 (风险1-2%)
  └─ 计算止盈价格 (2.5倍风险)
  ↓
  
输出: 完整交易计划
```

---

## 📊 Layer 1: 安全检查（严格）

```python
def safety_check(features, account_balance, existing_positions):
    """
    安全检查 - 5项全过才能交易
    
    Returns:
        (通过?, 原因)
    """
    checks = {}
    
    # 1. Gas费用检查
    checks['gas'] = (
        features[0] < 30 or features[1] < 15  # 更严格：ETH<30或BTC<15
    )
    if not checks['gas']:
        return False, "Gas费用过高"
    
    # 2. 数据完整性检查
    checks['data'] = (
        features[15] >= 8 and  # 至少8条新闻
        sum(features[22:24]) > 0  # 有AI预测
    )
    if not checks['data']:
        return False, "数据不足"
    
    # 3. 市场状态检查
    checks['market'] = (
        25 < features[19] < 75  # 恐惧贪婪指数正常范围
    )
    if not checks['market']:
        return False, "市场情绪极端"
    
    # 4. 波动率检查（保守）
    checks['volatility'] = features[7] < 0.04  # 波动率<4%
    if not checks['volatility']:
        return False, "波动率过高"
    
    # 5. 账户状态检查
    checks['account'] = (
        len(existing_positions) < 3 and  # 最多3个持仓
        account_balance > 100  # 账户余额充足
    )
    if not checks['account']:
        return False, "账户状态不允许"
    
    return True, "所有检查通过"
```

---

## 📊 Layer 2: 信号评分（保守）

### 新闻信号（30%）

```python
def calculate_news_score(features, news_data=None):
    """
    新闻信号评分
    
    重点：美联储、中美、关税
    """
    score = 50  # 中性基础分
    
    # 1. 新闻情绪 (±15分)
    if features[16] == 1:      # 看涨
        score += 15
    elif features[16] == -1:   # 看跌
        score -= 15
    
    # 2. 正负面比例 (±10分)
    if features[13] > 0.25 and features[14] < 0.15:  # 正面多，负面少
        score += 10
    elif features[14] > 0.25 and features[13] < 0.15:  # 负面多，正面少
        score -= 10
    
    # 3. 新闻数量 (±5分)
    if features[15] > 15:
        score += 5
    elif features[15] < 5:
        score -= 5
    
    # 4. 高优先级关键词加权 (±10分)
    # 如果新闻包含美联储/中美/关税等关键词，额外加权
    # 这需要从news_data中获取
    if news_data:
        high_priority_keywords = ['fed', 'federal reserve', 'china', 'tariff']
        keyword_count = sum(1 for kw in high_priority_keywords 
                           if any(kw in str(news).lower() for news in news_data))
        if keyword_count >= 2:
            # 如果新闻是利好
            if features[16] == 1:
                score += 10  # 强化看涨信号
            # 如果新闻是利空
            elif features[16] == -1:
                score -= 10  # 强化看跌信号
    
    return max(0, min(100, score))
```

### 价格信号（25%）

```python
def calculate_price_score(features):
    """价格信号评分"""
    score = 50
    
    # 1. 趋势方向 (±15分)
    if features[8] == 1:       # 上涨
        score += 15
    elif features[8] == -1:    # 下跌
        score -= 15
    
    # 2. 24h涨跌幅 (±10分) - 保守：只认可温和变化
    change = features[5]
    if 0.5 < change < 2.5:     # 温和上涨0.5-2.5%
        score += 10
    elif change >= 2.5:        # 上涨过快，警惕
        score += 5
    elif -2.5 < change < -0.5: # 温和下跌
        score -= 10
    elif change <= -2.5:       # 下跌过快
        score -= 5
    
    # 3. 波动率 (±10分)
    if features[7] < 0.015:    # 超低波动
        score += 10
    elif features[7] < 0.025:  # 低波动
        score += 5
    elif features[7] > 0.04:   # 高波动
        score -= 10
    
    return max(0, min(100, score))
```

### 情绪信号（25%）

```python
def calculate_sentiment_score(features):
    """市场情绪评分"""
    score = 50
    
    # 1. 恐惧贪婪指数 (±15分) - 保守：只在理想区间加分
    fgi = features[19]
    if 50 < fgi < 65:          # 理想区间：温和乐观
        score += 15
    elif 35 < fgi < 50:        # 温和悲观，可能机会
        score += 10
    elif fgi >= 75:            # 过度贪婪，危险
        score -= 15
    elif fgi <= 25:            # 过度恐惧，观望
        score -= 10
    
    # 2. 情绪标签 (±10分)
    if features[20] == 1:
        score += 10
    elif features[20] == -1:
        score -= 10
    
    return max(0, min(100, score))
```

### AI信号（20%）

```python
def calculate_ai_score(features):
    """AI预测评分"""
    score = 50
    
    # 1. AI共识 (±10分)
    if features[25] == 1:      # 看涨共识
        score += 10
    elif features[25] == -1:   # 看跌共识
        score -= 10
    
    # 2. 一致性 (±10分)
    if features[24] > 0.7:     # 高一致性
        score += 10
    elif features[24] < 0.4:   # 低一致性
        score -= 5
    
    return max(0, min(100, score))
```

---

## 📊 Layer 3: 保守决策（高标准）

```python
def make_conservative_decision(total_score, features):
    """
    保守决策逻辑 - 高标准
    
    Returns:
        (action, confidence, reason)
    """
    # 计算一致性指标
    consistency = calculate_consistency(features)
    
    # 标准1: 分数高标准
    # 标准2: 必须有足够一致性
    # 标准3: 市场状态正常
    
    # 看涨决策（严格）
    if (total_score > 75 and           # 高分
        consistency > 0.8 and          # 高一致性
        features[19] < 70):            # 不过度贪婪
        
        return "BUY", total_score, "多维度强烈看涨信号"
    
    # 看跌决策（严格）
    elif (total_score < 25 and         # 低分
          consistency > 0.8 and        # 高一致性
          features[19] > 30):          # 不过度恐慌
        
        return "SELL", 100 - total_score, "多维度强烈看跌信号"
    
    # 观望（保守）
    else:
        return "HOLD", 50, "信号不够明确或市场状态不佳"

def calculate_consistency(features):
    """
    计算各维度一致性
    
    Returns:
        一致性分数 0-1
    """
    signals = []
    
    # 新闻方向
    if features[16] != 0:
        signals.append(features[16])
    
    # 价格趋势
    if features[8] != 0:
        signals.append(features[8])
    
    # 市场情绪
    if features[20] != 0:
        signals.append(features[20])
    
    # AI预测
    if features[25] != 0:
        signals.append(features[25])
    
    if not signals:
        return 0.5
    
    # 计算一致性
    positive_count = signals.count(1)
    negative_count = signals.count(-1)
    
    max_count = max(positive_count, negative_count)
    consistency = max_count / len(signals)
    
    return consistency
```

---

## 📊 Layer 4: 仓位与止损计算

```python
def calculate_position_and_stops(
    entry_price, 
    direction, 
    account_balance, 
    volatility,
    risk_percent=0.015  # 默认1.5%
):
    """
    计算仓位大小、止损和止盈
    
    Args:
        entry_price: 入场价格
        direction: "BUY" or "SELL"
        account_balance: 账户余额
        volatility: 当前波动率
        risk_percent: 风险比例（默认1.5%）
    
    Returns:
        {
            'position_size': 仓位大小,
            'stop_loss': 止损价,
            'take_profit_1': 第一止盈,
            'take_profit_2': 第二止盈,
            'take_profit_3': 第三止盈,
            'max_loss': 最大亏损金额,
            'expected_profit': 期望盈利
        }
    """
    # 1. 根据波动率选择止损百分比
    if volatility < 0.01:
        stop_loss_percent = 0.015    # 1.5%
    elif volatility < 0.02:
        stop_loss_percent = 0.020    # 2%
    elif volatility < 0.03:
        stop_loss_percent = 0.025    # 2.5%
    else:
        stop_loss_percent = 0.030    # 3%
    
    # 2. 计算止损价
    if direction == "BUY":
        stop_loss_price = entry_price * (1 - stop_loss_percent)
    else:
        stop_loss_price = entry_price * (1 + stop_loss_percent)
    
    # 3. 计算止损距离
    stop_distance = abs(entry_price - stop_loss_price)
    
    # 4. 反推仓位大小（核心公式）
    risk_amount = account_balance * risk_percent
    position_size = risk_amount / stop_distance
    
    # 5. 验证仓位限制
    max_position = account_balance * 0.15  # 最多15%资金
    if position_size * entry_price > max_position:
        position_size = max_position / entry_price
        # 重新计算实际风险
        actual_risk = position_size * stop_distance / account_balance
        print(f"⚠️ 仓位受限，实际风险: {actual_risk*100:.2f}%")
    
    # 6. 计算分批止盈（2.5倍风险收益比）
    risk_distance = stop_distance
    
    if direction == "BUY":
        take_profit_1 = entry_price + (risk_distance * 1.5)  # 1.5倍
        take_profit_2 = entry_price + (risk_distance * 2.5)  # 2.5倍
        take_profit_3 = entry_price + (risk_distance * 4.0)  # 4倍
    else:
        take_profit_1 = entry_price - (risk_distance * 1.5)
        take_profit_2 = entry_price - (risk_distance * 2.5)
        take_profit_3 = entry_price - (risk_distance * 4.0)
    
    # 7. 计算预期盈亏
    max_loss = -risk_amount  # 最大亏损
    expected_profit = risk_amount * (0.5*1.5 + 0.3*2.5 + 0.2*4.0)  # 加权平均
    
    return {
        'position_size': round(position_size, 6),
        'position_value': round(position_size * entry_price, 2),
        'stop_loss': round(stop_loss_price, 2),
        'stop_loss_percent': stop_loss_percent * 100,
        'take_profit_1': round(take_profit_1, 2),  # 卖50%
        'take_profit_2': round(take_profit_2, 2),  # 卖30%
        'take_profit_3': round(take_profit_3, 2),  # 卖20%
        'max_loss': round(max_loss, 2),
        'expected_profit': round(expected_profit, 2),
        'risk_reward_ratio': round(expected_profit / abs(max_loss), 2)
    }
```

---

## 🎯 完整输出示例

```python
{
    "decision": {
        "action": "BUY",
        "confidence": 78,
        "reason": "多维度强烈看涨信号"
    },
    
    "signals": {
        "news_score": 75,
        "price_score": 70,
        "sentiment_score": 80,
        "ai_score": 60,
        "total_score": 73,
        "consistency": 0.85
    },
    
    "position": {
        "entry_price": 50000,
        "position_size": 0.15,          # BTC数量
        "position_value": 7500,         # 美元价值
        "stop_loss": 49000,             # 止损价
        "stop_loss_percent": 2.0,       # 止损2%
        "take_profit_1": 51500,         # 第一目标（50%仓位）
        "take_profit_2": 52500,         # 第二目标（30%仓位）
        "take_profit_3": 54000,         # 第三目标（20%仓位）
        "max_loss": -150,               # 最大亏损$150
        "expected_profit": 412.5,       # 期望盈利$412.5
        "risk_reward_ratio": 2.75       # 风险收益比2.75:1
    },
    
    "risk_management": {
        "account_balance": 10000,
        "risk_percent": 1.5,            # 风险1.5%
        "max_risk_amount": 150,
        "actual_risk_amount": 150,
        "position_percent": 15.0        # 仓位占比15%
    },
    
    "safety_checks": {
        "gas_ok": True,
        "data_sufficient": True,
        "market_normal": True,
        "volatility_ok": True,
        "account_ok": True
    }
}
```

---

## ✅ 核心优势

1. **风险第一** - 严格的1-2%风险控制
2. **科学仓位** - 反推公式，确保风险可控
3. **保守决策** - 高标准，只在明确信号时交易
4. **分批止盈** - 降低回撤，锁定利润
5. **多重验证** - 5项安全检查 + 一致性验证
6. **稳中求胜** - 风险收益比2.5:1以上

---

## 🚀 下一步

立即实现这个决策引擎！

文件: `utils/decision_engine.py`
