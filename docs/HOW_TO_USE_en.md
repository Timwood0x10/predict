# 🎯 Usage Guide - Quick Start

## 📋 File Description

You now have **3 ways** to use this system:

| File | Suitable Scenario | Features |
|------|-------------------|----------|
| `run_trading_analysis.sh` | Complete Analysis | ⭐**Recommended**, analyze BTC+ETH simultaneously with comprehensive comparison |
| `quick_trade.sh` | Quick Analysis | Concise, single coin quick analysis |
| `advanced_trading_system.py` | Custom | Direct command-line call, most flexible |

---

## 🚀 Method 1: Complete Analysis (Recommended)

### Usage

```bash
bash run_trading_analysis.sh
```

### Default Configuration

- Capital: 1000 USDT
- Leverage: 10x
- Risk: 2%
- Stop Loss: 2%
- Coins: **BTC + ETH** (simultaneous analysis)

### Modify Parameters

```bash
# Edit script
nano run_trading_analysis.sh

# Modify these lines (at the top of the file)
CAPITAL=1000                    # Change to your capital
LEVERAGE=10                     # Change to your desired leverage
RISK=2.0                        # Change to your risk tolerance
STOP_LOSS=2.0                   # Change to your stop loss percentage
SYMBOLS="BTCUSDT ETHUSDT"       # Change to the coins you want to analyze
```

### Output Example

```
================================================================================
📊 [1/2] Analyzing BTCUSDT
================================================================================
Current Price: $110,667
Decision: 🔴 Short (72% confidence)

================================================================================
📊 [2/2] Analyzing ETHUSDT
================================================================================
Current Price: $3,933
Decision: ⚪ Hold (50% confidence)

================================================================================
📊 Comprehensive Comparison Analysis
================================================================================
Decision Statistics:
  🟢 Long: 0 coins
  🔴 Short: 1 coin
  ⚪ Hold: 1 coin

💡 Trading Suggestions:
  ✅ Short opportunity available, prioritize high-confidence coins (BTC)
```

---

## ⚡ Method 2: Quick Analysis

### Usage

```bash
bash quick_trade.sh
```

### Default Configuration

- Capital: 1000 USDT
- Leverage: 10x
- Risk: 2%
- Stop Loss: 2%
- Coin: **BTC** (single coin)

### Modify Parameters

```bash
# Edit script
nano quick_trade.sh

# Only need to modify these 5 lines
CAPITAL=1000
LEVERAGE=10
RISK=2.0
STOP_LOSS=2.0
SYMBOL=BTCUSDT
```

---

## 🎮 Method 3: Direct Command Line Call

### Usage

```bash
python advanced_trading_system.py \
  --capital 1000 \
  --leverage 10 \
  --risk 2.0 \
  --stop-loss 2.0 \
  --symbol BTCUSDT
```

### Analyze Multiple Coins

```bash
# Analyze BTC
python advanced_trading_system.py --symbol BTCUSDT

# Analyze ETH
python advanced_trading_system.py --symbol ETHUSDT

# Analyze SOL
python advanced_trading_system.py --symbol SOLUSDT
```

---

## 📊 Parameter Details

### CAPITAL (Capital)
- **Meaning**: How much USDT you invest
- **Recommended**: 1000-5000
- **Example**: `CAPITAL=1000`

### LEVERAGE (Leverage)
- **Meaning**: How many times to amplify
- **Recommended**: 5-10x (beginners)
- **Risk**: 10x leverage = 10% adverse price movement = liquidation
- **Example**: `LEVERAGE=10`

### RISK (Risk Percentage)
- **Meaning**: Maximum % loss per trade
- **Recommended**: 1-2%
- **Calculation**: 1000U × 2% = maximum loss of 20U
- **Example**: `RISK=2.0`

### STOP_LOSS (Stop Loss Percentage)
- **Meaning**: Stop loss when price reverses by %
- **Recommended**: 2%
- **Impact**: Smaller stop loss = larger position
- **Example**: `STOP_LOSS=2.0`

### SYMBOLS (Trading Pairs)
- **Meaning**: Which coins to analyze
- **Format**: COIN+USDT (uppercase)
- **Examples**:
  - Single: `SYMBOL=BTCUSDT`
  - Multiple: `SYMBOLS="BTCUSDT ETHUSDT"`
  - More: `SYMBOLS="BTCUSDT ETHUSDT BNBUSDT SOLUSDT"`

---

## 🎯 Common Scenarios

### Scenario 1: I'm a beginner, want to be conservative

```bash
# Edit run_trading_analysis.sh
CAPITAL=500          # Small capital
LEVERAGE=5           # Low leverage
RISK=1.0             # Low risk
STOP_LOSS=2.0        # Standard stop loss
SYMBOLS="BTCUSDT"    # Only analyze BTC
```

### Scenario 2: Standard Trading (Recommended)

```bash
# Default configuration works fine
bash run_trading_analysis.sh
```

### Scenario 3: I want to analyze more coins

```bash
# Edit run_trading_analysis.sh
SYMBOLS="BTCUSDT ETHUSDT BNBUSDT SOLUSDT"
```

### Scenario 4: High Leverage Aggressive Strategy

```bash
# Edit run_trading_analysis.sh
CAPITAL=2000         # Larger capital
LEVERAGE=20          # High leverage (dangerous!)
RISK=2.0             # Standard risk
STOP_LOSS=1.5        # Tight stop loss
```

---

## 📖 Output Interpretation

### Final Decision

- **🟢 LONG**: Suggest buy, profit from price increase
- **🔴 SHORT**: Suggest sell, profit from price decrease
- **⚪ HOLD**: Signal unclear, not recommended to operate

### Confidence

- **>70%**: Strong signal, consider operating
- **50-70%**: Medium signal, operate cautiously
- **<50%**: Weak signal, recommend waiting

### Position Management

```
Margin: 100 USDT (10%)     ← Actual occupied capital
Position Value: 1000 USDT  ← Total controlled capital (margin × leverage)
Stop Loss: $112,881 (+2.0%)     ← Stop loss when price rises here
Max Loss: 20 USDT (2% capital) ← Actual loss when stop loss triggered

Take Profit Plan:
  TP1: $106,240 (-4%, 2:1) → Close 50%  ← Price drops 4%, close half position
  TP2: $104,027 (-6%, 3:1) → Close 30%  ← Price drops 6%, close another 30%
  TP3: $101,814 (-8%, 4:1) → Close 20%  ← Price drops 8%, close remaining 20%
```

---

## ⚠️ Important Reminders

### ✅ Recommended Practices

1. ✅ Test with small capital first (100-500U)
2. ✅ Use low leverage (5-10x)
3. ✅ Strictly execute stop loss
4. ✅ Take profit in batches
5. ✅ Don't overweight

### ❌ Avoid Mistakes

1. ❌ Don't use excessive leverage (>20x)
2. ❌ Don't set stop loss too small (easily triggered)
3. ❌ Don't move stop loss
4. ❌ Don't be greedy (close at take profit)
5. ❌ Don't trade emotionally

### 🔴 Risk Warning

- Higher leverage = easier liquidation
- 10x leverage: 10% adverse price = liquidation
- 20x leverage: 5% adverse price = liquidation
- 50x leverage: 2% adverse price = liquidation

---

## 🆘 Frequently Asked Questions

**Q: Script stuck?**
A: Wait 1-2 minutes, might be fetching news data

**Q: How to modify parameters?**
A: Use `nano` or `vim` to edit script files

**Q: Can analyze multiple coins simultaneously?**
A: Yes! Modify `SYMBOLS="BTCUSDT ETHUSDT BNBUSDT"`

**Q: Stop loss price unreasonable?**
A: Adjust `STOP_LOSS` parameter (recommended 1.5-3%)

**Q: Safety check failed?**
A: Check if capital > 100, or if data fetching succeeded

---

## 📚 More Documentation

Need detailed understanding? Check:

- `QUICK_START.md` - Quick start (1-minute setup)
- `PARAMETERS_GUIDE.md` - Parameter details (with calculation examples)
- `docs/ADVANCED_SYSTEM_GUIDE.md` - Advanced usage guide
- `docs/FINAL_SUMMARY.md` - Complete summary

---

## 🎉 Getting Started

### First Time Use (Recommended Flow)

```bash
# 1. Check quick start
cat QUICK_START.md

# 2. Run default analysis (BTC+ETH)
bash run_trading_analysis.sh

# 3. If want to modify parameters
nano run_trading_analysis.sh

# 4. Run again
bash run_trading_analysis.sh
```

---

**Happy Trading! Remember: This is an assistance tool, not a holy grail. Strict risk control, cautious operation!** 🚀