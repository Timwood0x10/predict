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
from real_trading_decision import RealTradingDecisionSystem
from utils.dynamic_weights import DynamicWeightManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """回测引擎 - 测试策略在历史数据上的表现"""
    
    def __init__(self, initial_capital: float = 1000, leverage: int = 10, risk_percent: float = 2.0, use_full_system: bool = False):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            leverage: 杠杆倍数
            risk_percent: 风险比例
            use_full_system: 是否使用完整决策系统（包括动态权重、AI决策等）
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.leverage = leverage
        self.risk_percent = risk_percent
        self.use_full_system = use_full_system
        
        self.trades = []  # 交易记录
        self.data_fetcher = BinanceDataFetcher()
        
        # 如果使用完整系统，初始化决策系统和动态权重
        if use_full_system:
            self.decision_system = RealTradingDecisionSystem(
                account_balance=initial_capital,
                risk_percent=risk_percent / 100  # 转换为小数
            )
            self.weight_manager = DynamicWeightManager()
            logger.info("🚀 使用完整决策系统（含动态权重）")
        else:
            self.decision_system = None
            self.weight_manager = None
            logger.info("📊 使用简单MA交叉策略")
        
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
        save_data: bool = True,
        interval: str = '1h'
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
        
        # 固定交易频率：每12小时一次决策
        # 根据K线间隔确定决策频率（一天两次）
        interval_hours_map = {
            '1m': 1/60, '5m': 5/60, '15m': 15/60, '30m': 0.5,
            '1h': 1, '2h': 2, '4h': 4, '6h': 6, '12h': 12, '1d': 24
        }
        
        # 获取当前K线间隔对应的小时数
        current_interval_hours = interval_hours_map.get(interval, 1)
        
        # 每12小时决策一次（一天两次）
        signal_interval = max(1, int(12 / current_interval_hours))
        
        logger.info(f"📅 回测周期: {len(historical_data)}根K线，间隔{interval}")
        logger.info(f"⏰ 交易频率: 每{signal_interval}根K线决策一次（每12小时）")
        logger.info(f"📊 预计交易次数: 约{(len(historical_data) // signal_interval)}次")
        
        for i in range(0, len(historical_data) - 10, signal_interval):
            try:
                current_row = historical_data.iloc[i]
                current_price = current_row['close']
                timestamp = current_row['open_time']
                
                logger.info(f"\n检查信号点 {i+1}/{len(historical_data)} - {timestamp}")
                logger.info(f"价格: ${current_price:,.2f}")
                
                # 生成交易信号
                if self.use_full_system:
                    # 使用完整决策系统
                    signal = self._generate_full_system_signal(symbol, historical_data.iloc[:i+1])
                else:
                    # 使用简单的MA交叉策略
                    signal = self._generate_simple_signal(historical_data.iloc[:i+1])
                
                if signal['action'] in ['LONG', 'SHORT']:
                    logger.info(f"✓ 生成{signal['action']}信号，置信度: {signal['confidence']:.0f}%")
                    
                    # 计算仓位（修正后的逻辑）
                    # 风险金额 = 账户余额 * 风险比例
                    risk_amount = current_capital * (self.risk_percent / 100)
                    
                    # 仓位价值 = 风险金额 / 止损比例 * 杠杆
                    # 例如：风险20 USDT，止损2%，杠杆10x
                    # 仓位价值 = 20 / 0.02 * 10 = 10,000 USDT
                    position_value = (risk_amount / (stop_loss_pct / 100)) * self.leverage
                    
                    # 限制最大仓位不超过账户余额 * 杠杆
                    max_position = current_capital * self.leverage
                    position_value = min(position_value, max_position)
                    
                    # 计算持仓数量
                    position_size = position_value / current_price
                    
                    logger.info(f"  风险金额: {risk_amount:.2f} USDT")
                    logger.info(f"  仓位价值: {position_value:.2f} USDT")
                    logger.info(f"  持仓数量: {position_size:.6f}")
                    
                    # 计算止损止盈（更合理的比例）
                    if signal['action'] == 'LONG':
                        stop_loss = current_price * (1 - stop_loss_pct / 100)
                        take_profit = [
                            current_price * (1 + stop_loss_pct * 1.0 / 100),   # 1:1 盈亏比
                            current_price * (1 + stop_loss_pct * 2.0 / 100),   # 1:2 盈亏比
                            current_price * (1 + stop_loss_pct * 3.0 / 100)    # 1:3 盈亏比
                        ]
                    else:
                        stop_loss = current_price * (1 + stop_loss_pct / 100)
                        take_profit = [
                            current_price * (1 - stop_loss_pct * 1.0 / 100),   # 1:1 盈亏比
                            current_price * (1 - stop_loss_pct * 2.0 / 100),   # 1:2 盈亏比
                            current_price * (1 - stop_loss_pct * 3.0 / 100)    # 1:3 盈亏比
                        ]
                    
                    logger.info(f"  止损: ${stop_loss:,.2f} ({stop_loss_pct:.1f}%)")
                    logger.info(f"  止盈1: ${take_profit[0]:,.2f} ({stop_loss_pct*1:.1f}%)")
                    logger.info(f"  止盈2: ${take_profit[1]:,.2f} ({stop_loss_pct*2:.1f}%)")
                    logger.info(f"  止盈3: ${take_profit[2]:,.2f} ({stop_loss_pct*3:.1f}%)")
                    
                    # 模拟交易（增加观察时间窗口）
                    # 使用更长的时间窗口，最多50根K线或到数据末尾
                    future_end = min(i + 51, len(historical_data))
                    future_data = historical_data.iloc[i+1:future_end]
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
    
    def _generate_full_system_signal(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        使用完整决策系统生成交易信号（使用真实的决策引擎和AI层）
        
        这是真正的回测：使用历史K线数据模拟当时的决策过程
        """
        try:
            if len(data) < 20:
                return {'action': 'HOLD', 'confidence': 0}
            
            # 1. 从历史数据构建市场数据快照（模拟当时的市场状态）
            market_snapshot = self._build_market_snapshot(symbol, data)
            
            # 2. 使用真实决策系统的核心逻辑
            from utils.data_integrator import DataIntegrator
            from utils.decision_engine import DecisionEngine
            
            integrator = DataIntegrator()
            decision_engine = DecisionEngine(
                account_balance=self.current_capital,
                risk_percent=self.risk_percent / 100,
                backtest_mode=True  # 回测模式，放宽数据完整性检查
            )
            
            # 3. 整合特征（使用历史数据）
            # 从market_snapshot中提取各种数据
            kline_df = None
            if 'klines' in market_snapshot and market_snapshot['klines']:
                import pandas as pd
                kline_df = pd.DataFrame(market_snapshot['klines'])
            
            integrated = integrator.integrate_all(
                gas_data=None,  # 回测时无Gas数据
                kline_df=kline_df,
                news_sentiment=market_snapshot.get('news_sentiment'),
                market_sentiment=None,
                ai_predictions=None,
                hours=12,
                orderbook_data=market_snapshot.get('orderbook'),
                macro_data=None,
                futures_data=market_snapshot.get('futures_data'),
                technical_indicators=None,
                multi_timeframe=None,
                support_resistance=None
            )
            features = integrated['features']
            
            # 4. 应用动态权重
            market_state = self.weight_manager.get_market_state(features)
            weights = self.weight_manager.get_weights(market_state)
            adjusted_weights = self.weight_manager.adjust_weights_by_dimensions(weights, features)
            
            # 5. 使用决策引擎进行分析
            decision_result = decision_engine.analyze(features=features, news_data=None)
            
            # 6. 提取信号和置信度
            decision_info = decision_result.get('decision', {})
            action = decision_info.get('action', 'HOLD')
            confidence = decision_info.get('confidence', 50)
            
            # 将BUY/SELL转换为LONG/SHORT（统一格式）
            if action == 'BUY':
                action = 'LONG'
            elif action == 'SELL':
                action = 'SHORT'
            else:
                action = 'HOLD'
            
            # 记录决策信息
            logger.info(f"  市场状态: {market_state}")
            logger.info(f"  动态权重: sentiment={weights.get('sentiment', 1.0):.1f}x, "
                       f"orderbook={weights.get('orderbook', 1.0):.1f}x, "
                       f"macro={weights.get('macro', 1.0):.1f}x")
            logger.info(f"  决策置信度: {confidence:.1f}%")
            
            return {
                'action': action,
                'confidence': confidence,
                'market_state': market_state,
                'weights': adjusted_weights,
                'decision': decision_result
            }
            
        except Exception as e:
            logger.warning(f"完整系统决策失败，使用备用策略: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_simple_signal(data)
    
    def _build_market_snapshot(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        从历史K线数据构建市场快照（模拟当时的市场状态）
        """
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        # 构建类似real_trading_decision中的market_data结构
        market_snapshot = {
            'symbol': symbol,
            'current_price': float(latest['close']),
            'klines': data.tail(100).to_dict('records'),  # 最近100根K线
            'market_data': {
                'price': float(latest['close']),
                'volume_24h': float(data.tail(24)['volume'].sum()) if len(data) >= 24 else float(data['volume'].sum()),
                'price_change_24h': ((float(latest['close']) - float(data.iloc[-24]['close'])) / float(data.iloc[-24]['close'])) if len(data) >= 24 else 0,
                'high_24h': float(data.tail(24)['high'].max()) if len(data) >= 24 else float(latest['high']),
                'low_24h': float(data.tail(24)['low'].min()) if len(data) >= 24 else float(latest['low']),
            },
            'orderbook': None,  # 回测时无订单簿数据
            'news_list': [],    # 回测时无新闻数据
            'news_sentiment': None,
            'polymarket_data': None,
            'futures_data': None,
            'timestamp': latest.name if hasattr(latest, 'name') else None
        }
        
        return market_snapshot
    
    def _extract_features_from_data(self, data: pd.DataFrame) -> list:
        """从历史数据中提取特征向量（用于动态权重）"""
        features = [0] * 35  # 35维特征向量
        
        if len(data) < 2:
            return features
        
        try:
            # 价格变化
            price_change = (data.iloc[-1]['close'] - data.iloc[-2]['close']) / data.iloc[-2]['close']
            features[2] = price_change  # 价格变化率
            
            # 波动率
            if len(data) >= 20:
                returns = data['close'].pct_change().dropna()
                volatility = returns.std()
                features[7] = volatility  # 波动率
            
            # 成交量变化
            if len(data) >= 2:
                volume_change = (data.iloc[-1]['volume'] - data.iloc[-2]['volume']) / data.iloc[-2]['volume']
                features[8] = volume_change
            
            # RSI（简化计算）
            if len(data) >= 14:
                delta = data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                features[10] = rsi.iloc[-1] / 100 if not pd.isna(rsi.iloc[-1]) else 0.5
            
            # 订单簿平衡（模拟）
            features[26] = 0.5  # 回测时无法获取真实订单簿，使用中性值
            
            # VIX（使用波动率代替）
            features[31] = min(volatility * 1000, 100) if len(data) >= 20 else 20
            
        except Exception as e:
            logger.warning(f"特征提取失败: {e}")
        
        return features
    
    def _generate_simple_signal(self, data: pd.DataFrame) -> Dict:
        """
        生成简单的交易信号（基于技术指标）
        
        使用改进的多指标策略
        """
        if len(data) < 20:
            return {'action': 'HOLD', 'confidence': 0}
        
        # 计算技术指标
        data_copy = data.copy()
        
        # 移动平均线
        data_copy['ma_short'] = data_copy['close'].rolling(window=7).mean()
        data_copy['ma_long'] = data_copy['close'].rolling(window=20).mean()
        
        # RSI指标
        delta = data_copy['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data_copy['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        data_copy['bb_middle'] = data_copy['close'].rolling(window=20).mean()
        bb_std = data_copy['close'].rolling(window=20).std()
        data_copy['bb_upper'] = data_copy['bb_middle'] + (bb_std * 2)
        data_copy['bb_lower'] = data_copy['bb_middle'] - (bb_std * 2)
        
        # 获取最近的值
        latest = data_copy.iloc[-1]
        prev = data_copy.iloc[-2]
        
        # 综合信号评分
        long_score = 0
        short_score = 0
        
        # 1. MA趋势 (40分)
        if latest['ma_short'] > latest['ma_long']:
            long_score += 40
        else:
            short_score += 40
        
        # 2. RSI超买超卖 (30分)
        if latest['rsi'] < 30:  # 超卖，看涨
            long_score += 30
        elif latest['rsi'] > 70:  # 超买，看跌
            short_score += 30
        elif latest['rsi'] < 45:  # 偏低
            long_score += 15
        elif latest['rsi'] > 55:  # 偏高
            short_score += 15
        
        # 3. 布林带位置 (30分)
        if latest['close'] < latest['bb_lower']:  # 触及下轨，看涨
            long_score += 30
        elif latest['close'] > latest['bb_upper']:  # 触及上轨，看跌
            short_score += 30
        elif latest['close'] < latest['bb_middle']:  # 低于中轨
            long_score += 15
        elif latest['close'] > latest['bb_middle']:  # 高于中轨
            short_score += 15
        
        # 4. MA交叉 (加分项)
        if prev['ma_short'] <= prev['ma_long'] and latest['ma_short'] > latest['ma_long']:
            long_score += 20  # 金叉
        elif prev['ma_short'] >= prev['ma_long'] and latest['ma_short'] < latest['ma_long']:
            short_score += 20  # 死叉
        
        # 根据得分决定信号
        if long_score >= 70 and long_score > short_score:
            confidence = min(long_score, 90)
            return {'action': 'LONG', 'confidence': confidence}
        elif short_score >= 70 and short_score > long_score:
            confidence = min(short_score, 90)
            return {'action': 'SHORT', 'confidence': confidence}
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
            
            # 回测参数
            f.write("【回测参数】\n")
            f.write(f"回测周期: {len(historical_data)}根K线\n")
            f.write(f"数据时间范围: {historical_data.iloc[0]['open_time']} 至 {historical_data.iloc[-1]['open_time']}\n")
            f.write(f"交易频率: 每12小时决策一次（一天两次）\n")
            f.write(f"初始资金: {self.initial_capital:.2f} USDT\n")
            f.write(f"杠杆倍数: {self.leverage}x\n")
            f.write(f"风险比例: {self.risk_percent}%\n\n")
            
            # 回测结果
            f.write("【回测结果】\n")
            f.write(f"最终资金: {stats['final_capital']:.2f} USDT\n")
            f.write(f"总盈亏: {stats['total_pnl']:+.2f} USDT\n")
            f.write(f"总收益率: {stats['total_return']:+.2f}%\n\n")
            
            # 交易统计
            f.write("【交易统计】\n")
            f.write(f"交易次数: {stats['total_trades']}\n")
            f.write(f"盈利次数: {stats['winning_trades']} 🟢\n")
            f.write(f"亏损次数: {stats['losing_trades']} 🔴\n")
            f.write(f"胜率: {stats['win_rate']:.2f}%\n\n")
            
            # 风险指标
            f.write("【风险指标】\n")
            f.write(f"平均盈利: {stats['avg_win']:.2f} USDT\n")
            f.write(f"平均亏损: {stats['avg_loss']:.2f} USDT\n")
            f.write(f"盈亏比: {abs(stats['avg_win']/stats['avg_loss']):.2f}:1\n" if stats['avg_loss'] != 0 else "盈亏比: N/A\n")
            f.write(f"最大回撤: {stats['max_drawdown']:.2f}%\n")
            f.write(f"夏普比率: {stats['sharpe_ratio']:.2f}\n")
        
        logger.info(f"✓ 统计报告已保存: {stats_file}")
    
    def print_results(self, stats: Dict):
        """打印回测结果"""
        print("\n" + "=" * 80)
        print("📊 回测结果汇总")
        print("=" * 80)
        print()
        print("【资金表现】")
        print(f"  初始资金: ${self.initial_capital:,.2f} USDT")
        print(f"  最终资金: ${stats['final_capital']:,.2f} USDT")
        print(f"  总盈亏: {stats['total_pnl']:+.2f} USDT")
        pnl_color = "🟢" if stats['total_return'] > 0 else "🔴"
        print(f"  总收益率: {stats['total_return']:+.2f}% {pnl_color}")
        print()
        print("【交易统计】")
        print(f"  交易次数: {stats['total_trades']}")
        print(f"  盈利次数: {stats['winning_trades']} 🟢")
        print(f"  亏损次数: {stats['losing_trades']} 🔴")
        win_rate_color = "🟢" if stats['win_rate'] >= 50 else "🔴"
        print(f"  胜率: {stats['win_rate']:.2f}% {win_rate_color}")
        print()
        print("【风险指标】")
        print(f"  平均盈利: +{stats['avg_win']:.2f} USDT")
        print(f"  平均亏损: {stats['avg_loss']:.2f} USDT")
        if stats['avg_loss'] != 0:
            profit_loss_ratio = abs(stats['avg_win'] / stats['avg_loss'])
            print(f"  盈亏比: {profit_loss_ratio:.2f}:1")
        print(f"  最大回撤: {stats['max_drawdown']:.2f}%")
        print(f"  夏普比率: {stats['sharpe_ratio']:.2f}")
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
    parser.add_argument('--full-system', action='store_true', help='使用完整决策系统（含动态权重）')
    
    args = parser.parse_args()
    
    # 创建回测引擎
    engine = BacktestEngine(
        initial_capital=args.capital,
        leverage=args.leverage,
        risk_percent=args.risk,
        use_full_system=args.full_system
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
        stop_loss_pct=args.stop_loss,
        interval=args.interval
    )
    
    # 打印结果
    engine.print_results(stats)


if __name__ == "__main__":
    main()
