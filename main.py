#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序 - 加密货币价格预测系统
功能: 
1. 获取BTC和ETH的实时K线数据
2. 使用Grok, Gemini, DeepSeek进行价格预测
3. 保存和对比预测结果
"""

import sys
import os
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置和模块
import config
from utils.data_fetcher import BinanceDataFetcher, format_klines_for_prompt
from models.ai_predictor import MultiModelPredictor

# 设置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{config.LOGS_DIR}/main_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CryptoPricePredictionSystem:
    """加密货币价格预测系统"""
    
    def __init__(self):
        """初始化系统"""
        logger.info("="*80)
        logger.info("初始化加密货币价格预测系统")
        logger.info("="*80)
        
        # 验证配置
        if not config.validate_config():
            logger.error("配置验证失败，请检查API密钥设置")
            sys.exit(1)
        
        # 初始化数据获取器
        self.data_fetcher = BinanceDataFetcher(config.BINANCE_API_BASE)
        logger.info("✓ 数据获取器初始化完成")
        
        # 初始化AI预测器
        self.predictor = MultiModelPredictor(config.API_KEYS)
        logger.info("✓ AI预测器初始化完成")
        
        # 存储结果
        self.kline_data: Dict[str, pd.DataFrame] = {}
        self.predictions: pd.DataFrame = None
    
    def fetch_data(self) -> bool:
        """
        步骤1: 获取K线数据
        
        Returns:
            是否成功获取数据
        """
        logger.info("\n" + "="*80)
        logger.info("步骤1: 获取K线数据")
        logger.info("="*80)
        
        try:
            # 获取所有交易对的数据
            for symbol in config.SYMBOLS:
                logger.info(f"\n正在获取 {symbol} 的K线数据...")
                
                # 获取最近15分钟的1分钟K线
                df = self.data_fetcher.fetch_recent_klines(
                    symbol=symbol,
                    minutes=15
                )
                
                if df is not None and len(df) > 0:
                    self.kline_data[symbol] = df
                    logger.info(f"✓ {symbol} 数据获取成功: {len(df)} 条记录")
                    
                    # 显示最新价格
                    latest_price = df.iloc[-1]['close']
                    logger.info(f"  最新价格: ${latest_price:,.2f}")
                else:
                    logger.error(f"✗ {symbol} 数据获取失败")
                    return False
            
            # 保存K线数据到CSV
            if self.kline_data:
                success = self.data_fetcher.save_to_csv(
                    self.kline_data,
                    config.KLINE_DATA_FILE
                )
                if success:
                    logger.info(f"\n✓ K线数据已保存到: {config.KLINE_DATA_FILE}")
                else:
                    logger.warning("K线数据保存失败")
            
            return len(self.kline_data) > 0
            
        except Exception as e:
            logger.error(f"获取数据时出错: {e}")
            return False
    
    def predict_prices(self) -> bool:
        """
        步骤2: 使用AI模型预测价格
        
        Returns:
            是否成功完成预测
        """
        logger.info("\n" + "="*80)
        logger.info("步骤2: AI模型预测")
        logger.info("="*80)
        
        if not self.kline_data:
            logger.error("没有K线数据，无法进行预测")
            return False
        
        try:
            all_predictions = []
            
            # 对每个交易对进行预测
            for symbol, df in self.kline_data.items():
                logger.info(f"\n{'='*80}")
                logger.info(f"正在预测 {symbol}")
                logger.info(f"{'='*80}")
                
                # 获取当前价格
                current_price = df.iloc[-1]['close']
                logger.info(f"当前价格: ${current_price:,.2f}")
                
                # 格式化K线数据为文本
                kline_text = format_klines_for_prompt(df, limit=15)
                
                # 对多个时间窗口进行预测
                predictions_df = self.predictor.predict_multiple_windows(
                    prompt_template=config.PREDICTION_PROMPT_TEMPLATE,
                    windows=config.PREDICTION_WINDOWS,
                    symbol=symbol,
                    current_price=current_price,
                    kline_data=kline_text
                )
                
                all_predictions.append(predictions_df)
                
                logger.info(f"\n✓ {symbol} 预测完成")
            
            # 合并所有预测结果
            if all_predictions:
                self.predictions = pd.concat(all_predictions, ignore_index=True)
                logger.info(f"\n✓ 所有预测完成，共 {len(self.predictions)} 条记录")
                return True
            else:
                logger.error("没有生成预测结果")
                return False
            
        except Exception as e:
            logger.error(f"预测过程出错: {e}")
            return False
    
    def save_predictions(self) -> bool:
        """
        步骤3: 保存预测结果
        
        Returns:
            是否成功保存
        """
        logger.info("\n" + "="*80)
        logger.info("步骤3: 保存预测结果")
        logger.info("="*80)
        
        if self.predictions is None or len(self.predictions) == 0:
            logger.error("没有预测结果可保存")
            return False
        
        try:
            # 保存完整预测结果
            self.predictions.to_csv(config.PREDICTIONS_FILE, index=False)
            logger.info(f"✓ 预测结果已保存到: {config.PREDICTIONS_FILE}")
            
            # 创建对比表格
            comparison_df = self.create_comparison_table()
            
            if comparison_df is not None:
                comparison_df.to_csv(config.COMPARISON_FILE, index=False)
                logger.info(f"✓ 对比结果已保存到: {config.COMPARISON_FILE}")
                
                # 在控制台打印对比表格
                self.print_comparison_table(comparison_df)
            
            return True
            
        except Exception as e:
            logger.error(f"保存结果时出错: {e}")
            return False
    
    def create_comparison_table(self) -> pd.DataFrame:
        """
        创建模型对比表格
        
        Returns:
            对比表格DataFrame
        """
        try:
            # 选择需要的列
            comparison_data = []
            
            for _, row in self.predictions.iterrows():
                record = {
                    "时间": row['timestamp'],
                    "币种": row['symbol'],
                    "预测窗口(分钟)": row['window_minutes'],
                    "当前价格": f"${row['current_price']:,.2f}",
                    "Grok预测": f"${row['grok_price']:,.2f}" if pd.notna(row['grok_price']) else "N/A",
                    "Grok置信度": f"{row['grok_confidence']}%" if pd.notna(row['grok_confidence']) else "N/A",
                    "Gemini预测": f"${row['gemini_price']:,.2f}" if pd.notna(row['gemini_price']) else "N/A",
                    "Gemini置信度": f"{row['gemini_confidence']}%" if pd.notna(row['gemini_confidence']) else "N/A",
                    "DeepSeek预测": f"${row['deepseek_price']:,.2f}" if pd.notna(row['deepseek_price']) else "N/A",
                    "DeepSeek置信度": f"{row['deepseek_confidence']}%" if pd.notna(row['deepseek_confidence']) else "N/A"
                }
                comparison_data.append(record)
            
            return pd.DataFrame(comparison_data)
            
        except Exception as e:
            logger.error(f"创建对比表格时出错: {e}")
            return None
    
    def print_comparison_table(self, df: pd.DataFrame):
        """
        在控制台打印对比表格
        
        Args:
            df: 对比表格DataFrame
        """
        logger.info("\n" + "="*80)
        logger.info("模型预测对比")
        logger.info("="*80)
        
        # 使用pandas的to_string方法格式化输出
        print("\n" + df.to_string(index=False))
        
        logger.info("\n" + "="*80)
    
    def run(self):
        """运行完整的预测流程"""
        logger.info("\n" + "="*80)
        logger.info("开始执行加密货币价格预测")
        logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        # 步骤1: 获取数据
        if not self.fetch_data():
            logger.error("数据获取失败，程序终止")
            return False
        
        # 步骤2: 预测价格
        if not self.predict_prices():
            logger.error("价格预测失败，程序终止")
            return False
        
        # 步骤3: 保存结果
        if not self.save_predictions():
            logger.error("结果保存失败")
            return False
        
        logger.info("\n" + "="*80)
        logger.info("✓ 所有步骤执行完成!")
        logger.info("="*80)
        logger.info(f"\n数据文件:")
        logger.info(f"  - K线数据: {config.KLINE_DATA_FILE}")
        logger.info(f"  - 预测结果: {config.PREDICTIONS_FILE}")
        logger.info(f"  - 对比表格: {config.COMPARISON_FILE}")
        logger.info(f"  - 日志文件: {config.LOGS_DIR}/")
        
        return True


def main():
    """主函数"""
    try:
        # 创建系统实例
        system = CryptoPricePredictionSystem()
        
        # 运行预测流程
        success = system.run()
        
        # 返回状态码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n用户中断程序")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
