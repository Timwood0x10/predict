#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化交易执行器
根据AI决策自动执行交易（做多/做空）
"""

import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

from ai_decision_layer import AIDecisionLayer
from utils.data_integrator import IntegratedDataFetcher

logger = logging.getLogger(__name__)


class AutoTrader:
    """
    自动化交易执行器
    
    功能：
    1. 获取市场数据
    2. AI智能决策
    3. 自动下单（做多/做空）
    4. 持仓管理
    5. 止盈止损
    6. 风险控制
    """
    
    def __init__(
        self,
        account_balance: float = 10000,
        risk_percent: float = 0.015,
        max_positions: int = 3,
        use_real_trading: bool = False,
        exchange_api_key: Optional[str] = None,
        exchange_api_secret: Optional[str] = None
    ):
        """
        初始化自动交易器
        
        Args:
            account_balance: 账户余额
            risk_percent: 单笔风险比例
            max_positions: 最大同时持仓数
            use_real_trading: 是否使用真实交易（否则为模拟）
            exchange_api_key: 交易所API Key
            exchange_api_secret: 交易所API Secret
        """
        logger.info("="*80)
        logger.info("初始化自动化交易系统")
        logger.info("="*80)
        
        self.account_balance = account_balance
        self.risk_percent = risk_percent
        self.max_positions = max_positions
        self.use_real_trading = use_real_trading
        
        # 初始化AI决策层
        self.ai_decision = AIDecisionLayer(
            account_balance=account_balance,
            risk_percent=risk_percent
        )
        logger.info("✓ AI决策层初始化完成")
        
        # 初始化数据获取器
        self.data_fetcher = IntegratedDataFetcher()
        logger.info("✓ 数据获取器初始化完成")
        
        # 初始化交易所连接（如果使用真实交易）
        if use_real_trading:
            self._init_exchange(exchange_api_key, exchange_api_secret)
        else:
            logger.info("📝 模拟交易模式")
            self.exchange = None
        
        # 持仓管理
        self.positions: List[Dict] = []  # 当前持仓
        self.trade_history: List[Dict] = []  # 交易历史
        
        logger.info(f"✓ 初始化完成")
        logger.info(f"  - 账户余额: ${account_balance:,.2f}")
        logger.info(f"  - 单笔风险: {risk_percent*100:.2f}%")
        logger.info(f"  - 最大持仓: {max_positions}")
        logger.info(f"  - 交易模式: {'真实' if use_real_trading else '模拟'}")
        logger.info("="*80)
    
    def _init_exchange(self, api_key: Optional[str], api_secret: Optional[str]):
        """初始化交易所连接"""
        try:
            import ccxt
            
            if not api_key or not api_secret:
                logger.warning("未提供交易所API密钥，将使用模拟交易")
                self.use_real_trading = False
                self.exchange = None
                return
            
            # 初始化币安交易所（可扩展到其他交易所）
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',  # 使用合约交易
                }
            })
            
            # 测试连接
            balance = self.exchange.fetch_balance()
            logger.info("✓ 交易所连接成功")
            logger.info(f"  可用余额: ${balance['USDT']['free']:.2f} USDT")
            
        except ImportError:
            logger.error("未安装ccxt库，请运行: pip install ccxt")
            self.use_real_trading = False
            self.exchange = None
        except Exception as e:
            logger.error(f"交易所连接失败: {e}")
            self.use_real_trading = False
            self.exchange = None
    
    def get_market_data(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        获取市场数据
        
        Args:
            symbol: 交易对
        
        Returns:
            整合后的数据
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"获取市场数据: {symbol}")
        logger.info(f"{'='*80}")
        
        try:
            data = self.data_fetcher.get_26d_features(symbol)
            
            if data and 'features' in data:
                logger.info("✓ 数据获取成功")
                logger.info(f"  当前价格: ${data['metadata']['current_price']:,.2f}")
                return data
            else:
                logger.error("数据获取失败")
                return None
                
        except Exception as e:
            logger.error(f"数据获取出错: {e}")
            return None
    
    def make_decision(self, data: Dict) -> Dict:
        """
        AI智能决策
        
        Args:
            data: 市场数据
        
        Returns:
            决策结果
        """
        features = data['features']
        metadata = data['metadata']
        
        # 使用AI决策层生成决策
        result = self.ai_decision.make_final_decision(features, metadata)
        
        # 打印决策报告
        print(self.ai_decision.format_decision_report(result))
        
        return result
    
    def execute_trade(self, decision: Dict, symbol: str = "BTCUSDT") -> bool:
        """
        执行交易
        
        Args:
            decision: AI决策结果
            symbol: 交易对
        
        Returns:
            是否成功执行
        """
        action = decision['decision']['action']
        
        if action == 'NEUTRAL':
            logger.info("📊 决策: 观望，不执行交易")
            return False
        
        # 检查持仓限制
        if len(self.positions) >= self.max_positions:
            logger.warning(f"⚠️ 已达到最大持仓数({self.max_positions})，不执行新交易")
            return False
        
        # 构建订单
        order_info = self._build_order(decision, symbol)
        
        if not order_info:
            logger.error("订单构建失败")
            return False
        
        # 执行订单
        if self.use_real_trading and self.exchange:
            success = self._execute_real_order(order_info)
        else:
            success = self._execute_simulated_order(order_info)
        
        if success:
            # 添加到持仓
            self.positions.append(order_info)
            
            # 记录交易历史
            self.trade_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'OPEN',
                'order': order_info
            })
            
            # 保存状态
            self._save_state()
        
        return success
    
    def _build_order(self, decision: Dict, symbol: str) -> Optional[Dict]:
        """构建订单信息"""
        try:
            dec = decision['decision']
            
            if dec['action'] not in ['LONG', 'SHORT']:
                return None
            
            entry_price = dec.get('entry_price', 0)
            stop_loss = dec.get('stop_loss', 0)
            take_profit = dec.get('take_profit', [])
            position_ratio = dec.get('position_size_ratio', 0.15)
            
            # 计算仓位大小
            position_value = self.account_balance * position_ratio
            position_size = position_value / entry_price
            
            order_info = {
                'id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'symbol': symbol,
                'side': 'buy' if dec['action'] == 'LONG' else 'sell',
                'type': dec['action'],
                'entry_price': entry_price,
                'position_size': position_size,
                'position_value': position_value,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'status': 'open',
                'open_time': datetime.now().isoformat(),
                'strategy': dec.get('source', 'unknown'),
                'confidence': dec['confidence']
            }
            
            return order_info
            
        except Exception as e:
            logger.error(f"订单构建出错: {e}")
            return None
    
    def _execute_real_order(self, order: Dict) -> bool:
        """执行真实交易"""
        try:
            logger.info(f"\n{'='*80}")
            logger.info("🚀 执行真实交易")
            logger.info(f"{'='*80}")
            
            symbol = order['symbol'].replace('USDT', '/USDT')
            side = order['side']
            amount = order['position_size']
            
            # 下市价单
            result = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=amount
            )
            
            logger.info(f"✓ 订单执行成功")
            logger.info(f"  订单ID: {result['id']}")
            logger.info(f"  交易对: {symbol}")
            logger.info(f"  方向: {side.upper()}")
            logger.info(f"  数量: {amount:.8f}")
            logger.info(f"  成交价: ${result.get('average', 0):,.2f}")
            
            # 设置止损止盈
            self._set_stop_loss_take_profit(order, result)
            
            return True
            
        except Exception as e:
            logger.error(f"真实交易执行失败: {e}")
            return False
    
    def _execute_simulated_order(self, order: Dict) -> bool:
        """执行模拟交易"""
        logger.info(f"\n{'='*80}")
        logger.info("📝 执行模拟交易")
        logger.info(f"{'='*80}")
        logger.info(f"  订单ID: {order['id']}")
        logger.info(f"  交易对: {order['symbol']}")
        logger.info(f"  方向: {order['type']}")
        logger.info(f"  入场价: ${order['entry_price']:,.2f}")
        logger.info(f"  仓位: {order['position_size']:.8f} ({order['position_value']:.2f} USDT)")
        logger.info(f"  止损: ${order['stop_loss']:,.2f}")
        
        if order['take_profit']:
            logger.info(f"  止盈:")
            logger.info(f"    目标1 (50%): ${order['take_profit'][0]:,.2f}")
            logger.info(f"    目标2 (30%): ${order['take_profit'][1]:,.2f}")
            logger.info(f"    目标3 (20%): ${order['take_profit'][2]:,.2f}")
        
        logger.info(f"  策略: {order['strategy']}")
        logger.info(f"  置信度: {order['confidence']:.0f}%")
        logger.info(f"{'='*80}")
        
        return True
    
    def _set_stop_loss_take_profit(self, order: Dict, exchange_result: Dict):
        """设置止损止盈"""
        try:
            symbol = order['symbol'].replace('USDT', '/USDT')
            
            # 设置止损单
            if order['stop_loss']:
                stop_side = 'sell' if order['side'] == 'buy' else 'buy'
                self.exchange.create_order(
                    symbol=symbol,
                    type='stop_market',
                    side=stop_side,
                    amount=order['position_size'],
                    params={'stopPrice': order['stop_loss']}
                )
                logger.info(f"✓ 止损单已设置: ${order['stop_loss']:,.2f}")
            
            # 设置止盈单（分批）
            if order['take_profit']:
                tp_amounts = [
                    order['position_size'] * 0.5,
                    order['position_size'] * 0.3,
                    order['position_size'] * 0.2
                ]
                
                for i, (tp_price, tp_amount) in enumerate(zip(order['take_profit'], tp_amounts)):
                    take_side = 'sell' if order['side'] == 'buy' else 'buy'
                    self.exchange.create_order(
                        symbol=symbol,
                        type='take_profit_market',
                        side=take_side,
                        amount=tp_amount,
                        params={'stopPrice': tp_price}
                    )
                
                logger.info(f"✓ 止盈单已设置（3档）")
                
        except Exception as e:
            logger.error(f"设置止损止盈失败: {e}")
    
    def monitor_positions(self):
        """监控持仓"""
        if not self.positions:
            return
        
        logger.info(f"\n{'='*80}")
        logger.info(f"持仓监控 ({len(self.positions)}个)")
        logger.info(f"{'='*80}")
        
        for position in self.positions:
            logger.info(f"  {position['id']}: {position['type']} @ ${position['entry_price']:,.2f}")
            logger.info(f"    状态: {position['status']}")
            logger.info(f"    策略: {position['strategy']}")
    
    def _save_state(self):
        """保存状态"""
        try:
            state = {
                'account_balance': self.account_balance,
                'positions': self.positions,
                'trade_history': self.trade_history,
                'last_update': datetime.now().isoformat()
            }
            
            with open('data/auto_trader_state.json', 'w') as f:
                json.dump(state, f, indent=2)
                
            logger.info("✓ 状态已保存")
            
        except Exception as e:
            logger.error(f"保存状态失败: {e}")
    
    def run_once(self, symbol: str = "BTCUSDT") -> bool:
        """
        执行一次完整的交易流程
        
        Args:
            symbol: 交易对
        
        Returns:
            是否执行了交易
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🤖 自动交易执行 - {symbol}")
        logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*80}")
        
        # 1. 获取市场数据
        data = self.get_market_data(symbol)
        if not data:
            return False
        
        # 2. AI决策
        decision = self.make_decision(data)
        
        # 3. 执行交易
        executed = self.execute_trade(decision, symbol)
        
        # 4. 监控持仓
        self.monitor_positions()
        
        return executed
    
    def run_continuous(
        self,
        symbol: str = "BTCUSDT",
        interval_minutes: int = 5
    ):
        """
        持续运行自动交易
        
        Args:
            symbol: 交易对
            interval_minutes: 检查间隔（分钟）
        """
        logger.info(f"\n{'='*80}")
        logger.info("🚀 启动自动交易持续模式")
        logger.info(f"{'='*80}")
        logger.info(f"  交易对: {symbol}")
        logger.info(f"  检查间隔: {interval_minutes}分钟")
        logger.info(f"  按 Ctrl+C 停止")
        logger.info(f"{'='*80}")
        
        try:
            while True:
                self.run_once(symbol)
                
                logger.info(f"\n⏰ 等待 {interval_minutes} 分钟后进行下次检查...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("\n用户中断，正在停止...")
            self.monitor_positions()
            logger.info("✓ 已停止")


if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='自动化交易执行器')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='交易对')
    parser.add_argument('--balance', type=float, default=10000, help='账户余额')
    parser.add_argument('--risk', type=float, default=0.015, help='单笔风险比例')
    parser.add_argument('--mode', type=str, choices=['once', 'continuous'], default='once',
                        help='运行模式')
    parser.add_argument('--interval', type=int, default=5, help='持续模式检查间隔（分钟）')
    parser.add_argument('--real', action='store_true', help='使用真实交易（需要API密钥）')
    
    args = parser.parse_args()
    
    # 创建自动交易器
    trader = AutoTrader(
        account_balance=args.balance,
        risk_percent=args.risk,
        use_real_trading=args.real
    )
    
    # 运行
    if args.mode == 'once':
        trader.run_once(args.symbol)
    else:
        trader.run_continuous(args.symbol, args.interval)
