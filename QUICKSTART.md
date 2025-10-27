# ⚡ 快速启动指南

## 🚀 5分钟快速上手

### 步骤1: 安装依赖 (30秒)
```bash
cd crypto_price_prediction
pip install -r requirements.txt
```

### 步骤2: 配置API密钥 (2分钟)

**推荐方法: 创建 .env 文件**
```bash
# 在项目根目录创建 .env 文件
cd crypto_price_prediction
cp .env.example .env
vim .env
```

在 `.env` 文件中添加你的API密钥：
```bash
# 至少配置一个即可（推荐DeepSeek，有免费额度）
DEEPSEEK_API_KEY=your-deepseek-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
GROK_API_KEY=your-grok-api-key-here
```

**备选方法: 直接设置环境变量**
```bash
export DEEPSEEK_API_KEY="你的密钥"
export GEMINI_API_KEY="你的密钥"
```

### 步骤3: 测试系统 (30秒)
```bash
python test_system.py
```
看到 ✓ 表示测试通过！

### 步骤4: 运行预测 (2分钟)
```bash
python main.py
```

就这么简单！ 🎉

---

## 📊 查看结果

程序运行完成后，查看生成的文件：

```bash
# 查看K线数据
cat data/kline_data.csv

# 查看预测结果
cat data/predictions.csv

# 查看对比表格
cat data/model_comparison.csv

# 查看日志
tail -f logs/main_*.log
```

---

## 🔑 获取API密钥

### Grok (X.AI)
1. 访问 https://x.ai/
2. 注册账号并申请API访问
3. 复制API密钥

### Gemini (Google)
1. 访问 https://ai.google.dev/
2. 点击 "Get API Key"
3. 创建新的API密钥

### DeepSeek
1. 访问 https://platform.deepseek.com/
2. 注册账号
3. 在设置中创建API密钥

---

## 💡 常用命令

```bash
# 只测试数据获取（不调用AI）
python utils/data_fetcher.py

# 验证配置
python config.py

# 完整预测流程
python main.py

# 查看帮助
python main.py --help
```

---

## 🎯 自定义配置

### 修改预测的币种
编辑 `config.py`:
```python
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
```

### 修改预测时间窗口
编辑 `config.py`:
```python
PREDICTION_WINDOWS = [5, 10, 15, 30, 60]  # 分钟
```

### 修改K线数据量
编辑 `config.py`:
```python
KLINE_LIMIT = 200  # 获取最近200根K线
```

---

## ⚠️ 故障排除

### 问题: 无法连接Binance
```bash
# 检查网络
ping api.binance.com

# 可能需要代理
export https_proxy=http://127.0.0.1:7890
```

### 问题: API密钥错误
```bash
# 重新检查config.py中的密钥
python config.py

# 或重新设置环境变量
export DEEPSEEK_API_KEY="新密钥"
```

### 问题: 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📚 更多信息

- 完整文档: [README.md](README.md)
- 项目总结: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- 代码注释: 所有文件都有详细注释

---

**开始你的加密货币预测之旅吧！** 🚀💰
