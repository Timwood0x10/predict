#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出模块 - 将收集到的各维度数据保存到文件
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """数据导出器 - 保存分析数据到文件"""
    
    def __init__(self, output_dir: str = "data/analysis"):
        """
        初始化数据导出器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_all_data(
        self,
        symbol: str,
        market_data: Dict,
        analysis_result: Dict
    ) -> Dict[str, str]:
        """
        导出所有分析数据
        
        Args:
            symbol: 交易对
            market_data: 市场数据（原始）
            analysis_result: 分析结果
            
        Returns:
            导出的文件路径字典
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{symbol}_{timestamp}"
        
        exported_files = {}
        
        # 1. 导出K线数据
        if market_data.get('kline_df') is not None:
            kline_file = self._export_kline_data(
                base_name, 
                market_data['kline_df']
            )
            if kline_file:
                exported_files['kline'] = kline_file
        
        # 2. 导出新闻数据
        if market_data.get('news_list'):
            news_file = self._export_news_data(
                base_name,
                market_data['news_list'],
                market_data.get('news_sentiment')
            )
            if news_file:
                exported_files['news'] = news_file
        
        # 3. 导出市场情绪数据
        if market_data.get('market_sentiment'):
            sentiment_file = self._export_sentiment_data(
                base_name,
                market_data['market_sentiment']
            )
            if sentiment_file:
                exported_files['sentiment'] = sentiment_file
        
        # 4. 导出Polymarket数据
        if market_data.get('polymarket_sentiment'):
            poly_file = self._export_polymarket_data(
                base_name,
                market_data['polymarket_sentiment']
            )
            if poly_file:
                exported_files['polymarket'] = poly_file
        
        # 5. 导出AI预测数据
        ai_predictions = market_data.get('ai_predictions')
        if ai_predictions is not None and isinstance(ai_predictions, dict):
            ai_file = self._export_ai_predictions(
                base_name,
                ai_predictions
            )
            if ai_file:
                exported_files['ai_predictions'] = ai_file
        
        # 6. 导出综合决策数据
        if analysis_result:
            decision_file = self._export_decision_data(
                base_name,
                analysis_result
            )
            if decision_file:
                exported_files['decision'] = decision_file
        
        # 7. 导出Gas费数据
        if market_data.get('gas_data'):
            gas_file = self._export_gas_data(
                base_name,
                market_data['gas_data']
            )
            if gas_file:
                exported_files['gas'] = gas_file
        
        # 8. 创建汇总文件
        summary_file = self._create_summary_file(
            base_name,
            symbol,
            market_data,
            analysis_result,
            exported_files
        )
        if summary_file:
            exported_files['summary'] = summary_file
        
        return exported_files
    
    def _export_kline_data(self, base_name: str, kline_df) -> Optional[str]:
        """导出K线数据"""
        try:
            file_path = os.path.join(self.output_dir, f"{base_name}_kline.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("K线数据 (Price Data)\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"数据条数: {len(kline_df)}\n")
                f.write(f"时间范围: {kline_df.iloc[0]['open_time']} ~ {kline_df.iloc[-1]['open_time']}\n\n")
                
                # 统计信息
                f.write("价格统计:\n")
                f.write(f"  最高价: ${kline_df['high'].max():,.2f}\n")
                f.write(f"  最低价: ${kline_df['low'].min():,.2f}\n")
                f.write(f"  平均价: ${kline_df['close'].mean():,.2f}\n")
                f.write(f"  当前价: ${kline_df.iloc[-1]['close']:,.2f}\n\n")
                
                f.write("成交量统计:\n")
                f.write(f"  总成交量: {kline_df['volume'].sum():,.2f}\n")
                f.write(f"  平均成交量: {kline_df['volume'].mean():,.2f}\n\n")
                
                # 详细数据
                f.write("=" * 80 + "\n")
                f.write("详细K线数据:\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"{'时间':<20} {'开盘':<12} {'最高':<12} {'最低':<12} {'收盘':<12} {'成交量':<15}\n")
                f.write("-" * 95 + "\n")
                
                for _, row in kline_df.iterrows():
                    f.write(
                        f"{str(row['open_time']):<20} "
                        f"${row['open']:>10,.2f} "
                        f"${row['high']:>10,.2f} "
                        f"${row['low']:>10,.2f} "
                        f"${row['close']:>10,.2f} "
                        f"{row['volume']:>13,.2f}\n"
                    )
            
            logger.info(f"✓ K线数据已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"导出K线数据失败: {e}")
            return None
    
    def _export_news_data(
        self,
        base_name: str,
        news_list: list,
        news_sentiment: Optional[Dict]
    ) -> Optional[str]:
        """导出新闻数据"""
        try:
            file_path = os.path.join(self.output_dir, f"{base_name}_news.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("新闻数据 (News Data)\n")
                f.write("=" * 80 + "\n\n")
                
                # 新闻情绪
                if news_sentiment:
                    f.write("新闻情绪分析:\n")
                    f.write(f"  总体情绪: {news_sentiment.get('sentiment', 'N/A')}\n")
                    f.write(f"  看涨新闻: {news_sentiment.get('bullish_count', 0)}\n")
                    f.write(f"  看跌新闻: {news_sentiment.get('bearish_count', 0)}\n")
                    f.write(f"  中性新闻: {news_sentiment.get('neutral_count', 0)}\n")
                    f.write(f"  情绪评分: {news_sentiment.get('score', 0):.1f}/100\n\n")
                
                f.write(f"新闻总数: {len(news_list)}\n\n")
                
                # 详细新闻
                f.write("=" * 80 + "\n")
                f.write("详细新闻列表:\n")
                f.write("=" * 80 + "\n\n")
                
                for i, news in enumerate(news_list, 1):
                    # 处理新闻可能是字符串或字典的情况
                    if isinstance(news, str):
                        f.write(f"[{i}] {news}\n\n")
                    elif isinstance(news, dict):
                        f.write(f"[{i}] {news.get('title', 'N/A')}\n")
                        source = news.get('source', {})
                        if isinstance(source, dict):
                            f.write(f"    来源: {source.get('name', 'N/A')}\n")
                        else:
                            f.write(f"    来源: {source}\n")
                        f.write(f"    时间: {news.get('publishedAt', 'N/A')}\n")
                        if news.get('description'):
                            f.write(f"    摘要: {news['description'][:200]}...\n")
                        f.write(f"    链接: {news.get('url', 'N/A')}\n")
                        f.write("\n")
                    else:
                        f.write(f"[{i}] {str(news)}\n\n")
            
            logger.info(f"✓ 新闻数据已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"导出新闻数据失败: {e}")
            return None
    
    def _export_sentiment_data(
        self,
        base_name: str,
        sentiment_data: Dict
    ) -> Optional[str]:
        """导出市场情绪数据"""
        try:
            file_path = os.path.join(self.output_dir, f"{base_name}_sentiment.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("市场情绪数据 (Market Sentiment)\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"总体情绪: {sentiment_data.get('overall_sentiment', 'N/A')}\n")
                f.write(f"综合评分: {sentiment_data.get('combined_score', 0):.1f}/100\n\n")
                
                # 各维度情绪
                if sentiment_data.get('fear_greed'):
                    fg = sentiment_data['fear_greed']
                    f.write("恐惧贪婪指数:\n")
                    f.write(f"  指数值: {fg.get('value', 'N/A')}\n")
                    f.write(f"  分类: {fg.get('value_classification', 'N/A')}\n\n")
                
                if sentiment_data.get('social_sentiment'):
                    social = sentiment_data['social_sentiment']
                    f.write("社交媒体情绪:\n")
                    f.write(f"  Twitter情绪: {social.get('twitter_sentiment', 'N/A')}\n")
                    f.write(f"  Reddit情绪: {social.get('reddit_sentiment', 'N/A')}\n\n")
                
                if sentiment_data.get('funding_rate'):
                    f.write("资金费率:\n")
                    f.write(f"  费率: {sentiment_data['funding_rate']}\n\n")
                
                # 详细数据（JSON格式）
                f.write("=" * 80 + "\n")
                f.write("详细数据 (JSON):\n")
                f.write("=" * 80 + "\n\n")
                f.write(json.dumps(sentiment_data, indent=2, ensure_ascii=False, default=str))
            
            logger.info(f"✓ 市场情绪数据已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"导出市场情绪数据失败: {e}")
            return None
    
    def _export_polymarket_data(
        self,
        base_name: str,
        poly_data: Dict
    ) -> Optional[str]:
        """导出Polymarket数据"""
        try:
            file_path = os.path.join(self.output_dir, f"{base_name}_polymarket.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("Polymarket预测市场数据 (Polymarket Prediction)\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"总体态度: {poly_data.get('overall_sentiment', 'N/A')}\n")
                f.write(f"预测评分: {poly_data.get('score', 0):.1f}/100\n")
                f.write(f"市场总数: {poly_data.get('market_count', 0)}\n")
                f.write(f"看涨市场: {poly_data.get('bullish_markets', 0)}\n")
                f.write(f"看跌市场: {poly_data.get('bearish_markets', 0)}\n")
                f.write(f"中性市场: {poly_data.get('neutral_markets', 0)}\n\n")
                
                # 详细市场数据
                if poly_data.get('markets'):
                    f.write("=" * 80 + "\n")
                    f.write("详细市场列表:\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for i, market in enumerate(poly_data['markets'], 1):
                        f.write(f"[{i}] {market.get('question', 'N/A')}\n")
                        f.write(f"    概率: {market.get('probability', 0):.1f}%\n")
                        f.write(f"    态度: {market.get('sentiment', 'N/A')}\n")
                        f.write(f"    流动性: ${market.get('liquidity', 0):,.0f}\n")
                        f.write("\n")
                
                # JSON数据
                f.write("=" * 80 + "\n")
                f.write("完整数据 (JSON):\n")
                f.write("=" * 80 + "\n\n")
                f.write(json.dumps(poly_data, indent=2, ensure_ascii=False, default=str))
            
            logger.info(f"✓ Polymarket数据已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"导出Polymarket数据失败: {e}")
            return None
    
    def _export_ai_predictions(
        self,
        base_name: str,
        ai_predictions: Dict
    ) -> Optional[str]:
        """导出AI预测数据"""
        try:
            file_path = os.path.join(self.output_dir, f"{base_name}_ai_predictions.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("AI预测数据 (AI Predictions)\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"预测方向: {ai_predictions.get('direction', 'N/A')}\n")
                f.write(f"置信度: {ai_predictions.get('confidence', 0):.0f}%\n")
                f.write(f"预测依据: {ai_predictions.get('reasoning', 'N/A')}\n\n")
                
                # JSON数据
                f.write("=" * 80 + "\n")
                f.write("完整数据 (JSON):\n")
                f.write("=" * 80 + "\n\n")
                f.write(json.dumps(ai_predictions, indent=2, ensure_ascii=False, default=str))
            
            logger.info(f"✓ AI预测数据已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"导出AI预测数据失败: {e}")
            return None
    
    def _export_decision_data(
        self,
        base_name: str,
        decision_data: Dict
    ) -> Optional[str]:
        """导出综合决策数据"""
        try:
            file_path = os.path.join(self.output_dir, f"{base_name}_decision.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("综合决策数据 (Trading Decision)\n")
                f.write("=" * 80 + "\n\n")
                
                final = decision_data.get('final_decision', {})
                f.write("最终决策:\n")
                f.write(f"  操作: {final.get('action', 'N/A')}\n")
                f.write(f"  置信度: {final.get('confidence', 0):.0f}%\n")
                f.write(f"  原因: {final.get('reason', 'N/A')}\n\n")
                
                # 仓位信息
                if final.get('position'):
                    pos = final['position']
                    f.write("仓位管理:\n")
                    f.write(f"  保证金: {pos.get('margin_required', 0):.2f} USDT\n")
                    f.write(f"  仓位价值: {pos.get('position_value', 0):.2f} USDT\n")
                    f.write(f"  币数: {pos.get('position_size', 0):.8f}\n")
                    f.write(f"  止损: ${pos.get('stop_loss', 0):,.2f}\n")
                    f.write(f"  最大损失: {pos.get('max_loss', 0):.2f} USDT\n\n")
                
                # AI决策
                if decision_data.get('ai_decision'):
                    ai = decision_data['ai_decision']['decision']
                    f.write("AI决策层:\n")
                    f.write(f"  建议: {ai.get('action', 'N/A')}\n")
                    f.write(f"  置信度: {ai.get('confidence', 0):.0f}%\n")
                    f.write(f"  理由: {ai.get('reasoning', 'N/A')}\n\n")
                
                # 引擎决策
                if decision_data.get('engine_decision'):
                    engine = decision_data['engine_decision']
                    eng_dec = engine.get('decision', {})
                    f.write("决策引擎:\n")
                    f.write(f"  验证: {eng_dec.get('action', 'N/A')}\n")
                    
                    if engine.get('signals'):
                        signals = engine['signals']
                        f.write(f"  综合评分: {signals.get('total_score', 0):.0f}/100\n")
                        f.write(f"  信号一致性: {signals.get('consistency', 0)*100:.0f}%\n")
                
                # 市场诊断
                if decision_data.get('market_diagnosis'):
                    diag = decision_data['market_diagnosis']
                    f.write("\n市场诊断:\n")
                    if diag.get('overall_state'):
                        f.write(f"  {diag['overall_state']}\n")
                    
                    if diag.get('key_factors'):
                        f.write("\n  关键因素:\n")
                        for factor in diag['key_factors']:
                            f.write(f"    • {factor}\n")
                
                # JSON数据
                f.write("\n" + "=" * 80 + "\n")
                f.write("完整数据 (JSON):\n")
                f.write("=" * 80 + "\n\n")
                f.write(json.dumps(decision_data, indent=2, ensure_ascii=False, default=str))
            
            logger.info(f"✓ 综合决策数据已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"导出综合决策数据失败: {e}")
            return None
    
    def _export_gas_data(
        self,
        base_name: str,
        gas_data: Dict
    ) -> Optional[str]:
        """导出Gas费数据"""
        try:
            file_path = os.path.join(self.output_dir, f"{base_name}_gas.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("Gas费数据 (Gas Fee Data)\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(json.dumps(gas_data, indent=2, ensure_ascii=False, default=str))
            
            logger.info(f"✓ Gas费数据已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"导出Gas费数据失败: {e}")
            return None
    
    def _create_summary_file(
        self,
        base_name: str,
        symbol: str,
        market_data: Dict,
        analysis_result: Dict,
        exported_files: Dict
    ) -> Optional[str]:
        """创建汇总文件"""
        try:
            file_path = os.path.join(self.output_dir, f"{base_name}_SUMMARY.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"交易分析汇总报告 - {symbol}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"交易对: {symbol}\n\n")
                
                # 快速概览
                f.write("=" * 80 + "\n")
                f.write("快速概览\n")
                f.write("=" * 80 + "\n\n")
                
                if analysis_result:
                    final = analysis_result.get('final_decision', {})
                    f.write(f"✨ 最终决策: {final.get('action', 'N/A')}\n")
                    f.write(f"📊 置信度: {final.get('confidence', 0):.0f}%\n")
                    f.write(f"💡 原因: {final.get('reason', 'N/A')}\n\n")
                
                # 数据维度统计
                f.write("=" * 80 + "\n")
                f.write("数据维度统计\n")
                f.write("=" * 80 + "\n\n")
                
                dimensions = []
                kline_df = market_data.get('kline_df')
                if kline_df is not None:
                    try:
                        dimensions.append(f"✓ K线数据: {len(kline_df)} 条")
                    except:
                        dimensions.append(f"✓ K线数据: 已获取")
                
                news_list = market_data.get('news_list')
                if news_list:
                    dimensions.append(f"✓ 新闻数据: {len(news_list)} 条")
                
                market_sentiment = market_data.get('market_sentiment')
                if market_sentiment:
                    dimensions.append(f"✓ 市场情绪: 已分析")
                
                polymarket_sentiment = market_data.get('polymarket_sentiment')
                if polymarket_sentiment:
                    dimensions.append(f"✓ Polymarket: {polymarket_sentiment.get('market_count', 0)} 个市场")
                
                ai_predictions = market_data.get('ai_predictions')
                if ai_predictions is not None and isinstance(ai_predictions, dict):
                    dimensions.append(f"✓ AI预测: 已生成")
                
                gas_data = market_data.get('gas_data')
                if gas_data:
                    dimensions.append(f"✓ Gas费: 已监控")
                
                for dim in dimensions:
                    f.write(f"{dim}\n")
                
                # 导出文件列表
                f.write("\n" + "=" * 80 + "\n")
                f.write("导出文件列表\n")
                f.write("=" * 80 + "\n\n")
                
                for key, filepath in exported_files.items():
                    if key != 'summary':
                        f.write(f"📄 {key}: {os.path.basename(filepath)}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("所有数据文件已保存到: " + self.output_dir + "\n")
                f.write("=" * 80 + "\n")
            
            logger.info(f"✓ 汇总报告已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"创建汇总文件失败: {e}")
            return None


# 测试代码
if __name__ == "__main__":
    print("数据导出模块测试")
    exporter = DataExporter()
    print(f"输出目录: {exporter.output_dir}")
