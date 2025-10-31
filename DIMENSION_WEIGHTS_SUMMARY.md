# 交易系统维度与权重总结

## 📊 完整维度（35维）

### 原有26维

#### Gas费用（4维）
- eth_gas_gwei: ETH Gas费 [权重1.0]
- btc_fee_sat: BTC交易费 [权重1.0]
- eth_tradeable: 可交易性 [权重1.0]
- btc_tradeable: 可交易性 [权重1.0]

#### K线价格（8维）
- current_price: 当前价格 [权重1.2]
- price_change_pct: 价格变化率 [权重1.3] ⭐
- avg_volume: 平均成交量 [权重1.0]
- volatility: 波动率 [权重1.2]
- trend: 趋势方向 [权重1.3] ⭐
- high_price: 最高价 [权重1.0]
- low_price: 最低价 [权重1.0]
- price_range_pct: 价格区间 [权重1.1]

#### 新闻情绪（5维）
- news_score: 新闻评分 [权重1.2]
- news_pos_ratio: 正面比例 [权重1.1]
- news_neg_ratio: 负面比例 [权重1.1]
- news_count: 新闻数量 [权重1.0]
- news_sentiment: 情绪标签 [权重1.2]

#### 市场情绪（4维）
- market_sentiment_score: 情绪评分 [权重1.3] ⭐
- market_confidence: 市场信心 [权重1.2]
- fear_greed_index: 恐惧贪婪指数 [权重1.4] ⭐⭐
- market_sentiment_label: 情绪标签 [权重1.3] ⭐

#### AI预测（5维）
- ai_avg_confidence: 平均置信度 [权重1.3] ⭐
- ai_up_count: 看涨数 [权重1.2]
- ai_down_count: 看跌数 [权重1.2]
- ai_agreement_ratio: 一致性 [权重1.4] ⭐⭐
- ai_consensus: 共识 [权重1.4] ⭐⭐

---

### 新增9维 ✨

#### 订单簿深度（3维）
- orderbook_imbalance: 买卖盘失衡 [-1~1] [权重1.2]
- support_strength: 支撑强度 [0-100] [权重1.2]
- resistance_strength: 阻力强度 [0-100] [权重1.2]

#### 宏观经济（4维）
- dxy_change: 美元指数变化 [-10~10%] [权重1.1]
- sp500_change: 美股变化 [-10~10%] [权重1.3] ⭐
- vix_level: VIX恐慌指数 [10-80] [权重1.3] ⭐
- risk_appetite: 风险偏好 [0-100] [权重1.4] ⭐⭐

#### 期货数据（2维）
- oi_change: OI变化率 [-50~50%] [权重1.2]
- funding_trend: 资金费率趋势 [-1~1] [权重1.3] ⭐

---

## 🎯 动态权重（市场状态）

### 牛市配置
```
情绪类: 1.3x (更可靠)
订单簿: 1.2x (买盘强)
新闻: 1.2x
AI: 1.3x
宏观: 0.8x (影响小)
```

### 熊市配置
```
宏观: 1.4x (主导)
风险: 1.3x
VIX: 1.4x
期货: 1.2x
情绪: 0.7x (易误导)
```

### 震荡配置
```
技术: 1.3x
订单簿: 1.2x
支撑阻力: 1.3x
其他: 1.0x
```

---

## 📈 Top 10 最重要维度

1. fear_greed_index [1.4] - 市场总体情绪
2. ai_consensus [1.4] - AI共识
3. ai_agreement_ratio [1.4] - AI一致性
4. risk_appetite [1.4] - 风险偏好
5. price_change_pct [1.3] - 价格趋势
6. trend [1.3] - 趋势方向
7. market_sentiment_score [1.3] - 市场情绪
8. sp500_change [1.3] - 美股
9. vix_level [1.3] - 恐慌
10. funding_trend [1.3] - 资金费率

---

**总维度: 35维（26+9）**
**预期提升: 25-30%**
**原则: 数据辅助AI，不束缚决策**
