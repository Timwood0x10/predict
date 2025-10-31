# 🤖 Cryptocurrency Trading Decision System

> A trading assistance decision system based on real market data, supporting dual-direction trading (long/short) and leveraged trading

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Project Introduction

This is a **trading assistance decision system**, not an automated trading bot. It provides reference suggestions for traders by collecting and analyzing multi-dimensional market data.

### ⚠️ Important Disclaimer

- ❌ **No Profit Guarantee** - This is an assistance tool, not a holy grail
- ❌ **Cannot Predict Future** - Based on historical and current data analysis
- ❌ **Requires Human Judgment** - Suggestions are for reference only, combine with your own judgment
- ✅ **Risk at Your Own Risk** - Cryptocurrency trading has high risks, please use with caution

---

## ✨ Core Features

### 1. Real Data Collection

The system obtains **real data** from the following sources:

| Data Type | Data Source | Update Frequency |
|-----------|-------------|------------------|
| 📈 **K-line Data** | Binance API | Real-time |
| 💰 **Gas Fees** | Etherscan + Mempool.space | Real-time |
| 📰 **News** | NewsAPI + CryptoCompare + Odaily | Hourly |
| 😊 **Market Sentiment** | Fear & Greed Index | Hourly |

**Note**: The AI prediction part currently uses algorithms based on market sentiment and has not integrated real LLM APIs.

### 2. Decision Strategy

The system adopts a **three-layer verification framework**:

```
Layer 1: Safety Checks (5 prerequisite conditions)
    ├─ Are gas fees reasonable
    ├─ Is data complete
    ├─ Is market extreme
    ├─ Is volatility controllable
    └─ Is account status normal
    
Layer 2: Multi-dimensional Scoring (4 dimensions)
    ├─ 📰 News Signals (30% weight)
    ├─ 📈 Price Signals (25% weight)
    ├─ 😊 Sentiment Signals (25% weight)
    └─ 🤖 AI Signals (20% weight)
    
Layer 3: Final Decision
    ├─ Long: Score ≥63 + AI support
    ├─ Short: Score ≤57 + AI support
    └─ Hold: Other cases
```

### 3. Trading Strategies

Built-in 5 classic trading strategies:

| Strategy | Applicable Scenarios | Implementation Status |
|----------|---------------------|----------------------|
| Trend Following | Clear uptrend or downtrend | ✅ Implemented |
| Mean Reversion | Price deviates from mean | ✅ Implemented |
| Breakout Strategy | Breaks key support/resistance | ✅ Implemented |
| Grid Strategy | Ranging market | ✅ Implemented |
| Scalping | Short-term rapid trading | ✅ Implemented |

The **AI Decision Layer** automatically selects the most suitable strategy based on market conditions.

### 4. Risk Management

- **Fixed Risk Ratio**: Fixed risk per trade (default 2% of capital)
- **Dynamic Stop Loss/Take Profit**: Calculated based on volatility and risk-reward ratio
- **Leverage Position Calculation**: Scientific position management considering leverage multiplier
- **Batch Take Profit**: Three-tier take profit (2:1, 3:1, 4:1 risk-reward ratio)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env file, add API keys
nano .env
```

Required API keys:
- `NEWSAPI_KEY` - News data (optional, news analysis will be skipped if not set)
- Other APIs are free, no configuration needed

### 3. Run Analysis

```bash
# One-click analysis of BTC and ETH (recommended)
bash run_trading_analysis.sh
```

**It's that simple!**

---

## 📊 Usage Examples

### Default Analysis

```bash
bash run_trading_analysis.sh
```

**Default Configuration**:
- Capital: 1000 USDT
- Leverage: 10x
- Risk: 2%
- Stop Loss: 2%
- Coins: BTC + ETH

### Custom Parameters

```bash
# Edit script
nano run_trading_analysis.sh

# Modify these parameters
CAPITAL=1000                    # Your capital
LEVERAGE=10                     # Leverage multiplier
RISK=2.0                        # Risk ratio (%)
STOP_LOSS=2.0                   # Stop loss ratio (%)
SYMBOLS="BTCUSDT ETHUSDT"       # Coins to analyze
```

### Output Example

```
================================================================================
📊 [1/2] Analyzing BTCUSDT
================================================================================
Current Price: $110,667

【Decision Result】
  🔴 Action: SHORT (Short)
  Confidence: 72%
  Reason: AI suggests short + Engine support (10x leverage)

【Position Management】
  Leverage: 10x
  Capital: 1000 USDT
  Margin: 100 USDT (10%)
  Stop Loss: $112,881 (+2%)
  Take Profit 1: $106,240 (-4%, 2:1) → Close 50%
  Take Profit 2: $104,027 (-6%, 3:1) → Close 30%
  Take Profit 3: $101,814 (-8%, 4:1) → Close 20%

================================================================================
📊 Comprehensive Comparison Analysis
================================================================================
  🔴 BTCUSDT    SHORT
  ⚪ ETHUSDT    HOLD

💡 Trading Suggestions:
  ✅ Short opportunity available, prioritize high-confidence coins (BTC)
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [HOW_TO_USE.md](HOW_TO_USE.md) | Complete Usage Guide ⭐**Recommended** |
| [QUICK_START.md](QUICK_START.md) | Quick Start (1-minute setup) |
| [PARAMETERS_GUIDE.md](PARAMETERS_GUIDE.md) | Detailed Parameter Description |
| [docs/AI_DECISION_STRATEGY.md](docs/AI_DECISION_STRATEGY.md) | AI Decision Strategy Design |
| [docs/FINAL_SUMMARY.md](docs/FINAL_SUMMARY.md) | Complete Project Summary |
| [PROJECT_FILES.md](PROJECT_FILES.md) | File Structure Description |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Collection Layer                    │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Gas Fee Monitor│ K-line Data   │ News Aggregation│ Market Sentiment │
│ GasFeeMonitor│ DataFetcher  │ NewsAPI     │ SentimentAnalyzer│
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       └──────────────┴──────────────┴────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Data Integrator│
                    │ DataIntegrator │
                    │  (26-dim features)│
                    └───────┬────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
        ┌───────▼────────┐      ┌──────▼──────┐
        │  AI Decision    │      │ Decision   │
        │   Layer         │      │   Engine    │
        │(Strategy Select)│      │(Risk Assess)│
        └───────┬────────┘      └──────┬──────┘
                │                       │
                └───────────┬───────────┘
                            │
                    ┌───────▼────────┐
                    │  Final Decision │
                    │ LONG/SHORT/HOLD│
                    └────────────────┘
```

---

## 🔧 Core Components

### Data Layer
- `utils/gas_monitor.py` - Gas fee monitoring
- `utils/data_fetcher.py` - Binance data fetching
- `utils/financial_news.py` - News aggregation
- `utils/news_processor.py` - News deep processing
- `utils/sentiment_analyzer.py` - Market sentiment analysis
- `utils/data_integrator.py` - Data integration (26-dim features)

### Decision Layer
- `ai_decision_layer.py` - AI intelligent decision layer
- `utils/decision_engine.py` - Decision engine (three-layer verification)

### Strategy Layer
- `strategies/trend_following.py` - Trend following
- `strategies/mean_reversion.py` - Mean reversion
- `strategies/breakout_strategy.py` - Breakout strategy
- `strategies/grid_strategy.py` - Grid strategy
- `strategies/scalping_strategy.py` - Scalping strategy

### Application Layer
- `real_trading_decision.py` - Dual-coin comparative analysis
- `advanced_trading_system.py` - Advanced leveraged trading system
- `run_trading_analysis.sh` - Main usage script

---

## 📊 Data Processing Flow

### 26-Dimensional Feature Vector

The system integrates market data into a 26-dimensional feature vector:

```python
[0-3]   Gas Fee Features (4 dims)
  ├─ ETH Gas price
  ├─ BTC Fee price
  ├─ ETH suitable for trading
  └─ BTC suitable for trading

[4-11]  Price Features (8 dims)
  ├─ Current price
  ├─ Price change rate
  ├─ Average volume
  ├─ Volatility
  ├─ Trend direction
  ├─ Highest price
  ├─ Lowest price
  └─ Price range

[12-16] News Features (5 dims)
  ├─ News sentiment score
  ├─ Positive news ratio
  ├─ Negative news ratio
  ├─ News count
  └─ News sentiment label

[17-20] Market Sentiment Features (4 dims)
  ├─ Market sentiment score
  ├─ Market confidence
  ├─ Fear & Greed Index
  └─ Market sentiment label

[21-25] AI Prediction Features (5 dims)
  ├─ AI average confidence
  ├─ Bullish model count
  ├─ Bearish model count
  ├─ AI agreement ratio
  └─ AI consensus direction
```

---

## ⚙️ Configuration Parameters

| Parameter | Description | Default | Recommended Range |
|-----------|-------------|---------|-------------------|
| `CAPITAL` | Investment capital (USDT) | 1000 | 100-10000 |
| `LEVERAGE` | Leverage multiplier | 10 | 5-20 |
| `RISK` | Single trade risk ratio (%) | 2.0 | 1.0-3.0 |
| `STOP_LOSS` | Stop loss ratio (%) | 2.0 | 1.5-3.0 |
| `SYMBOLS` | Trading pair list | "BTCUSDT ETHUSDT" | Any Binance trading pair |

### Risk Level Reference

| Leverage | Liquidation Distance | Risk Level |
|----------|---------------------|------------|
| 5x | 20% | 🟢 Low Risk |
| 10x | 10% | 🟡 Medium Risk |
| 20x | 5% | 🔴 High Risk |
| 50x | 2% | ⚫ Dangerous |

---

## 🧪 Testing

```bash
# Run decision engine tests
python -m pytest tests/test_decision_engine.py -v

# Run strategy tests
python -m pytest tests/test_strategies.py -v

# Run all tests
python -m pytest tests/ -v
```

**Test Coverage**:
- Decision Engine: 8 core scenarios
- Trading Strategies: 25 test cases
- Coverage: >80%

---

## 🔐 Data Privacy

- ✅ All market data obtained through public APIs
- ✅ No personal information collected
- ✅ No trading data uploaded to servers
- ✅ Completely local operation

---

## ⚠️ Risk Warning

### Market Risks
- Cryptocurrency market **extremely volatile**
- Prices can change significantly in short time
- Past performance **does not represent future results**

### Leverage Risks
- Leverage amplifies profits, **also amplifies losses**
- 10x leverage: 10% adverse price movement leads to liquidation
- Beginners recommended to use **low leverage** (5-10x)

### System Limitations
- ❌ Cannot predict black swan events
- ❌ Cannot respond to sudden news
- ❌ Cannot guarantee 100% accuracy
- ❌ Depends on data source stability

### Usage Recommendations
1. ✅ Test with small capital first
2. ✅ Strictly execute stop loss
3. ✅ Don't overweight single coins
4. ✅ Take profit in batches, don't be greedy
5. ✅ Stay rational, avoid emotional trading

---

## 📈 Actual Performance

**Disclaimer**: The following data are system test results only and do not represent actual trading performance.

### Test Environment
- Time: 2025-10-30
- Coins: BTC, ETH
- Period: 12 hours
- Strategy: Trend Following + Mean Reversion

### Decision Accuracy
- Safety check pass rate: 95%
- Signal consistency: 75%
- Trend recognition accuracy: ~70% (estimated)

**Note**: Actual performance is affected by market conditions, parameter settings, execution timing, and other factors.

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

### Contribution Areas
- 🐛 Bug fixes
- ✨ New feature suggestions
- 📚 Documentation improvements
- 🧪 Test cases
- 🌐 Multi-language support

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 👨‍💻 Author

Anonymous who prefers not to disclose name
---

## 🙏 Acknowledgments

Thanks to the following open source projects and data providers:

- [Binance API](https://binance-docs.github.io/apidocs/) - K-line data
- [Etherscan API](https://etherscan.io/apis) - ETH Gas data
- [Mempool.space API](https://mempool.space/docs/api) - BTC Fee data
- [NewsAPI](https://newsapi.org/) - News data
- [Alternative.me](https://alternative.me/crypto/fear-and-greed-index/) - Fear & Greed Index
- [CryptoCompare](https://www.cryptocompare.com/) - Cryptocurrency news
- [Odaily](https://www.odaily.news/) - Chinese cryptocurrency news

---

## 📞 Contact

For questions or suggestions, feel free to contact through:

- 💬 Issue: [GitHub Issues](https://github.com/Timwood0x10/predict/issues)

---

## 🎓 Learning Resources

Recommended learning resources:

- [Binance Academy](https://academy.binance.com/) - Cryptocurrency basics
- [Investopedia](https://www.investopedia.com/) - Trading and investment education
- [TradingView](https://www.tradingview.com/) - Technical analysis learning

---

**Final Reminder**: Trading involves risks, enter the market with caution! This system is only an assistance tool and does not constitute investment advice. Please use it with full understanding of the risks.

**Happy Trading!** 🚀