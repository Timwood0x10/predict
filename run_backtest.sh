#!/bin/bash
# ==============================================================================
# 回测脚本 - 独立回测功能
# ==============================================================================

echo "════════════════════════════════════════════════════════════════════════════════"
echo "📊 回测引擎"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# ================================ 参数配置 ====================================

# 💰 初始资金
CAPITAL=1000

# 📊 杠杆倍数（1-125）
LEVERAGE=10

# ⚠️ 风险比例（建议1-3%）
RISK=2.0

# 🛑 止损比例（建议1-5%）
STOP_LOSS=2.0

# 🪙 交易对（支持多个，用空格分隔）
SYMBOLS="BTCUSDT ETHUSDT"

# 📅 回测天数（1-30天）
BACKTEST_DAYS=14

# ⏱️ K线间隔
# 选项：1m, 5m, 15m, 1h, 4h, 1d
# 推荐：12h（一天两次决策）或 1h（更细粒度的数据）
BACKTEST_INTERVAL="12h"

# 🚀 使用完整决策系统（含动态权重）
# 选项：true / false
# true: 使用完整决策系统（包括动态权重、AI决策层）
# false: 使用简单MA交叉策略（更快）
USE_FULL_SYSTEM=true

# ==============================================================================

echo "回测配置："
echo "  💰 初始资金: $CAPITAL USDT"
echo "  📊 杠杆倍数: ${LEVERAGE}x"
echo "  ⚠️  风险比例: ${RISK}%"
echo "  🛑 止损比例: ${STOP_LOSS}%"
echo "  📅 回测天数: $BACKTEST_DAYS 天"
echo "  ⏱️  K线间隔: $BACKTEST_INTERVAL"
echo "  🪙 交易对: $SYMBOLS"
echo ""
echo "  ⏰ 交易频率: 每12小时决策一次（一天2次）"
echo "  📈 预计总交易: BTC约$((BACKTEST_DAYS * 2))次, ETH约$((BACKTEST_DAYS * 2))次"
echo ""
if [ "$USE_FULL_SYSTEM" = "true" ]; then
    echo "  🚀 决策系统: 完整系统（含动态权重）"
else
    echo "  📊 决策系统: 简单MA交叉策略"
fi
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"

# 创建输出目录
mkdir -p data/backtest

# 统计变量
total_count=0
success_count=0

# 对每个币种进行回测
for SYMBOL in $SYMBOLS; do
    total_count=$((total_count + 1))
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "[$total_count] 回测 $SYMBOL"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # 构建命令
    CMD="python backtest_engine.py \
        --capital $CAPITAL \
        --leverage $LEVERAGE \
        --risk $RISK \
        --stop-loss $STOP_LOSS \
        --symbol $SYMBOL \
        --days $BACKTEST_DAYS \
        --interval $BACKTEST_INTERVAL"
    
    # 如果启用完整系统，添加参数
    if [ "$USE_FULL_SYSTEM" = "true" ]; then
        CMD="$CMD --full-system"
    fi
    
    # 执行回测
    eval $CMD
    
    if [ $? -eq 0 ]; then
        success_count=$((success_count + 1))
    fi
    
    # 等待一下再继续
    if [ $total_count -lt $(echo $SYMBOLS | wc -w) ]; then
        echo ""
        echo "⏳ 等待2秒后继续..."
        sleep 2
    fi
done

# ==============================================================================
# 总结
# ==============================================================================

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ 回测完成！"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 统计："
echo "  总回测数: $total_count"
echo "  成功: $success_count"
echo "  失败: $((total_count - success_count))"
echo ""
echo "📁 结果保存在: data/backtest/"
echo ""
echo "💡 查看结果："
echo "  ls -lh data/backtest/                 # 查看所有文件"
echo "  cat data/backtest/*_stats*.txt        # 查看统计报告"
echo ""
echo "💡 提示："
echo "  - 查看详细文档: cat 回测和数据导出使用指南.md"
echo "  - 调整参数: vim run_backtest.sh"
echo "  - 对比不同参数的回测结果"
echo ""
echo "🚀 完整系统 vs 简单策略："
echo "  - 完整系统: 包含动态权重、市场状态识别、置信度调整"
echo "  - 简单策略: 仅使用MA交叉，速度更快"
echo "  - 切换方式: 修改 run_backtest.sh 中的 USE_FULL_SYSTEM 参数"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
