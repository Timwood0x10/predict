# 🚀 加密货币价格预测系统

使用多个AI模型（Grok, Gemini, DeepSeek）对BTC和ETH进行价格预测和对比分析。

## 📋 功能特性

- ✅ **实时数据获取**: 从Binance获取BTC和ETH的最新K线数据
- ✅ **多模型预测**: 同时使用3个AI模型进行预测
- ✅ **多时间窗口**: 支持3分钟到30分钟的多个时间窗口预测
- ✅ **结果对比**: 自动生成模型预测对比表格
- ✅ **数据持久化**: 所有数据和预测结果保存为CSV文件
- ✅ **完整日志**: 详细的日志记录便于调试和分析

## 📁 项目结构

```
crypto_price_prediction/
├── config.py                 # 配置文件（API密钥、参数设置）
├── main.py                   # 主程序入口
├── requirements.txt          # Python依赖包
├── README.md                # 项目说明文档
│
├── utils/                   # 工具模块
│   └── data_fetcher.py      # 数据获取模块（Binance API）
│
├── models/                  # AI模型模块
│   └── ai_predictor.py      # AI预测器（Grok/Gemini/DeepSeek）
│
├── data/                    # 数据目录
│   ├── kline_data.csv       # K线原始数据
│   ├── predictions.csv      # 详细预测结果
│   └── model_comparison.csv # 模型对比表格
│
└── logs/                    # 日志目录
    └── main_*.log           # 运行日志
```

## 🔧 安装和配置

### 1. 安装依赖

```bash
cd crypto_price_prediction
pip install -r requirements.txt
```

### 2. 配置API密钥

**推荐方式：创建 `.env` 文件**

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件
vim .env
```

在 `.env` 文件中添加你的API密钥：

```bash
# 至少配置一个即可（推荐DeepSeek和Gemini，都有免费额度）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxx
GROK_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxx
```

**备选方式：使用环境变量**

```bash
export DEEPSEEK_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
```

**注意**: 
- 系统会自动跳过未配置的模型
- 至少需要配置一个模型才能运行
- DeepSeek和Gemini都有免费额度，推荐优先使用

### 3. API密钥获取方式

- **Grok**: https://x.ai/ (申请API访问)
- **Gemini**: https://ai.google.dev/ (获取API密钥)
- **DeepSeek**: https://platform.deepseek.com/ (注册并获取密钥)

## 🚀 使用方法

### 快速开始

直接运行主程序：

```bash
python main.py
```

程序会自动执行以下步骤：
1. 从Binance获取BTC和ETH的最近15分钟K线数据
2. 使用3个AI模型分别预测3, 5, 8, 10, 12, 15, 30分钟后的价格
3. 保存所有数据和预测结果到CSV文件
4. 在控制台显示对比表格

### 单独测试模块

测试数据获取模块：
```bash
python utils/data_fetcher.py
```

测试AI预测模块：
```bash
python models/ai_predictor.py
```

验证配置：
```bash
python config.py
```

## 📊 输出文件说明

### 1. `data/kline_data.csv`
K线原始数据，包含字段：
- `symbol`: 交易对（BTCUSDT/ETHUSDT）
- `open_time`: 开盘时间
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量
- 等...

### 2. `data/predictions.csv`
详细预测结果，包含字段：
- `symbol`: 交易对
- `window_minutes`: 预测时间窗口
- `current_price`: 当前价格
- `timestamp`: 预测时间
- `grok_price`, `grok_confidence`, `grok_direction`: Grok预测
- `gemini_price`, `gemini_confidence`, `gemini_direction`: Gemini预测
- `deepseek_price`, `deepseek_confidence`, `deepseek_direction`: DeepSeek预测

### 3. `data/model_comparison.csv`
模型对比表格，易于阅读和分析

### 4. `logs/main_*.log`
详细的运行日志，包含所有步骤的执行信息

## 🎯 预测时间窗口

默认预测以下时间窗口（可在`config.py`中修改）：
- 3分钟
- 5分钟
- 8分钟
- 10分钟
- 12分钟
- 15分钟
- 30分钟

## ⚙️ 自定义配置

编辑 `config.py` 可以修改：

```python
# 修改交易对
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# 修改预测时间窗口
PREDICTION_WINDOWS = [5, 10, 15, 30, 60]

# 修改获取的K线数量
KLINE_LIMIT = 200

# 修改模型参数
MODEL_CONFIGS = {
    "grok": {
        "temperature": 0.3,  # 降低温度使预测更确定
        "max_tokens": 1000
    },
    ...
}
```

## 📈 使用场景

1. **短期交易参考**: 对比多个模型的预测，辅助短期交易决策
2. **模型评估**: 记录预测结果，后续对比实际价格评估模型准确性
3. **趋势分析**: 观察多个模型的预测方向，判断市场趋势
4. **研究实验**: 测试不同AI模型在价格预测任务上的表现

## ⚠️ 注意事项

1. **免责声明**: 本系统仅供学习和研究使用，预测结果不构成投资建议
2. **API限制**: 注意各AI服务的API调用频率限制和费用
3. **数据延迟**: Binance数据可能有轻微延迟
4. **预测准确性**: AI预测存在不确定性，请谨慎参考
5. **风险提示**: 加密货币投资有风险，请勿盲目依赖预测结果

## 🔍 故障排除

### 问题1: API密钥错误
```
解决: 检查config.py中的API密钥是否正确设置
```

### 问题2: 网络连接失败
```
解决: 
1. 检查网络连接
2. 确认Binance API可访问（可能需要VPN）
3. 检查防火墙设置
```

### 问题3: 模型无法提取预测结果
```
解决: 
1. 检查日志查看模型原始响应
2. 模型可能没有按格式返回JSON
3. 调整config.py中的PREDICTION_PROMPT_TEMPLATE
```

### 问题4: 依赖包安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📝 开发计划

- [ ] 添加更多交易对支持
- [ ] 实现预测结果回测功能
- [ ] 添加Web界面展示
- [ ] 支持实时流式预测
- [ ] 集成更多AI模型
- [ ] 添加技术指标分析
- [ ] 实现预测准确率统计

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题或建议，请通过GitHub Issues联系。

---

**Happy Trading! 🎉**

*记住: 投资有风险，入市需谨慎！*
