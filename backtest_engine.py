#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测引擎 - 使用历史数据测试交易策略
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from utils.data_fetcher import BinanceDataFetcher
from advanced_trading_system import AdvancedTradingSystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """回测引擎 - 测试策略在历史数据上的表现"""
    
    def __init__(self, initial_capital: float = 1000, leverage: int = 10, risk_percent: float = 2.0):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            leverage: 杠杆倍数
            risk_percent: 风险比例
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.leverage = leverage
        self.risk_percent = risk_percent
        
        self.trades = []  # 交易记录
        self.data_fetcher = BinanceDataFetcher()
        
        logger.info("=" * 80)
        logger.info("📊 回测引擎初始化")
        logger.info("=" * 80)
        logger.info(f"  初始资金: {initial_capital} USDT")
        logger.info(f"  杠杆倍数: {leverage}x")
        logger.info(f"  风险比例: {risk_percent}%")
    
    def fetch_historical_data(
        self, 
        symbol: str, 
        interval: str = "1h",
        days: int = 7
    ) -> Optional[pd.DataFrame]:
        """
        获取历史数据
        
        Args:
            symbol: 交易对
            interval: K线间隔 (1m, 5m, 15m, 1h, 4h, 1d)
            days: 回测天数
            
        Returns:
            历史K线数据
        """
        try:
            # 计算需要的K线数量
            intervals_per_day = {
                '1m': 1440,
                '5m': 288,
                '15m': 96,
                '1h': 24,
                '4h': 6,
                '1d': 1
            }
            
            limit = intervals_per_day.get(interval, 24) * days
            limit = min(limit, 1000)  # Binance限制
            
            logger.info(f"获取 {symbol} 最近 {days} 天的 {interval} K线数据 (约{limit}条)...")
            
            df = self.data_fetcher.fetch_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            if df is not None and len(df) > 0:
                logger.info(f"✓ 成功获取 {len(df)} 条历史数据")
                logger.info(f"  时间范围: {df.iloc[0]['open_time']} 至 {df.iloc[-1]['open_time']}")
                return df
            else:
                logger.error("✗ 获取历史数据失败")
                return None
                
        except Exception as e:
            logger.error(f"获取历史数据出错: {e}")
            return None
    
    def simulate_trade(
        self,
        entry_price: float,
        action: str,
        stop_loss: float,
        take_profit: List[float],
        position_size: float,
        timestamp: datetime,
        future_prices: pd.DataFrame
    ) -> Dict:
        """
        模拟单笔交易
        
        Args:
            entry_price: 入场价格
            action: 操作 (LONG/SHORT)
            stop_loss: 止损价格
            take_profit: 止盈价格列表 [TP1, TP2, TP3]
            position_size: 仓位大小
            timestamp: 入场时间
            future_prices: 未来价格数据
            
        Returns:
            交易结果
        """
        if future_prices is None or len(future_prices) == 0:
            return None
        
        remaining_position = position_size
        total_pnl = 0
        exit_price = None
        exit_time = None
        exit_reason = ""
        
        # 遍历未来价格，检查止损/止盈
        for idx, row in future_prices.iterrows():
            current_price = row['close']
            current_time = row['open_time']
            
            if action == "LONG":
                # 检查止损
                if current_price <= stop_loss:
                    pnl = (stop_loss - entry_price) * remaining_position
                    total_pnl += pnl
                    exit_price = stop_loss
                    exit_time = current_time
                    exit_reason = "止损"
                    break
                
                # 检查止盈
                for i, tp in enumerate(take_profit):
                    if current_price >= tp:
                        # 分批平仓 (33%, 33%, 34%)
                        close_ratio = [0.33, 0.33, 0.34][i]
                        close_size = position_size * close_ratio
                        pnl = (tp - entry_price) * close_size
                        total_pnl += pnl
                        remaining_position -= close_size
                        
                        if remaining_position <= 0.001:
                            exit_price = tp
                            exit_time = current_time
                            exit_reason = f"止盈TP{i+1}"
                            break
            
            elif action == "SHORT":
                # 检查止损
                if current_price >= stop_loss:
                    pnl = (entry_price - stop_loss) * remaining_position
                    total_pnl += pnl
                    exit_price = stop_loss
                    exit_time = current_time
                    exit_reason = "止损"
                    break
                
                # 检查止盈
                for i, tp in enumerate(take_profit):
                    if current_price <= tp:
                        close_ratio = [0.33, 0.33, 0.34][i]
                        close_size = position_size * close_ratio
                        pnl = (entry_price - tp) * close_size
                        total_pnl += pnl
                        remaining_position -= close_size
                        
                        if remaining_position <= 0.001:
                            exit_price = tp
                            exit_time = current_time
                            exit_reason = f"止盈TP{i+1}"
                            break
            
            if exit_price is not None:
                break
        
        # 如果没有触发止损止盈，按最后价格平仓
        if exit_price is None and len(future_prices) > 0:
            exit_price = future_prices.iloc[-1]['close']
            exit_time = future_prices.iloc[-1]['open_time']
            exit_reason = "时间到期"
            
            if action == "LONG":
                pnl = (exit_price - entry_price) * remaining_position
            else:
                pnl = (entry_price - exit_price) * remaining_position
            
            total_pnl += pnl
        
        return {
            'entry_time': timestamp,
            'entry_price': entry_price,
            'exit_time': exit_time,
            'exit_price': exit_price,
            'action': action,
            'position_size': position_size,
            'pnl': total_pnl,
            'pnl_percent': (total_pnl / (entry_price * position_size)) * 100 if position_size > 0 else 0,
            'exit_reason': exit_reason
        }
    
    def run_backtest(
        self,
        symbol: str,
        historical_data: pd.DataFrame,
        stop_loss_pct: float = 2.0,
        save_data: bool = True
    ) -> Dict:
        """
        运行回测
        
        Args:
            symbol: 交易对
            historical_data: 历史数据
            stop_loss_pct: 止损百分比
            save_data: 是否保存数据
            
        Returns:
            回测结果统计
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"开始回测 {symbol}")
        logger.info("=" * 80)
        
        # 创建交易系统（用于生成信号）
        system = AdvancedTradingSystem(
            capital_usdt=self.initial_capital,
            leverage=self.leverage,
            risk_percent=self.risk_percent
        )
        
        trades = []
        current_capital = self.initial_capital
        
        # 每隔一定周期生成一次信号（避免过于频繁）
        signal_interval = max(1, len(historical_data) // 20)  # 最多20个信号
        
        for i in range(0, len(historical_data) - 10, signal_interval):
            try:
                current_row = historical_data.iloc[i]
                current_price = current_row['close']
                timestamp = current_row['open_time']
                
                logger.info(f"\n检查信号点 {i+1}/{len(historical_data)} - {timestamp}")
                logger.info(f"价格: ${current_price:,.2f}")
                
                # 这里简化处理：因为完整分析需要实时数据
                # 在实际回测中，我们使用简单的技术指标生成信号
                signal = self._generate_simple_signal(historical_data.iloc[:i+1])
                
                if signal['action'] in ['LONG', 'SHORT']:
                    logger.info(f"✓ 生成{signal['action']}信号，置信度: {signal['confidence']:.0f}%")
                    
                    # 计算仓位
                    margin_required = (current_capital * self.risk_percent / 100) / (stop_loss_pct / 100)
                    position_value = margin_required * self.leverage
                    position_size = position_value / current_price
                    
                    # 计算止损止盈
                    if signal['action'] == 'LONG':
                        stop_loss = current_price * (1 - stop_loss_pct / 100)
                        take_profit = [
                            current_price * 1.04,
                            current_price * 1.07,
                            current_price * 1.12
                        ]
                    else:
                        stop_loss = current_price * (1 + stop_loss_pct / 100)
                        take_profit = [
                            current_price * 0.96,
                            current_price * 0.93,
                            current_price * 0.88
                        ]
                    
                    # 模拟交易
                    future_data = historical_data.iloc[i+1:i+11]
                    trade_result = self.simulate_trade(
                        entry_price=current_price,
                        action=signal['action'],
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        position_size=position_size,
                        timestamp=timestamp,
                        future_prices=future_data
                    )
                    
                    if trade_result:
                        # 更新资金
                        current_capital += trade_result['pnl']
                        trade_result['capital_after'] = current_capital
                        trades.append(trade_result)
                        
                        logger.info(f"  交易结果: {trade_result['exit_reason']}")
                        logger.info(f"  盈亏: {trade_result['pnl']:.2f} USDT ({trade_result['pnl_percent']:.2f}%)")
                        logger.info(f"  剩余资金: {current_capital:.2f} USDT")
            
            except Exception as e:
                logger.warning(f"处理信号点 {i} 时出错: {e}")
                continue
        
        # 计算统计数据
        stats = self._calculate_statistics(trades, current_capital)
        
        # 保存数据
        if save_data and trades:
            self._save_backtest_data(symbol, trades, stats, historical_data)
        
        return stats
    
    def _generate_simple_signal(self, data: pd.DataFrame) -> Dict:
        """
        生成简单的交易信号（基于技术指标）
        
        使用简单的MA交叉策略
        """
        if len(data) < 20:
            return {'action': 'HOLD', 'confidence': 0}
        
        # 计算移动平均线
        data_copy = data.copy()
        data_copy['ma_short'] = data_copy['close'].rolling(window=7).mean()
        data_copy['ma_long'] = data_copy['close'].rolling(window=20).mean()
        
        # 获取最近的值
        latest = data_copy.iloc[-1]
        prev = data_copy.iloc[-2]
        
        # MA交叉策略
        if prev['ma_short'] <= prev['ma_long'] and latest['ma_short'] > latest['ma_long']:
            return {'action': 'LONG', 'confidence': 70}
        elif prev['ma_short'] >= prev['ma_long'] and latest['ma_short'] < latest['ma_long']:
            return {'action': 'SHORT', 'confidence': 70}
        else:
            return {'action': 'HOLD', 'confidence': 50}
    
    def _calculate_statistics(self, trades: List[Dict], final_capital: float) -> Dict:
        """计算回测统计数据"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_return': 0,
                'final_capital': final_capital,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'avg_win': 0,
                'avg_loss': 0
            }
        
        df = pd.DataFrame(trades)
        
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] <= 0])
        win_rate = (winning_trades / len(trades)) * 100 if trades else 0
        
        total_pnl = df['pnl'].sum()
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # 计算最大回撤
        df['cumulative_capital'] = self.initial_capital + df['pnl'].cumsum()
        df['max_capital'] = df['cumulative_capital'].expanding().max()
        df['drawdown'] = (df['cumulative_capital'] - df['max_capital']) / df['max_capital'] * 100
        max_drawdown = df['drawdown'].min()
        
        # 夏普比率（简化版）
        returns = df['pnl_percent']
        sharpe_ratio = (returns.mean() / returns.std()) if returns.std() > 0 else 0
        
        return {
            'total_trades': len(trades),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'final_capital': final_capital,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_win': df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0,
            'avg_loss': df[df['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0
        }
    
    def _save_backtest_data(
        self,
        symbol: str,
        trades: List[Dict],
        stats: Dict,
        historical_data: pd.DataFrame
    ):
        """保存回测数据到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建回测数据目录
        os.makedirs('data/backtest', exist_ok=True)
        
        # 保存交易记录
        trades_df = pd.DataFrame(trades)
        trades_file = f'data/backtest/{symbol}_trades_{timestamp}.csv'
        trades_df.to_csv(trades_file, index=False)
        logger.info(f"✓ 交易记录已保存: {trades_file}")
        
        # 保存统计数据
        stats_file = f'data/backtest/{symbol}_stats_{timestamp}.txt'
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"回测统计报告 - {symbol}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"初始资金: {self.initial_capital:.2f} USDT\n")
            f.write(f"最终资金: {stats['final_capital']:.2f} USDT\n")
            f.write(f"总盈亏: {stats['total_pnl']:.2f} USDT\n")
            f.write(f"总收益率: {stats['total_return']:.2f}%\n\n")
            f.write(f"交易次数: {stats['total_trades']}\n")
            f.write(f"盈利次数: {stats['winning_trades']}\n")
            f.write(f"亏损次数: {stats['losing_trades']}\n")
            f.write(f"胜率: {stats['win_rate']:.2f}%\n\n")
            f.write(f"平均盈利: {stats['avg_win']:.2f} USDT\n")
            f.write(f"平均亏损: {stats['avg_loss']:.2f} USDT\n")
            f.write(f"最大回撤: {stats['max_drawdown']:.2f}%\n")
            f.write(f"夏普比率: {stats['sharpe_ratio']:.2f}\n")
        
        logger.info(f"✓ 统计报告已保存: {stats_file}")
    
    def print_results(self, stats: Dict):
        """打印回测结果"""
        print("\n" + "=" * 80)
        print("📊 回测结果")
        print("=" * 80)
        print(f"初始资金: {self.initial_capital:.2f} USDT")
        print(f"最终资金: {stats['final_capital']:.2f} USDT")
        print(f"总盈亏: {stats['total_pnl']:+.2f} USDT")
        print(f"总收益率: {stats['total_return']:+.2f}%")
        print()
        print(f"交易次数: {stats['total_trades']}")
        print(f"盈利次数: {stats['winning_trades']} 🟢")
        print(f"亏损次数: {stats['losing_trades']} 🔴")
        print(f"胜率: {stats['win_rate']:.2f}%")
        print()
        print(f"平均盈利: {stats['avg_win']:.2f} USDT")
        print(f"平均亏损: {stats['avg_loss']:.2f} USDT")
        print(f"最大回撤: {stats['max_drawdown']:.2f}%")
        print(f"夏普比率: {stats['sharpe_ratio']:.2f}")
        print("=" * 80)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='交易策略回测引擎')
    parser.add_argument('--capital', type=float, default=1000, help='初始资金')
    parser.add_argument('--leverage', type=int, default=10, help='杠杆倍数')
    parser.add_argument('--risk', type=float, default=2.0, help='风险比例')
    parser.add_argument('--stop-loss', type=float, default=2.0, help='止损比例')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='交易对')
    parser.add_argument('--days', type=int, default=7, help='回测天数')
    parser.add_argument('--interval', type=str, default='1h', help='K线间隔')
    
    args = parser.parse_args()
    
    # 创建回测引擎
    engine = BacktestEngine(
        initial_capital=args.capital,
        leverage=args.leverage,
        risk_percent=args.risk
    )
    
    # 获取历史数据
    historical_data = engine.fetch_historical_data(
        symbol=args.symbol,
        interval=args.interval,
        days=args.days
    )
    
    if historical_data is None:
        logger.error("无法获取历史数据")
        return
    
    # 运行回测
    stats = engine.run_backtest(
        symbol=args.symbol,
        historical_data=historical_data,
        stop_loss_pct=args.stop_loss
    )
    
    # 打印结果
    engine.print_results(stats)


if __name__ == "__main__":
    main()
