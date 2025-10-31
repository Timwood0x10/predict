# 📋 Detailed Parameter Guide

## Quick Usage

```bash
# Method 1: Use detailed script (with warnings and confirmations)
bash run_trading_analysis.sh

# Method 2: Use quick script (concise version)
bash quick_trade.sh

# Method 3: Direct command line
python advanced_trading_system.py --capital 1000 --leverage 10 --risk 2.0 --stop-loss 2.0 --symbol BTCUSDT
```

---

## 📊 Parameter Details

### 1. 💰 CAPITAL (Capital)

**Meaning**: How much USDT you're prepared to invest in trading

**Range**: Any positive number

**Recommendations**:
- Testing: 100-500 USDT
- Real trading: 1000-5000 USDT
- Large capital: >5000 USDT

**Examples**:
```bash
CAPITAL=1000    # Invest 1000 USDT
CAPITAL=5000    # Invest 5000 USDT
```

**Calculation Impact**:
- Larger capital = larger position
- Maximum single loss = Capital × Risk percentage

---

### 2. 📊 LEVERAGE (Leverage Multiplier)

**Meaning**: How many times to amplify trading funds

**Range**: 1-125 (depends on exchange)

**Risk Levels**:

| Leverage | Liquidation Distance | Risk Level | Suitable For |
|----------|---------------------|------------|--------------|
| 1x | 100% | 🟢 No risk | Spot trading |
| 2-5x | 20-50% | 🟢 Low risk | Beginners |
| 5-10x | 10-20% | 🟡 Medium risk | Intermediate |
| 10-20x | 5-10% | 🟠 High risk | Experienced |
| 20-50x | 2-5% | 🔴 Very high risk | Professional |
| >50x | <2% | ⚫ Dangerous | Not recommended |

**Liquidation Distance Calculation**:
```
Liquidation Distance ≈ 100% / Leverage Multiplier
```

**Examples**:
```bash
LEVERAGE=1     # 1x leverage (equivalent to spot)
LEVERAGE=5     # 5x leverage (conservative)
LEVERAGE=10    # 10x leverage (balanced)
LEVERAGE=20    # 20x leverage (aggressive)
```

**Important Notes**:
- ⚠️ Higher leverage = easier liquidation
- ⚠️ 10x leverage: 10% adverse price = liquidation
- ⚠️ 20x leverage: 5% adverse price = liquidation
- ⚠️ 50x leverage: 2% adverse price = liquidation

---

### 3. ⚠️ RISK (Risk Percentage)

**Meaning**: Maximum loss percentage of capital willing to bear per trade

**Range**: 0.5-5.0%

**Recommended Values**:

| Risk | Consecutive Stop Losses | Style | Suitable For |
|------|-----------------------|-------|--------------|
| 0.5% | 200 times | 🟢 Ultra conservative | Long-term stability |
| 1.0% | 100 times | 🟢 Conservative | Beginners |
| 1.5% | 67 times | 🟡 Balanced | Intermediate |
| 2.0% | 50 times | 🟡 Standard | **Recommended** |
| 2.5% | 40 times | 🟠 Aggressive | Experienced |
| 3.0% | 33 times | 🔴 Very aggressive | Professional |
| 5.0% | 20 times | ⚫ Dangerous | Not recommended |

**Examples**:
```bash
RISK=1.0    # Maximum 1% loss per trade (conservative)
RISK=2.0    # Maximum 2% loss per trade (recommended)
RISK=3.0    # Maximum 3% loss per trade (aggressive)
```

**Actual Loss Calculation**:
```
Capital = 1000 USDT
Risk = 2.0%
Maximum single loss = 1000 × 2% = 20 USDT
```

**Consecutive Stop Loss Impact**:
```
Risk 2%, 10 consecutive stop losses = 20% capital loss
Risk 3%, 10 consecutive stop losses = 30% capital loss
```

---

### 4. 🛑 STOP_LOSS (Stop Loss Percentage)

**Meaning**: Stop loss when price moves adversely by what percentage

**Range**: 0.5-5.0%

**Recommended Values**:

| Stop Loss | Characteristics | Pros | Cons |
|-----------|-----------------|------|------|
| 0.5-1.0% | 🔴 Very tight | Quick stop loss | Easily triggered |
| 1.5% | 🟠 Tight | Protect profits | Sometimes premature |
| 2.0% | 🟡 Balanced | **Recommended** | Reasonable |
| 2.5-3.0% | 🟢 Loose | Give space | Larger loss |
| >3.0% | ⚫ Too loose | Much space | Very high risk |

**Examples**:
```bash
STOP_LOSS=1.5    # Stop loss at 1.5% adverse price (tight)
STOP_LOSS=2.0    # Stop loss at 2.0% adverse price (recommended)
STOP_LOSS=3.0    # Stop loss at 3.0% adverse price (loose)
```

**Stop Loss and Position Relationship**:
```
Smaller stop loss → Larger position → Concentrated risk
Larger stop loss → Smaller position → Diversified risk

For example:
Capital 1000U, risk 2%, stop loss 1% → Position ~2000U
Capital 1000U, risk 2%, stop loss 2% → Position ~1000U
Capital 1000U, risk 2%, stop loss 3% → Position ~667U
```

**Automatic Take Profit Calculation**:
```
Stop loss 2%, then:
- Take profit 1 = 4%  (2:1 risk-reward ratio)
- Take profit 2 = 6%  (3:1 risk-reward ratio)
- Take profit 3 = 8%  (4:1 risk-reward ratio)
```

---

### 5. 🪙 SYMBOL (Trading Pair)

**Meaning**: Which coin to analyze

**Format**: Coin name + USDT (must be uppercase)

**Common Trading Pairs**:

| Trading Pair | Coin | Market Cap Rank | Volatility |
|-------------|------|----------------|------------|
| BTCUSDT | Bitcoin | #1 | 🟡 Medium |
| ETHUSDT | Ethereum | #2 | 🟡 Medium |
| BNBUSDT | Binance Coin | #4 | 🟠 Higher |
| SOLUSDT | Solana | #5 | 🔴 High |
| XRPUSDT | Ripple | #6 | 🟡 Medium |
| ADAUSDT | Cardano | #8 | 🟠 Higher |
| DOGEUSDT | Dogecoin | #9 | 🔴 High |
| AVAXUSDT | Avalanche | #10 | 🔴 High |
| MATICUSDT | Polygon | - | 🔴 High |
| DOTUSDT | Polkadot | - | 🟠 Higher |

**Examples**:
```bash
SYMBOL=BTCUSDT     # Analyze Bitcoin
SYMBOL=ETHUSDT     # Analyze Ethereum
SYMBOL=SOLUSDT     # Analyze Solana
```

**Selection Recommendations**:
- Beginners: BTC, ETH (low volatility, good liquidity)
- Intermediate: BNB, XRP, ADA (mainstream coins)
- Experienced: SOL, AVAX, DOGE (high volatility)

---

## 💡 Parameter Combination Suggestions

### Combination 1: Beginner Conservative Strategy
```bash
CAPITAL=500         # Small capital for testing
LEVERAGE=3          # Low leverage
RISK=1.0            # Low risk
STOP_LOSS=2.0       # Standard stop loss
SYMBOL=BTCUSDT      # Stable coin
```
**Features**: Safe, stable, suitable for learning

---

### Combination 2: Balanced Strategy (Recommended)
```bash
CAPITAL=1000        # Standard capital
LEVERAGE=10         # Medium leverage
RISK=2.0            # Standard risk
STOP_LOSS=2.0       # Standard stop loss
SYMBOL=BTCUSDT      # Mainstream coin
```
**Features**: Controlled risk, reasonable returns

---

### Combination 3: Aggressive Strategy
```bash
CAPITAL=2000        # Larger capital
LEVERAGE=20         # High leverage
RISK=2.5            # Higher risk
STOP_LOSS=1.5       # Tight stop loss
SYMBOL=ETHUSDT      # Mainstream coin
```
**Features**: High returns, high risk

---

### Combination 4: Short-term Trading
```bash
CAPITAL=1000        # Standard capital
LEVERAGE=15         # Higher leverage
RISK=1.5            # Medium risk
STOP_LOSS=1.0       # Tight stop loss
SYMBOL=BTCUSDT      # Good liquidity
```
**Features**: Quick in and out

---

## 📊 Example Calculations

### Example 1: Standard Configuration
```bash
Capital: 1000 USDT
Leverage: 10x
Risk: 2%
Stop Loss: 2%
```

**Calculation Results**:
```
Effective funds = 1000 × 10 = 10,000 USDT
Single trade risk = 1000 × 2% = 20 USDT
Assume BTC price = 100,000 USDT

Position calculation:
Position size = 20 / (100,000 × 2%) = 0.01 BTC
Position value = 0.01 × 100,000 = 1,000 USDT
Margin = 1,000 / 10 = 100 USDT (10% of capital)

Stop loss and take profit:
Entry: 100,000
Stop loss: 98,000 (-2%)
Take profit 1: 104,000 (+4%, 2:1)
Take profit 2: 106,000 (+6%, 3:1)
Take profit 3: 108,000 (+8%, 4:1)

Risk and reward:
Maximum loss: 20 USDT (2% of capital)
Expected profit: 40-80 USDT (4-8% of capital)
```

---

### Example 2: High Leverage Configuration
```bash
Capital: 1000 USDT
Leverage: 20x
Risk: 2%
Stop Loss: 1.5%
```

**Calculation Results**:
```
Effective funds = 1000 × 20 = 20,000 USDT
Single trade risk = 1000 × 2% = 20 USDT
Liquidation distance ≈ 5%

Position calculation:
Position size = 20 / (100,000 × 1.5%) = 0.0133 BTC
Position value = 0.0133 × 100,000 = 1,333 USDT
Margin = 1,333 / 20 = 66.7 USDT (6.7% of capital)

Stop loss and take profit:
Entry: 100,000
Stop loss: 98,500 (-1.5%)
Take profit 1: 103,000 (+3%, 2:1)
Take profit 2: 104,500 (+4.5%, 3:1)
Take profit 3: 106,000 (+6%, 4:1)

⚠️ Warning: 5% adverse price will cause liquidation!
```

---

## ⚠️ Important Reminders

### ✅ Recommended Practices
1. ✅ Start with small capital
2. ✅ Use low leverage (5-10x)
3. ✅ Control risk within 2%
4. ✅ Strictly execute stop loss
5. ✅ Take profit in batches

### ❌ Avoid Mistakes
1. ❌ Don't use excessive leverage (>20x)
2. ❌ Don't set too high risk (>3%)
3. ❌ Don't move stop loss
4. ❌ Don't overweight one coin
5. ❌ Don't trade emotionally

---

## 🔧 Quick Modification Guide

### Parameter Modification Steps

1. **Open script**
```bash
nano quick_trade.sh
# or
vim quick_trade.sh
```

2. **Modify parameters**
```bash
# For example, change to conservative strategy
CAPITAL=500
LEVERAGE=5
RISK=1.0
STOP_LOSS=2.0
SYMBOL=BTCUSDT
```

3. **Save and run**
```bash
bash quick_trade.sh
```

---

## 📞 Usage Help

If you encounter problems, check:
1. Python is installed (python --version)
2. Dependencies are installed (pip install -r requirements.txt)
3. Network is normal
4. Parameter format is correct

---

**Happy Trading!** 🎉