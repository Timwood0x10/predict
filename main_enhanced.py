#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版主程序 - 集成决策引擎的加密货币交易系统

功能: 
1. 获取多源数据（Gas、价格、新闻、情绪、AI预测）
2. 整合成26维特征向量
3. 使用决策引擎分析
4. 输出完整交易计划
5. AI可调用的API接口
"""

import sys
import os
import json
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, jsonify, request

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置和模块
import config
from utils.data_integrator import IntegratedDataFetcher
from utils.decision_engine import DecisionEngine
from models.ai_predictor import MultiModelPredictor

# 设置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{config.LOGS_DIR}/main_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedTradingSystem:
    """增强版交易系统 - 集成决策引擎"""
    
    def __init__(self, account_balance: float = 10000, risk_percent: float = 0.015):
        """
        初始化系统
        
        Args:
            account_balance: 账户余额（USDT）
            risk_percent: 单笔风险比例（默认1.5%）
        """
        logger.info("="*80)
        logger.info("初始化增强版交易系统（集成决策引擎）")
        logger.info("="*80)
        
        # 验证配置
        if not config.validate_config():
            logger.error("配置验证失败，请检查API密钥设置")
            sys.exit(1)
        
        # 初始化数据整合器
        self.data_fetcher = IntegratedDataFetcher()
        logger.info("✓ 数据整合器初始化完成")
        
        # 初始化决策引擎
        self.decision_engine = DecisionEngine(
            account_balance=account_balance,
            risk_percent=risk_percent
        )
        logger.info(f"✓ 决策引擎初始化完成 (账户: ${account_balance:,.2f}, 风险: {risk_percent*100:.2f}%)")
        
        # 初始化AI预测器
        self.ai_predictor = MultiModelPredictor(config.API_KEYS)
        logger.info("✓ AI预测器初始化完成")
        
        # 存储结果
        self.latest_data: Dict = None
        self.latest_decision: Dict = None
    
    def fetch_and_integrate_data(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        步骤1: 获取并整合所有数据
        
        Args:
            symbol: 交易对（默认BTCUSDT）
        
        Returns:
            整合后的数据字典
        """
        logger.info("\n" + "="*80)
        logger.info(f"步骤1: 获取并整合数据 - {symbol}")
        logger.info("="*80)
        
        try:
            # 使用数据整合器获取26维特征
            integrated_data = self.data_fetcher.get_26d_features(symbol)
            
            if integrated_data and 'features' in integrated_data:
                self.latest_data = integrated_data
                
                logger.info(f"✓ 数据整合成功")
                logger.info(f"  - 特征维度: {len(integrated_data['features'])}")
                logger.info(f"  - 当前价格: ${integrated_data['metadata']['current_price']:,.2f}")
                logger.info(f"  - Gas费用: ETH {integrated_data['metadata']['gas']['eth_gas_gwei']} Gwei")
                logger.info(f"  - 新闻数量: {integrated_data['metadata']['news']['total_news']}条")
                logger.info(f"  - AI预测数: {integrated_data['metadata']['ai']['total_predictions']}个")
                
                return integrated_data
            else:
                logger.error("数据整合失败")
                return None
                
        except Exception as e:
            logger.error(f"数据获取出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_and_decide(self) -> Optional[Dict]:
        """
        步骤2: 使用决策引擎分析
        
        Returns:
            决策结果字典
        """
        logger.info("\n" + "="*80)
        logger.info("步骤2: 决策引擎分析")
        logger.info("="*80)
        
        if not self.latest_data:
            logger.error("没有数据，无法进行决策")
            return None
        
        try:
            # 提取特征向量
            features = self.latest_data['features']
            
            # 使用决策引擎分析
            decision = self.decision_engine.analyze(features)
            
            self.latest_decision = decision
            
            # 打印决策报告
            report = self.decision_engine.format_decision_report(decision)
            print("\n" + report)
            
            return decision
            
        except Exception as e:
            logger.error(f"决策分析出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_results(self, symbol: str = "BTCUSDT") -> bool:
        """
        步骤3: 保存结果
        
        Args:
            symbol: 交易对
        
        Returns:
            是否保存成功
        """
        logger.info("\n" + "="*80)
        logger.info("步骤3: 保存结果")
        logger.info("="*80)
        
        if not self.latest_decision:
            logger.error("没有决策结果可保存")
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 1. 保存决策结果（JSON）
            decision_file = f"{config.DATA_DIR}/decision_{symbol}_{timestamp}.json"
            with open(decision_file, 'w', encoding='utf-8') as f:
                json.dump(self.latest_decision, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ 决策结果已保存: {decision_file}")
            
            # 2. 保存特征数据（JSON）
            if self.latest_data:
                data_file = f"{config.DATA_DIR}/features_{symbol}_{timestamp}.json"
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.latest_data, f, indent=2, ensure_ascii=False)
                logger.info(f"✓ 特征数据已保存: {data_file}")
            
            # 3. 保存交易日志（CSV）
            log_entry = {
                'timestamp': self.latest_decision['timestamp'],
                'symbol': symbol,
                'action': self.latest_decision['decision']['action'],
                'confidence': self.latest_decision['decision']['confidence'],
                'total_score': self.latest_decision['signals']['total_score'] if self.latest_decision['signals'] else None,
                'current_price': self.latest_data['metadata']['current_price'] if self.latest_data else None,
                'stop_loss': self.latest_decision['position']['stop_loss'] if self.latest_decision['position'] else None,
                'take_profit_1': self.latest_decision['position']['take_profit_1'] if self.latest_decision['position'] else None,
                'position_size': self.latest_decision['position']['position_size'] if self.latest_decision['position'] else None,
            }
            
            log_file = f"{config.DATA_DIR}/trading_log.csv"
            df = pd.DataFrame([log_entry])
            
            # 追加到现有文件
            if os.path.exists(log_file):
                df.to_csv(log_file, mode='a', header=False, index=False)
            else:
                df.to_csv(log_file, index=False)
            
            logger.info(f"✓ 交易日志已更新: {log_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"保存结果出错: {e}")
            return False
    
    def run_single_analysis(self, symbol: str = "BTCUSDT") -> bool:
        """
        运行单次完整分析
        
        Args:
            symbol: 交易对
        
        Returns:
            是否成功
        """
        logger.info("\n" + "="*80)
        logger.info(f"开始执行交易决策分析 - {symbol}")
        logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        # 步骤1: 获取数据
        if not self.fetch_and_integrate_data(symbol):
            logger.error("数据获取失败，程序终止")
            return False
        
        # 步骤2: 决策分析
        if not self.analyze_and_decide():
            logger.error("决策分析失败，程序终止")
            return False
        
        # 步骤3: 保存结果
        if not self.save_results(symbol):
            logger.error("结果保存失败")
            return False
        
        logger.info("\n" + "="*80)
        logger.info("✓ 分析完成!")
        logger.info("="*80)
        
        # 输出决策摘要
        decision = self.latest_decision['decision']
        logger.info(f"\n📊 决策摘要:")
        logger.info(f"  动作: {decision['action']}")
        logger.info(f"  置信度: {decision['confidence']:.2f}%")
        logger.info(f"  原因: {decision['reason']}")
        
        if self.latest_decision['position']:
            pos = self.latest_decision['position']
            logger.info(f"\n💰 仓位信息:")
            logger.info(f"  仓位: {pos['position_size']:.8f} BTC (${pos['position_value']:,.2f})")
            logger.info(f"  止损: ${pos['stop_loss']:,.2f}")
            logger.info(f"  止盈: ${pos['take_profit_1']:,.2f} / ${pos['take_profit_2']:,.2f} / ${pos['take_profit_3']:,.2f}")
        
        return True
    
    def run_continuous_monitoring(self, symbol: str = "BTCUSDT", interval_minutes: int = 5):
        """
        持续监控模式
        
        Args:
            symbol: 交易对
            interval_minutes: 检查间隔（分钟）
        """
        logger.info("\n" + "="*80)
        logger.info("启动持续监控模式")
        logger.info(f"交易对: {symbol}")
        logger.info(f"检查间隔: {interval_minutes}分钟")
        logger.info("="*80)
        
        import time
        
        try:
            while True:
                logger.info(f"\n{'='*80}")
                logger.info(f"执行定时检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}")
                
                # 执行单次分析
                self.run_single_analysis(symbol)
                
                # 等待下一次检查
                logger.info(f"\n⏰ 等待 {interval_minutes} 分钟后进行下次检查...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("\n用户中断持续监控")
        except Exception as e:
            logger.error(f"持续监控出错: {e}")
    
    def get_latest_decision_json(self) -> str:
        """
        获取最新决策的JSON格式（供AI调用）
        
        Returns:
            JSON字符串
        """
        if self.latest_decision:
            return json.dumps(self.latest_decision, indent=2, ensure_ascii=False)
        else:
            return json.dumps({"error": "没有可用的决策结果"}, ensure_ascii=False)
    
    def get_latest_decision_summary(self) -> str:
        """
        获取最新决策的简要摘要（供AI调用）
        
        Returns:
            摘要文本
        """
        if not self.latest_decision:
            return "❌ 没有可用的决策结果"
        
        decision = self.latest_decision['decision']
        
        summary = f"""
📊 交易决策摘要
{'='*50}
🎯 决策: {decision['action']}
📈 置信度: {decision['confidence']:.2f}%
💡 原因: {decision['reason']}
"""
        
        if self.latest_decision['position']:
            pos = self.latest_decision['position']
            summary += f"""
💰 仓位信息:
  - 仓位大小: {pos['position_size']:.8f} BTC
  - 仓位价值: ${pos['position_value']:,.2f}
  - 止损价: ${pos['stop_loss']:,.2f}
  - 止盈1 (50%): ${pos['take_profit_1']:,.2f}
  - 止盈2 (30%): ${pos['take_profit_2']:,.2f}
  - 止盈3 (20%): ${pos['take_profit_3']:,.2f}
  - 预期收益: ${pos['expected_profit']:,.2f}
  - 风险收益比: {pos['risk_reward_ratio']}:1
"""
        
        if self.latest_decision['signals']:
            signals = self.latest_decision['signals']
            summary += f"""
📡 信号分析:
  - 新闻信号: {signals['news_score']:.0f}/100
  - 价格信号: {signals['price_score']:.0f}/100
  - 情绪信号: {signals['sentiment_score']:.0f}/100
  - AI信号: {signals['ai_score']:.0f}/100
  - 总分: {signals['total_score']:.0f}/100
  - 一致性: {signals['consistency']*100:.0f}%
"""
        
        summary += "=" * 50
        return summary


# ==================== Flask API (供AI调用) ====================

app = Flask(__name__)
trading_system = None


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    API接口: 执行交易分析
    
    POST参数:
        symbol: 交易对（可选，默认BTCUSDT）
    
    返回:
        JSON格式的决策结果
    """
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTCUSDT')
        
        # 执行分析
        success = trading_system.run_single_analysis(symbol)
        
        if success:
            return jsonify({
                'status': 'success',
                'data': trading_system.latest_decision
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '分析失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/decision', methods=['GET'])
def api_get_decision():
    """
    API接口: 获取最新决策
    
    返回:
        JSON格式的最新决策
    """
    try:
        if trading_system.latest_decision:
            return jsonify({
                'status': 'success',
                'data': trading_system.latest_decision
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '没有可用的决策'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/summary', methods=['GET'])
def api_get_summary():
    """
    API接口: 获取决策摘要
    
    返回:
        文本格式的决策摘要
    """
    try:
        summary = trading_system.get_latest_decision_summary()
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def api_health():
    """
    API接口: 健康检查
    """
    return jsonify({
        'status': 'ok',
        'system': 'Enhanced Trading System',
        'timestamp': datetime.now().isoformat()
    })


def start_api_server(host: str = '0.0.0.0', port: int = 5000):
    """
    启动API服务器
    
    Args:
        host: 监听地址
        port: 监听端口
    """
    logger.info("\n" + "="*80)
    logger.info("启动API服务器")
    logger.info(f"监听地址: http://{host}:{port}")
    logger.info("="*80)
    logger.info("\nAPI端点:")
    logger.info(f"  - POST http://{host}:{port}/api/analyze   执行分析")
    logger.info(f"  - GET  http://{host}:{port}/api/decision  获取决策")
    logger.info(f"  - GET  http://{host}:{port}/api/summary   获取摘要")
    logger.info(f"  - GET  http://{host}:{port}/api/health    健康检查")
    logger.info("\n" + "="*80)
    
    app.run(host=host, port=port, debug=False)


# ==================== 命令行接口 ====================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='增强版加密货币交易系统')
    parser.add_argument('--mode', type=str, choices=['single', 'monitor', 'api'], default='single',
                        help='运行模式: single(单次分析), monitor(持续监控), api(API服务器)')
    parser.add_argument('--symbol', type=str, default='BTCUSDT',
                        help='交易对 (默认: BTCUSDT)')
    parser.add_argument('--balance', type=float, default=10000,
                        help='账户余额 (默认: 10000)')
    parser.add_argument('--risk', type=float, default=0.015,
                        help='单笔风险比例 (默认: 0.015 即1.5%%)')
    parser.add_argument('--interval', type=int, default=5,
                        help='监控间隔（分钟，仅monitor模式，默认: 5）')
    parser.add_argument('--port', type=int, default=5000,
                        help='API端口 (仅api模式，默认: 5000)')
    
    args = parser.parse_args()
    
    try:
        # 创建系统实例
        global trading_system
        trading_system = EnhancedTradingSystem(
            account_balance=args.balance,
            risk_percent=args.risk
        )
        
        # 根据模式运行
        if args.mode == 'single':
            # 单次分析模式
            success = trading_system.run_single_analysis(args.symbol)
            sys.exit(0 if success else 1)
            
        elif args.mode == 'monitor':
            # 持续监控模式
            trading_system.run_continuous_monitoring(args.symbol, args.interval)
            
        elif args.mode == 'api':
            # API服务器模式
            start_api_server(port=args.port)
        
    except KeyboardInterrupt:
        logger.info("\n用户中断程序")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
