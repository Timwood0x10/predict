# 🔑 环境配置指南 (.env 文件)

## ✅ 当前配置状态

系统已配置从 `.env` 文件读取API密钥！

## 📝 配置步骤

### 1. 创建 .env 文件

```bash
cd crypto_price_prediction
cp .env.example .env
```

### 2. 编辑 .env 文件

```bash
vim .env
# 或使用其他编辑器
nano .env
```

### 3. 添加API密钥

在 `.env` 文件中添加：

```bash
# DeepSeek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Gemini (免费，每分钟60次请求)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Grok (可选，需要申请)
GROK_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**注意**:
- ✅ 至少配置一个模型即可运行
- ✅ 系统会自动跳过未配置的模型
- ✅ 推荐同时配置DeepSeek和Gemini（都有免费额度）

---

## 🎁 免费API获取方式

### 1. DeepSeek (强烈推荐) 🌟

**免费额度**: 500万tokens（约5000次调用）

**获取步骤**:
1. 访问 https://platform.deepseek.com/sign_up
2. 使用邮箱注册账号
3. 验证邮箱
4. 登录后进入"API Keys"页面
5. 点击"Create API Key"
6. 复制密钥并粘贴到 `.env` 文件

**特点**:
- ✅ 完全免费500万tokens
- ✅ 中文支持好
- ✅ 速度快
- ✅ 无需信用卡

---

### 2. Gemini (Google) 🌟

**免费额度**: 每分钟60次请求

**获取步骤**:
1. 访问 https://makersuite.google.com/app/apikey
2. 登录Google账号
3. 点击"Create API Key"
4. 选择或创建项目
5. 复制API密钥
6. 粘贴到 `.env` 文件

**特点**:
- ✅ 完全免费（有频率限制）
- ✅ Google品质
- ✅ 无需信用卡

---

### 3. Grok (X.AI) ⚠️

**免费额度**: 目前需要申请Beta访问

**获取步骤**:
1. 访问 https://x.ai/
2. 申请API访问权限
3. 等待审批（可能需要几天）

**特点**:
- ⚠️ 需要申请
- ⚠️ 可能需要付费
- 建议：暂时跳过，只用DeepSeek和Gemini

---

## 🔐 安全建议

### ✅ 好的做法

```bash
# .env 文件已在 .gitignore 中，不会被提交到Git
# 可以安全地存储API密钥
DEEPSEEK_API_KEY=your-real-key-here
```

### ❌ 不要做的事

```bash
# 不要把密钥硬编码在代码中
# 不要把 .env 文件提交到GitHub
# 不要分享你的API密钥
```

---

## 🧪 验证配置

### 检查API密钥是否正确加载

```bash
python -c "import config; config.validate_config()"
```

**期望输出**:
```
============================================================
API密钥配置状态:
============================================================
✓ 已配置的模型: DEEPSEEK, GEMINI
============================================================
```

### 运行完整测试

```bash
python test_system.py
```

**期望结果**:
```
✓ 配置模块导入成功
✓ 数据获取模块导入成功
✓ AI预测模块导入成功
  ✓ 已配置的模型: deepseek, gemini
✓ 主程序模块导入成功
✓ 系统已就绪！
```

---

## 💡 常见问题

### Q1: .env 文件放在哪里？

**A**: 放在 `crypto_price_prediction/` 目录下（与 `main.py` 同级）

```
crypto_price_prediction/
├── .env              ← 这里！
├── main.py
├── config.py
└── ...
```

### Q2: 为什么系统读不到API密钥？

**A**: 检查以下几点：
1. `.env` 文件位置正确
2. 文件名是 `.env` 不是 `env.txt`
3. 没有多余的空格或引号
4. 已安装 `python-dotenv` 包

```bash
pip install python-dotenv
```

### Q3: 我只有一个API密钥可以吗？

**A**: 可以！至少配置一个即可，系统会自动跳过未配置的模型。

推荐配置顺序：
1. DeepSeek（最推荐，免费额度大）
2. Gemini（免费，备用）
3. Grok（可选）

### Q4: 如何查看剩余额度？

**DeepSeek**:
- 登录 https://platform.deepseek.com/
- 查看"Usage"页面

**Gemini**:
- 访问 https://console.cloud.google.com/
- 查看API使用情况

### Q5: 免费额度用完了怎么办？

**方案A**: 注册新账号（不推荐）
**方案B**: 购买付费额度（推荐）
**方案C**: 使用其他免费模型（如HuggingFace）

---

## 📊 成本估算

### 单次运行成本

```
配置: 2个币种 × 7个时间窗口 × 2个模型 = 28次API调用
每次约500-1000 tokens
总消耗: ~28,000 tokens/次

DeepSeek免费额度: 5,000,000 tokens
可运行次数: 5,000,000 ÷ 28,000 ≈ 178次

结论: 免费额度完全够用！ ✅
```

### 付费价格参考

**DeepSeek**:
- ¥0.001/1K tokens
- 约 ¥0.028/次运行
- 非常便宜！

**Gemini**:
- 免费（有频率限制）

---

## 🚀 下一步

配置完成后：

```bash
# 1. 验证配置
python test_system.py

# 2. 开始预测
python main.py

# 3. 查看结果
cat data/model_comparison.csv
```

---

**祝你预测成功！** 🎉💰
