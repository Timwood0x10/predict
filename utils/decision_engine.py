"""
稳妥决策引擎 - 整合AI决策策略和风险管理
基于26维特征向量，提供保守、科学的交易决策

设计原则：
1. 风险第一，收益第二
2. 多层验证，严格标准
3. 科学仓位管理
4. 分批止盈止损
"""

import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    保守决策引擎
    
    架构：
    Layer 1: 安全检查（5项全过）
    Layer 2: 信号评分（加权计算）
    Layer 3: 保守决策（高标准）
    Layer 4: 仓位计算（风险控制）
    """
    
    def __init__(self, account_balance: float = 10000, risk_percent: float = 0.015):
        """
        初始化决策引擎
        
        Args:
            account_balance: 账户余额（USD）
            risk_percent: 单笔风险比例（默认1.5%）
        """
        self.account_balance = account_balance
        self.risk_percent = risk_percent
        self.existing_positions = []  # 当前持仓列表
        
        # 权重配置
        self.weights = {
            'news': 0.30,      # 新闻信号 30%
            'price': 0.25,     # 价格信号 25%
            'sentiment': 0.25, # 情绪信号 25%
            'ai': 0.20         # AI信号 20%
        }
        
        # 决策阈值（保守）
        self.thresholds = {
            'buy_score': 75,        # 买入分数阈值
            'sell_score': 25,       # 卖出分数阈值
            'min_consistency': 0.80 # 最低一致性要求
        }
    
    # ==================== Layer 1: 安全检查 ====================
    
    def safety_check(self, features: List[float]) -> Tuple[bool, str]:
        """
        安全检查 - 5项全过才能交易
        
        Args:
            features: 26维特征向量
            
        Returns:
            (是否通过, 原因)
        """
        checks = {}
        
        # 1. Gas费用检查（更严格）
        eth_gas = features[0]  # ETH Gas (Gwei)
        btc_fee = features[1]  # BTC Fee (sat/vB)
        checks['gas'] = eth_gas < 30 or btc_fee < 15
        if not checks['gas']:
            return False, f"Gas费用过高 (ETH: {eth_gas:.2f} Gwei, BTC: {btc_fee} sat/vB)"
        
        # 2. 数据完整性检查
        news_count = features[15] if len(features) > 15 else 0
        ai_up = features[22] if len(features) > 22 else 0
        ai_down = features[23] if len(features) > 23 else 0
        checks['data'] = news_count >= 8 and (ai_up + ai_down) > 0
        if not checks['data']:
            return False, f"数据不足 (新闻: {news_count}条, AI预测: {ai_up + ai_down}个)"
        
        # 3. 市场状态检查
        fear_greed = features[19] if len(features) > 19 else 50
        checks['market'] = 25 < fear_greed < 75
        if not checks['market']:
            return False, f"市场情绪极端 (恐惧贪婪指数: {fear_greed})"
        
        # 4. 波动率检查（保守）
        volatility = features[7] if len(features) > 7 else 0
        checks['volatility'] = volatility < 0.04
        if not checks['volatility']:
            return False, f"波动率过高 ({volatility*100:.2f}%)"
        
        # 5. 账户状态检查
        checks['account'] = (
            len(self.existing_positions) < 3 and
            self.account_balance > 10  # 降低到10 USDT最低要求
        )
        if not checks['account']:
            return False, f"账户状态不允许 (持仓: {len(self.existing_positions)}, 余额: ${self.account_balance:.2f})"
        
        return True, "所有安全检查通过 ✅"
    
    # ==================== Layer 2: 信号评分 ====================
    
    def calculate_news_score(self, features: List[float], news_data: Optional[List] = None) -> float:
        """
        新闻信号评分（30%权重）
        
        重点：美联储、中美关系、关税政策
        """
        score = 50  # 中性基础分
        
        # 特征索引
        news_positive_pct = features[13] if len(features) > 13 else 0
        news_negative_pct = features[14] if len(features) > 14 else 0
        news_count = features[15] if len(features) > 15 else 0
        news_sentiment = features[16] if len(features) > 16 else 0
        
        # 1. 新闻情绪标签 (±15分)
        if news_sentiment == 1:      # 看涨
            score += 15
        elif news_sentiment == -1:   # 看跌
            score -= 15
        
        # 2. 正负面比例 (±10分)
        if news_positive_pct > 0.25 and news_negative_pct < 0.15:
            score += 10
        elif news_negative_pct > 0.25 and news_positive_pct < 0.15:
            score -= 10
        
        # 3. 新闻数量 (±5分)
        if news_count > 15:
            score += 5
        elif news_count < 5:
            score -= 5
        
        # 4. 高优先级关键词加权 (±10分)
        if news_data:
            high_priority_keywords = ['fed', 'federal reserve', 'powell', 'china', 'tariff', 'trade war']
            keyword_hits = sum(
                1 for kw in high_priority_keywords
                if any(kw in str(news).lower() for news in news_data)
            )
            
            if keyword_hits >= 2:
                # 强化信号
                if news_sentiment == 1:
                    score += 10
                elif news_sentiment == -1:
                    score -= 10
        
        return max(0, min(100, score))
    
    def calculate_price_score(self, features: List[float]) -> float:
        """
        价格信号评分（25%权重）
        
        保守原则：只认可温和变化
        """
        score = 50
        
        # 特征索引
        price_change_24h = features[5] if len(features) > 5 else 0
        volatility = features[7] if len(features) > 7 else 0
        trend = features[8] if len(features) > 8 else 0
        
        # 1. 趋势方向 (±15分)
        if trend == 1:       # 上涨
            score += 15
        elif trend == -1:    # 下跌
            score -= 15
        
        # 2. 24h涨跌幅 (±10分) - 温和优先
        if 0.5 < price_change_24h < 2.5:     # 温和上涨
            score += 10
        elif price_change_24h >= 2.5:        # 上涨过快
            score += 5
        elif -2.5 < price_change_24h < -0.5: # 温和下跌
            score -= 10
        elif price_change_24h <= -2.5:       # 下跌过快
            score -= 5
        
        # 3. 波动率 (±10分)
        if volatility < 0.015:      # 超低波动
            score += 10
        elif volatility < 0.025:    # 低波动
            score += 5
        elif volatility > 0.04:     # 高波动
            score -= 10
        
        return max(0, min(100, score))
    
    def calculate_sentiment_score(self, features: List[float]) -> float:
        """
        市场情绪评分（25%权重）
        
        保守原则：只在理想区间给高分
        """
        score = 50
        
        # 特征索引
        fear_greed = features[19] if len(features) > 19 else 50
        sentiment_label = features[20] if len(features) > 20 else 0
        
        # 1. 恐惧贪婪指数 (±15分)
        if 50 < fear_greed < 65:        # 理想区间：温和乐观
            score += 15
        elif 35 < fear_greed < 50:      # 温和悲观，可能机会
            score += 10
        elif fear_greed >= 75:          # 过度贪婪，危险
            score -= 15
        elif fear_greed <= 25:          # 过度恐惧，观望
            score -= 10
        
        # 2. 情绪标签 (±10分)
        if sentiment_label == 1:
            score += 10
        elif sentiment_label == -1:
            score -= 10
        
        return max(0, min(100, score))
    
    def calculate_ai_score(self, features: List[float]) -> float:
        """
        AI预测评分（20%权重）
        """
        score = 50
        
        # 特征索引
        ai_agreement = features[24] if len(features) > 24 else 0
        ai_consensus = features[25] if len(features) > 25 else 0
        ai_confidence = features[21] if len(features) > 21 else 0
        
        # 1. AI共识 (±10分)
        if ai_consensus == 1:      # 看涨共识
            score += 10
        elif ai_consensus == -1:   # 看跌共识
            score -= 10
        
        # 2. 一致性 (±10分)
        if ai_agreement > 0.7:     # 高一致性
            score += 10
        elif ai_agreement < 0.4:   # 低一致性
            score -= 5
        
        return max(0, min(100, score))
    
    def calculate_total_score(self, features: List[float], news_data: Optional[List] = None) -> Dict:
        """
        计算加权总分
        
        Returns:
            包含各维度分数和总分的字典
        """
        news_score = self.calculate_news_score(features, news_data)
        price_score = self.calculate_price_score(features)
        sentiment_score = self.calculate_sentiment_score(features)
        ai_score = self.calculate_ai_score(features)
        
        # 加权计算
        total_score = (
            news_score * self.weights['news'] +
            price_score * self.weights['price'] +
            sentiment_score * self.weights['sentiment'] +
            ai_score * self.weights['ai']
        )
        
        return {
            'news_score': round(news_score, 2),
            'price_score': round(price_score, 2),
            'sentiment_score': round(sentiment_score, 2),
            'ai_score': round(ai_score, 2),
            'total_score': round(total_score, 2)
        }
    
    # ==================== Layer 3: 保守决策 ====================
    
    def calculate_consistency(self, features: List[float]) -> float:
        """
        计算各维度一致性
        
        Returns:
            一致性分数 0-1
        """
        signals = []
        
        # 新闻方向
        if len(features) > 16 and features[16] != 0:
            signals.append(features[16])
        
        # 价格趋势
        if len(features) > 8 and features[8] != 0:
            signals.append(features[8])
        
        # 市场情绪
        if len(features) > 20 and features[20] != 0:
            signals.append(features[20])
        
        # AI预测
        if len(features) > 25 and features[25] != 0:
            signals.append(features[25])
        
        if not signals:
            return 0.5
        
        # 计算一致性
        positive_count = signals.count(1)
        negative_count = signals.count(-1)
        
        max_count = max(positive_count, negative_count)
        consistency = max_count / len(signals)
        
        return consistency
    
    def make_decision(self, total_score: float, features: List[float]) -> Tuple[str, float, str]:
        """
        保守决策逻辑
        
        Returns:
            (action, confidence, reason)
        """
        consistency = self.calculate_consistency(features)
        fear_greed = features[19] if len(features) > 19 else 50
        
        # 看涨决策（严格标准）
        if (total_score > self.thresholds['buy_score'] and
            consistency > self.thresholds['min_consistency'] and
            fear_greed < 70):
            
            return "BUY", total_score, "多维度强烈看涨信号（一致性{:.0%}）".format(consistency)
        
        # 看跌决策（严格标准）
        elif (total_score < self.thresholds['sell_score'] and
              consistency > self.thresholds['min_consistency'] and
              fear_greed > 30):
            
            return "SELL", 100 - total_score, "多维度强烈看跌信号（一致性{:.0%}）".format(consistency)
        
        # 观望（保守）
        else:
            reasons = []
            if total_score >= self.thresholds['sell_score'] and total_score <= self.thresholds['buy_score']:
                reasons.append(f"分数在中性区间({total_score:.0f})")
            if consistency <= self.thresholds['min_consistency']:
                reasons.append(f"一致性不足({consistency:.0%})")
            if fear_greed >= 70:
                reasons.append(f"市场过度贪婪({fear_greed})")
            elif fear_greed <= 30:
                reasons.append(f"市场过度恐慌({fear_greed})")
            
            reason = "信号不够明确或市场状态不佳：" + "，".join(reasons) if reasons else "保守观望"
            return "HOLD", 50, reason
    
    # ==================== Layer 4: 仓位计算 ====================
    
    def calculate_stop_loss_percent(self, volatility: float) -> float:
        """
        根据波动率选择止损百分比
        
        保守策略：波动率越高，止损越宽
        """
        if volatility < 0.01:
            return 0.015    # 1.5%
        elif volatility < 0.02:
            return 0.020    # 2%
        elif volatility < 0.03:
            return 0.025    # 2.5%
        else:
            return 0.030    # 3%
    
    def calculate_position_and_stops(
        self,
        entry_price: float,
        direction: str,
        volatility: float
    ) -> Dict:
        """
        计算仓位大小、止损和止盈
        
        核心公式：仓位 = (总资金 × 风险比例) / (入场价 - 止损价)
        
        Args:
            entry_price: 入场价格
            direction: "BUY" or "SELL"
            volatility: 当前波动率
            
        Returns:
            包含仓位、止损、止盈等信息的字典
        """
        # 1. 根据波动率选择止损百分比
        stop_loss_percent = self.calculate_stop_loss_percent(volatility)
        
        # 2. 计算止损价
        if direction == "BUY":
            stop_loss_price = entry_price * (1 - stop_loss_percent)
        else:
            stop_loss_price = entry_price * (1 + stop_loss_percent)
        
        # 3. 计算止损距离
        stop_distance = abs(entry_price - stop_loss_price)
        
        # 4. 反推仓位大小（核心公式）
        risk_amount = self.account_balance * self.risk_percent
        position_size = risk_amount / stop_distance
        
        # 5. 验证仓位限制（最多15%资金）
        max_position_value = self.account_balance * 0.15
        position_value = position_size * entry_price
        
        if position_value > max_position_value:
            position_size = max_position_value / entry_price
            actual_risk = position_size * stop_distance / self.account_balance
            logger.warning(f"⚠️ 仓位受限，实际风险: {actual_risk*100:.2f}%")
        else:
            actual_risk = self.risk_percent
        
        # 6. 计算分批止盈（风险收益比 > 2:1）
        risk_distance = stop_distance
        
        if direction == "BUY":
            take_profit_1 = entry_price + (risk_distance * 1.5)  # 1.5倍风险
            take_profit_2 = entry_price + (risk_distance * 2.5)  # 2.5倍风险
            take_profit_3 = entry_price + (risk_distance * 4.0)  # 4倍风险
        else:
            take_profit_1 = entry_price - (risk_distance * 1.5)
            take_profit_2 = entry_price - (risk_distance * 2.5)
            take_profit_3 = entry_price - (risk_distance * 4.0)
        
        # 7. 计算预期盈亏
        max_loss = -risk_amount
        # 加权平均：50%@1.5x + 30%@2.5x + 20%@4x = 2.35x
        expected_profit = risk_amount * (0.5 * 1.5 + 0.3 * 2.5 + 0.2 * 4.0)
        
        return {
            'position_size': round(position_size, 8),
            'position_value': round(position_size * entry_price, 2),
            'position_percent': round((position_size * entry_price / self.account_balance) * 100, 2),
            'stop_loss': round(stop_loss_price, 2),
            'stop_loss_percent': round(stop_loss_percent * 100, 2),
            'take_profit_1': round(take_profit_1, 2),  # 卖50%
            'take_profit_2': round(take_profit_2, 2),  # 卖30%
            'take_profit_3': round(take_profit_3, 2),  # 卖20%
            'max_loss': round(max_loss, 2),
            'expected_profit': round(expected_profit, 2),
            'risk_reward_ratio': round(expected_profit / abs(max_loss), 2),
            'actual_risk_percent': round(actual_risk * 100, 2)
        }
    
    # ==================== 主决策接口 ====================
    
    def analyze(self, features: List[float], news_data: Optional[List] = None) -> Dict:
        """
        完整决策分析
        
        Args:
            features: 26维特征向量
            news_data: 新闻原始数据（可选）
            
        Returns:
            完整的决策报告
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Layer 1: 安全检查
        safety_pass, safety_reason = self.safety_check(features)
        
        if not safety_pass:
            return {
                'timestamp': timestamp,
                'decision': {
                    'action': 'HOLD',
                    'confidence': 0,
                    'reason': f"安全检查未通过: {safety_reason}"
                },
                'safety_checks': {
                    'passed': False,
                    'reason': safety_reason
                },
                'signals': None,
                'position': None,
                'risk_management': {
                    'account_balance': self.account_balance,
                    'risk_percent': self.risk_percent * 100,
                    'max_risk_amount': round(self.account_balance * self.risk_percent, 2),
                    'existing_positions': len(self.existing_positions)
                }
            }
        
        # Layer 2: 信号评分
        scores = self.calculate_total_score(features, news_data)
        consistency = self.calculate_consistency(features)
        
        # Layer 3: 决策
        action, confidence, reason = self.make_decision(scores['total_score'], features)
        
        # Layer 4: 仓位计算（仅在BUY/SELL时）
        position_info = None
        if action in ['BUY', 'SELL']:
            entry_price = features[4] if len(features) > 4 else 0
            volatility = features[7] if len(features) > 7 else 0
            
            if entry_price > 0:
                position_info = self.calculate_position_and_stops(
                    entry_price, action, volatility
                )
        
        # 构建完整报告
        result = {
            'timestamp': timestamp,
            'decision': {
                'action': action,
                'confidence': round(confidence, 2),
                'reason': reason
            },
            'signals': {
                'news_score': scores['news_score'],
                'price_score': scores['price_score'],
                'sentiment_score': scores['sentiment_score'],
                'ai_score': scores['ai_score'],
                'total_score': scores['total_score'],
                'consistency': round(consistency, 2)
            },
            'position': position_info,
            'risk_management': {
                'account_balance': self.account_balance,
                'risk_percent': self.risk_percent * 100,
                'max_risk_amount': round(self.account_balance * self.risk_percent, 2),
                'existing_positions': len(self.existing_positions)
            },
            'safety_checks': {
                'passed': True,
                'reason': safety_reason
            },
            'weights': self.weights,
            'thresholds': self.thresholds
        }
        
        return result
    
    def format_decision_report(self, result: Dict) -> str:
        """
        格式化决策报告为可读文本
        """
        lines = []
        lines.append("=" * 70)
        lines.append("📊 交易决策报告")
        lines.append("=" * 70)
        lines.append(f"时间: {result['timestamp']}")
        lines.append("")
        
        # 决策结果
        decision = result['decision']
        action_emoji = "🟢" if decision['action'] == "BUY" else ("🔴" if decision['action'] == "SELL" else "⚪")
        lines.append(f"{action_emoji} 决策: {decision['action']}")
        lines.append(f"   置信度: {decision['confidence']:.0f}%")
        lines.append(f"   原因: {decision['reason']}")
        lines.append("")
        
        # 信号分析
        if result['signals']:
            signals = result['signals']
            lines.append("📡 信号分析:")
            lines.append(f"   新闻信号: {signals['news_score']:.0f}/100 (权重30%)")
            lines.append(f"   价格信号: {signals['price_score']:.0f}/100 (权重25%)")
            lines.append(f"   情绪信号: {signals['sentiment_score']:.0f}/100 (权重25%)")
            lines.append(f"   AI信号: {signals['ai_score']:.0f}/100 (权重20%)")
            lines.append(f"   总分: {signals['total_score']:.0f}/100")
            lines.append(f"   一致性: {signals['consistency']*100:.0f}%")
            lines.append("")
        
        # 仓位信息
        if result['position']:
            pos = result['position']
            lines.append("💰 仓位管理:")
            lines.append(f"   仓位大小: {pos['position_size']:.8f} (${pos['position_value']:,.2f})")
            lines.append(f"   仓位占比: {pos['position_percent']:.2f}%")
            lines.append(f"   止损价: ${pos['stop_loss']:,.2f} (-{pos['stop_loss_percent']:.2f}%)")
            lines.append(f"   止盈目标:")
            lines.append(f"      目标1 (50%): ${pos['take_profit_1']:,.2f}")
            lines.append(f"      目标2 (30%): ${pos['take_profit_2']:,.2f}")
            lines.append(f"      目标3 (20%): ${pos['take_profit_3']:,.2f}")
            lines.append(f"   最大亏损: ${pos['max_loss']:,.2f}")
            lines.append(f"   期望盈利: ${pos['expected_profit']:,.2f}")
            lines.append(f"   风险收益比: {pos['risk_reward_ratio']}:1")
            lines.append("")
        
        # 风险管理
        if result['risk_management']:
            risk = result['risk_management']
            lines.append("🛡️ 风险管理:")
            lines.append(f"   账户余额: ${risk['account_balance']:,.2f}")
            lines.append(f"   单笔风险: {risk['risk_percent']:.2f}%")
            lines.append(f"   最大风险金额: ${risk['max_risk_amount']:,.2f}")
            lines.append(f"   当前持仓数: {risk['existing_positions']}")
            lines.append("")
        
        # 安全检查
        safety = result['safety_checks']
        status = "✅ 通过" if safety['passed'] else "❌ 未通过"
        lines.append(f"🔒 安全检查: {status}")
        lines.append(f"   {safety['reason']}")
        lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 创建决策引擎
    engine = DecisionEngine(account_balance=10000, risk_percent=0.015)
    
    # 模拟26维特征向量
    # [0-1: Gas, 2-3: Gas适合性, 4-9: 价格数据, 10-12: 价格扩展, 
    #  13-16: 新闻情绪, 17-20: 市场情绪, 21-25: AI预测]
    features = [
        15.0,  # [0] ETH Gas (Gwei)
        8.0,   # [1] BTC Fee (sat/vB)
        1,     # [2] ETH适合交易
        1,     # [3] BTC适合交易
        50000, # [4] 当前价格
        1.5,   # [5] 24h涨跌 (%)
        1000000, # [6] 成交量
        0.02,  # [7] 波动率
        1,     # [8] 趋势 (1=上涨)
        51000, # [9] 最高价
        49500, # [10] 最低价
        49800, # [11] 开盘价
        0.65,  # [12] 相对强弱指数 (RSI/100)
        0.30,  # [13] 新闻正面比例
        0.10,  # [14] 新闻负面比例
        12,    # [15] 新闻数量
        1,     # [16] 新闻情绪标签 (1=看涨)
        0.72,  # [17] 新闻置信度
        0.68,  # [18] 市场置信度
        58,    # [19] 恐惧贪婪指数
        1,     # [20] 市场情绪标签 (1=看涨)
        0.75,  # [21] AI平均置信度
        2,     # [22] AI看涨数量
        1,     # [23] AI看跌数量
        0.75,  # [24] AI一致性
        1      # [25] AI共识 (1=看涨)
    ]
    
    # 执行决策分析
    result = engine.analyze(features)
    
    # 打印报告
    print(engine.format_decision_report(result))
    
    # 也可以获取JSON格式
    import json
    print("\n" + "=" * 70)
    print("JSON格式输出:")
    print("=" * 70)
    print(json.dumps(result, indent=2, ensure_ascii=False))
