#!/bin/bash
# 快速启动脚本 - 增强版交易系统

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印横幅
print_banner() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${GREEN}   🚀 加密货币交易系统 - 快速启动${NC}"
    echo -e "${BLUE}================================================================${NC}"
}

# 打印菜单
print_menu() {
    echo ""
    echo -e "${YELLOW}请选择运行模式:${NC}"
    echo ""
    echo "  1) 单次分析 (推荐新手)"
    echo "  2) 持续监控 (推荐量化)"
    echo "  3) API服务器 (推荐AI集成)"
    echo "  4) 运行测试"
    echo "  5) 查看文档"
    echo "  6) 退出"
    echo ""
}

# 单次分析
run_single() {
    echo -e "\n${GREEN}▶ 启动单次分析模式${NC}\n"
    
    read -p "交易对 [BTCUSDT]: " symbol
    symbol=${symbol:-BTCUSDT}
    
    read -p "账户余额 [10000]: " balance
    balance=${balance:-10000}
    
    read -p "风险比例% [1.5]: " risk
    risk=${risk:-1.5}
    risk=$(echo "scale=4; $risk / 100" | bc)
    
    echo -e "\n${BLUE}正在分析 $symbol...${NC}\n"
    python main_enhanced.py \
        --mode single \
        --symbol $symbol \
        --balance $balance \
        --risk $risk
    
    echo -e "\n${GREEN}✓ 分析完成！${NC}"
    echo -e "${YELLOW}查看结果:${NC}"
    echo "  - 终端报告（上方）"
    echo "  - JSON文件: data/decision_*.json"
    echo "  - 交易日志: data/trading_log.csv"
}

# 持续监控
run_monitor() {
    echo -e "\n${GREEN}▶ 启动持续监控模式${NC}\n"
    
    read -p "交易对 [BTCUSDT]: " symbol
    symbol=${symbol:-BTCUSDT}
    
    read -p "检查间隔(分钟) [5]: " interval
    interval=${interval:-5}
    
    read -p "账户余额 [10000]: " balance
    balance=${balance:-10000}
    
    read -p "风险比例% [1.5]: " risk
    risk=${risk:-1.5}
    risk=$(echo "scale=4; $risk / 100" | bc)
    
    echo -e "\n${BLUE}监控 $symbol，每 $interval 分钟检查一次...${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止监控${NC}\n"
    
    python main_enhanced.py \
        --mode monitor \
        --symbol $symbol \
        --interval $interval \
        --balance $balance \
        --risk $risk
}

# API服务器
run_api() {
    echo -e "\n${GREEN}▶ 启动API服务器模式${NC}\n"
    
    read -p "监听端口 [5000]: " port
    port=${port:-5000}
    
    read -p "账户余额 [10000]: " balance
    balance=${balance:-10000}
    
    read -p "风险比例% [1.5]: " risk
    risk=${risk:-1.5}
    risk=$(echo "scale=4; $risk / 100" | bc)
    
    echo -e "\n${BLUE}启动API服务器...${NC}\n"
    echo -e "${GREEN}API端点:${NC}"
    echo "  POST http://localhost:$port/api/analyze  - 执行分析"
    echo "  GET  http://localhost:$port/api/decision - 获取决策"
    echo "  GET  http://localhost:$port/api/summary  - 获取摘要"
    echo "  GET  http://localhost:$port/api/health   - 健康检查"
    echo ""
    echo -e "${YELLOW}测试API:${NC}"
    echo "  curl http://localhost:$port/api/health"
    echo "  curl -X POST http://localhost:$port/api/analyze -H 'Content-Type: application/json' -d '{\"symbol\":\"BTCUSDT\"}'"
    echo ""
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}\n"
    
    python main_enhanced.py \
        --mode api \
        --port $port \
        --balance $balance \
        --risk $risk
}

# 运行测试
run_tests() {
    echo -e "\n${GREEN}▶ 运行测试套件${NC}\n"
    
    echo -e "${BLUE}选择测试类型:${NC}"
    echo "  1) 完整测试 (test_all.py)"
    echo "  2) 决策引擎测试 (test_decision_engine.py)"
    echo "  3) 杠杆计算测试 (test_leverage.py)"
    echo "  4) AI集成测试 (test_ai_integration.py)"
    echo "  5) 全部运行"
    echo ""
    
    read -p "选择 [1-5]: " test_choice
    
    case $test_choice in
        1)
            echo -e "\n${BLUE}运行完整测试...${NC}\n"
            python test_all.py
            ;;
        2)
            echo -e "\n${BLUE}运行决策引擎测试...${NC}\n"
            python test_decision_engine.py
            ;;
        3)
            echo -e "\n${BLUE}运行杠杆计算测试...${NC}\n"
            python test_leverage.py
            ;;
        4)
            echo -e "\n${BLUE}运行AI集成测试...${NC}\n"
            python test_ai_integration.py
            ;;
        5)
            echo -e "\n${BLUE}运行所有测试...${NC}\n"
            python test_all.py
            python test_decision_engine.py
            python test_leverage.py
            python test_ai_integration.py
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            return
            ;;
    esac
    
    echo -e "\n${GREEN}✓ 测试完成！${NC}"
}

# 查看文档
view_docs() {
    echo -e "\n${GREEN}▶ 文档列表${NC}\n"
    
    echo "  1) MAIN_ENHANCED_GUIDE.md - 增强版主程序使用指南"
    echo "  2) MAIN_INTEGRATION_README.md - 主程序集成说明"
    echo "  3) DECISION_ENGINE_GUIDE.md - 决策引擎详细指南"
    echo "  4) DECISION_ENGINE_README.md - 决策引擎快速入门"
    echo "  5) INTEGRATION_SUMMARY.md - 整合完成报告"
    echo ""
    
    read -p "选择文档 [1-5] (Enter跳过): " doc_choice
    
    case $doc_choice in
        1) less MAIN_ENHANCED_GUIDE.md ;;
        2) less MAIN_INTEGRATION_README.md ;;
        3) less DECISION_ENGINE_GUIDE.md ;;
        4) less DECISION_ENGINE_README.md ;;
        5) less INTEGRATION_SUMMARY.md ;;
        *) return ;;
    esac
}

# 主函数
main() {
    print_banner
    
    while true; do
        print_menu
        read -p "请选择 [1-6]: " choice
        
        case $choice in
            1)
                run_single
                read -p $'\n按Enter继续...'
                ;;
            2)
                run_monitor
                read -p $'\n按Enter继续...'
                ;;
            3)
                run_api
                read -p $'\n按Enter继续...'
                ;;
            4)
                run_tests
                read -p $'\n按Enter继续...'
                ;;
            5)
                view_docs
                ;;
            6)
                echo -e "\n${GREEN}👋 再见！${NC}\n"
                exit 0
                ;;
            *)
                echo -e "\n${RED}无效选择，请重试${NC}"
                ;;
        esac
    done
}

# 检查Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}错误: 未找到Python，请先安装Python 3${NC}"
    exit 1
fi

# 检查依赖
check_deps() {
    echo -e "${BLUE}检查依赖...${NC}"
    python -c "import flask, requests, pandas, numpy" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}缺少依赖，正在安装...${NC}"
        pip install flask requests pandas numpy
    fi
}

check_deps

# 运行主函数
main
