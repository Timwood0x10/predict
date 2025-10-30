# 🤖 AI交易决策策略方案

## 📋 核心思路

将30维特征数据转换为AI可理解的**决策树逻辑**，结合**多层验证机制**，确保交易决策的准确性和安全性。

**最新更新**：新增Polymarket预测市场数据（4维特征），总特征从26维扩展到30维。

---

## 🎯 决策框架（三层验证）

```
第一层: 前置条件检查 (必须全部满足)
    ↓
第二层: 多维度评分 (加权计算)
    ↓
第三层: 风险评估 (最终确认)
    ↓
输出: BUY/SELL/HOLD + 置信度
```

---

## 📊 第一层: 前置条件检查（Gate Keeper）

### 必要条件（任一不满足 → HOLD）

```python
必须满足:
1. Gas费用合理
   - ETH Gas < 50 Gwei OR BTC Fee < 20 sat/vB
   - features[2] == 1 OR features[3] == 1
   
2. 市场不极端恐慌/贪婪
   - 20 < 恐惧贪婪指数 < 80
   - 20 < features[19] < 80
   
3. 波动率可控
   - 波动率 < 0.05 (5%)
   - features[7] < 0.05
   
4. 有足够数据支持
   - 新闻数量 > 5 OR AI预测存在
   - features[15] > 5 OR (features[22] + features[23]) > 0
```

### 排除条件（任一满足 → 强制HOLD）

```python
禁止交易:
1. 极端波动
   - 24h涨跌 > ±5%
   - abs(features[5]) > 10
   
2. 市场崩盘信号
   - 恐惧贪婪指数 < 10
   - features[19] < 10
   
3. 数据缺失严重
   - 超过50%特征为0
```

---

## 🎯 第二层: 多维度评分系统（Scoring）

### 评分维度（总分100分）

#### 1️⃣ 成本维度（10分）
```python
score_cost = 0

# Gas费用
if features[0] < 10:      # ETH Gas < 10 Gwei
    score_cost += 5
elif features[0] < 30:
    score_cost += 3

if features[1] < 5:       # BTC Fee < 5 sat/vB
    score_cost += 5
elif features[1] < 15:
    score_cost += 3

权重: 10%
```

#### 2️⃣ 价格趋势维度（25分）
```python
score_trend = 0

# 短期趋势
if features[8] == 1:      # 上涨趋势
    score_trend += 10
elif features[8] == -1:   # 下跌趋势
    score_trend -= 10

# 24h涨跌
if 0 < features[5] < 3:   # 温和上涨
    score_trend += 8
elif features[5] > 3:     # 强劲上涨
    score_trend += 5
elif -3 < features[5] < 0:  # 温和下跌
    score_trend -= 8
elif features[5] < -3:    # 强劲下跌
    score_trend -= 5

# 波动率
if features[7] < 0.01:    # 低波动
    score_trend += 7
elif features[7] < 0.03:  # 中等波动
    score_trend += 3

权重: 25%
```

#### 3️⃣ 新闻情绪维度（20分）
```python
score_news = 0

# 新闻情绪标签
if features[16] == 1:     # 看涨
    score_news += 10
elif features[16] == -1:  # 看跌
    score_news -= 10

# 正负面比例
pos_neg_ratio = features[13] / (features[14] + 0.01)
if pos_neg_ratio > 3:     # 正面远多于负面
    score_news += 7
elif pos_neg_ratio < 0.33:  # 负面远多于正面
    score_news -= 7

# 新闻数量
if features[15] > 15:     # 关注度高
    score_news += 3

权重: 20%
```

#### 4️⃣ 市场情绪维度（25分）
```python
score_sentiment = 0

# 恐惧贪婪指数
fgi = features[19]
if 55 < fgi < 70:         # 温和贪婪，适合买入
    score_sentiment += 10
elif 70 < fgi:            # 过度贪婪，警惕
    score_sentiment -= 5
elif 30 < fgi < 45:       # 温和恐惧，可能抄底
    score_sentiment += 5
elif fgi < 30:            # 过度恐惧，观望
    score_sentiment -= 10

# 市场情绪标签
if features[20] == 1:     # 看涨
    score_sentiment += 8
elif features[20] == -1:  # 看跌
    score_sentiment -= 8

# 市场置信度
if features[18] > 60:     # 高置信度
    score_sentiment += 7
elif features[18] > 40:
    score_sentiment += 3

权重: 25%
```

#### 5️⃣ Polymarket预测市场维度（20分）⭐新增
```python
score_polymarket = 0

# Polymarket评分
polymarket_score = features[21]  # 0-100分
if polymarket_score > 60:         # 看涨
    score_polymarket += 10
elif polymarket_score < 40:       # 看跌
    score_polymarket -= 10
else:                             # 中性
    score_polymarket += 0

# 市场数量（可信度）
total_markets = features[22] + features[23]  # 看涨+看跌市场
if total_markets >= 5:            # 足够的市场数量
    score_polymarket += 5
elif total_markets >= 3:
    score_polymarket += 3

# 净情绪强度
net_sentiment = abs(features[24])  # 净情绪绝对值
if net_sentiment > 0.3:           # 强烈的净情绪
    score_polymarket += 5
elif net_sentiment > 0.15:
    score_polymarket += 3

权重: 20%（与AI预测同等重要）

说明: Polymarket是真实资金投注的预测市场，
      反映了市场参与者的真实看法，权重较高
```

#### 6️⃣ AI综合预测维度（综合信号）
```python
score_ai = 0

# AI共识（综合了以上所有信号）
if features[29] == 1:     # AI看涨
    score_ai += 10
elif features[29] == -1:  # AI看跌
    score_ai -= 10

# AI一致性
if features[28] > 0.7:    # 70%以上一致
    score_ai += 6
elif features[28] > 0.5:
    score_ai += 3

# AI置信度
if features[25] > 70:     # 高置信度
    score_ai += 4

权重: 综合考虑
```

### 加权总分计算

```python
total_score = (
    score_cost * 0.10 +           # 成本 10%
    score_trend * 0.25 +          # 趋势 25%
    score_news * 0.20 +           # 新闻 20%
    score_sentiment * 0.15 +      # 情绪 15%
    score_polymarket * 0.20 +     # Polymarket 20% ⭐新增
    score_ai * 0.10               # AI综合 10%
)

# 归一化到0-100
total_score = max(0, min(100, (total_score + 50) * 100 / 100))
```

---

## 🛡️ 第三层: 风险评估（Risk Control）

### 风险等级判定

```python
risk_level = "LOW"

# 波动率风险
if features[7] > 0.03:
    risk_level = "HIGH"
elif features[7] > 0.015:
    risk_level = "MEDIUM"

# 价格剧烈波动风险
if abs(features[5]) > 5:
    risk_level = "HIGH"

# 市场极端情绪风险
if features[19] < 20 or features[19] > 80:
    risk_level = "HIGH"

# 数据不足风险
if features[15] < 3 and features[21] == 0:
    risk_level = "HIGH"
```

### 仓位大小建议

```python
if risk_level == "LOW":
    position_size = 0.15      # 15% 资金
elif risk_level == "MEDIUM":
    position_size = 0.08      # 8% 资金
else:  # HIGH
    position_size = 0.03      # 3% 资金
```

---

## 📤 最终决策输出

### 决策逻辑

```python
if total_score > 70 and risk_level != "HIGH":
    action = "BUY"
    confidence = total_score
    
elif total_score < 30 and risk_level != "HIGH":
    action = "SELL"
    confidence = 100 - total_score
    
else:
    action = "HOLD"
    confidence = 50
```

### 输出格式

```python
{
    "action": "BUY" | "SELL" | "HOLD",
    "confidence": 0-100,
    "total_score": 0-100,
    "risk_level": "LOW" | "MEDIUM" | "HIGH",
    "position_size": 0.03-0.15,
    "reasons": [
        "Gas费用合理 (+5分)",
        "价格温和上涨 (+8分)",
        "新闻情绪积极 (+10分)",
        "市场恐惧贪婪指数适中 (+10分)"
    ],
    "warnings": [
        "波动率较高，建议降低仓位",
        "AI预测数据缺失"
    ],
    "stop_loss": 当前价 * 0.98,
    "take_profit": 当前价 * 1.05
}
```

---

## 🎨 AI Prompt设计（LLM增强）

### 方案A: 规则引擎 + LLM验证

```python
# 第一步: 规则引擎计算初步决策
initial_decision = rule_engine.calculate(features)

# 第二步: 生成AI验证Prompt
prompt = f"""
我的交易系统基于26维市场数据分析，给出以下初步决策:

【系统建议】
操作: {initial_decision['action']}
置信度: {initial_decision['confidence']}%
风险等级: {initial_decision['risk_level']}

【数据依据】
价格: ${features[4]:,.2f}, 24h {features[5]:+.2f}%
Gas: ETH {features[0]:.2f} Gwei, BTC {features[1]} sat/vB
市场情绪: 恐惧贪婪指数 {features[19]}/100
新闻情绪: {features[15]}条新闻, 正面{features[13]:.0%}/负面{features[14]:.0%}
AI预测: {features[22]}看涨 vs {features[23]}看跌

【评分详情】
成本维度: {score_cost}/10
趋势维度: {score_trend}/25
新闻维度: {score_news}/20
情绪维度: {score_sentiment}/15
Polymarket维度: {score_polymarket}/20 ⭐新增
AI综合维度: {score_ai}/10
总分: {total_score}/100

请作为专业交易顾问:
1. 评估这个决策是否合理？
2. 有什么潜在风险？
3. 最终建议: BUY/SELL/HOLD?
"""

# 第三步: 发送给LLM
llm_response = call_llm(prompt)

# 第四步: 综合决策
if llm_response.agree_with_system:
    final_decision = initial_decision
else:
    final_decision = merge_decisions(initial_decision, llm_response)
```

### 方案B: 纯LLM决策（简化版）

```python
prompt = f"""
请基于以下市场数据给出BTC交易建议:

【交易成本】✅ 适合交易
ETH Gas: {features[0]:.2f} Gwei, BTC Fee: {features[1]} sat/vB

【价格走势】
当前: ${features[4]:,.2f}
24h: {features[5]:+.2f}%
波动率: {features[7]:.4f}
趋势: {'上涨' if features[8]==1 else '下跌' if features[8]==-1 else '平稳'}

【市场情绪】
恐惧贪婪指数: {features[19]}/100
市场情绪: {'看涨' if features[20]==1 else '看跌' if features[20]==-1 else '中性'}

【新闻分析】
总计: {features[15]}条
正面: {features[13]:.0%}, 负面: {features[14]:.0%}
情绪: {'看涨' if features[16]==1 else '看跌' if features[16]==-1 else '中性'}

【AI预测】
看涨模型: {features[22]}个
看跌模型: {features[23]}个
一致性: {features[24]:.0%}

请用JSON格式回答:
{{
  "action": "BUY/SELL/HOLD",
  "confidence": 0-100,
  "reason": "简短原因",
  "position_size": 0.05-0.15,
  "stop_loss_percent": 2-5,
  "take_profit_percent": 3-10
}}
"""
```

---

## 💡 实施建议

### 阶段1: 规则引擎（立即可用）
- ✅ 完全基于26维特征
- ✅ 确定性输出
- ✅ 可解释性强
- ✅ 无需外部API
- ⚠️ 需要持续调优规则

### 阶段2: 规则 + LLM验证（推荐）⭐
- ✅ 规则引擎快速初筛
- ✅ LLM提供第二意见
- ✅ 降低误判风险
- ⚠️ 需要LLM API调用
- ⚠️ 响应时间稍长

### 阶段3: 纯LLM决策（高级）
- ✅ 最灵活
- ✅ 能理解复杂模式
- ⚠️ 依赖LLM质量
- ⚠️ 成本较高
- ⚠️ 可解释性较弱

### 阶段4: 规则 + LLM + ML模型（最优）
- ✅ 三重验证
- ✅ 准确率最高
- ⚠️ 系统复杂
- ⚠️ 需要训练数据

---

## 📊 预期效果

### 保守估计
- 准确率: 60-70%
- 误判率: < 15%
- 风险控制: 良好

### 理想情况（优化后）
- 准确率: 75-85%
- 误判率: < 10%
- 风险控制: 优秀

---

## 🎯 下一步实施

1. **立即可做**: 实现规则引擎决策
2. **短期目标**: 集成LLM验证
3. **中期目标**: 添加ML模型
4. **长期目标**: 自适应学习系统

---

**您觉得这个方案如何？**

- 需要调整权重？
- 想先实现哪个阶段？
- 有其他想法？
