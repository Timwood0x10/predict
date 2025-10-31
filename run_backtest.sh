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
BACKTEST_DAYS=7

# ⏱️ K线间隔
# 选项：1m, 5m, 15m, 1h, 4h, 1d
# 推荐：1h（数据量适中）
BACKTEST_INTERVAL="1h"

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
    
    python backtest_engine.py \
        --capital "$CAPITAL" \
        --leverage "$LEVERAGE" \
        --risk "$RISK" \
        --stop-loss "$STOP_LOSS" \
        --symbol "$SYMBOL" \
        --days "$BACKTEST_DAYS" \
        --interval "$BACKTEST_INTERVAL"
    
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
echo "════════════════════════════════════════════════════════════════════════════════"
