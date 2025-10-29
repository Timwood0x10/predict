#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
杠杆交易测试脚本 - 展示不同杠杆倍数下的止盈止损
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.decision_engine import DecisionEngine


class LeverageCalculator:
    """杠杆交易计算器"""
    
    def __init__(self, capital: float, leverage: int):
        """
        初始化杠杆计算器
        
        Args:
            capital: 本金（USDT）
            leverage: 杠杆倍数
        """
        self.capital = capital
        self.leverage = leverage
        self.position_value = capital * leverage  # 持仓价值
    
    def calculate_position(
        self,
        entry_price: float,
        risk_percent: float = 0.01,
        stop_loss_percent: float = 0.02
    ):
        """
        计算杠杆交易的仓位、止损和止盈
        
        Args:
            entry_price: 入场价格
            risk_percent: 本金风险比例（默认1%）
            stop_loss_percent: 止损百分比（默认2%）
        
        Returns:
            交易计划字典
        """
        # 1. 计算可以开多少仓位（BTC数量）
        position_size = self.position_value / entry_price
        
        # 2. 计算止损价（做多）
        stop_loss_price = entry_price * (1 - stop_loss_percent)
        
        # 3. 计算每个点的盈亏（杠杆放大）
        # 价格变动1%，本金变动 = 1% * 杠杆倍数
        price_change_1pct = entry_price * 0.01
        profit_per_1pct = position_size * price_change_1pct  # 1%涨跌的盈亏
        
        # 4. 计算止损时的亏损
        price_drop = entry_price - stop_loss_price
        total_loss = position_size * price_drop
        capital_loss_percent = (total_loss / self.capital) * 100
        
        # 5. 验证是否会爆仓
        # 爆仓价 = 入场价 * (1 - 1/杠杆倍数)
        liquidation_price = entry_price * (1 - 0.98 / self.leverage)  # 98%考虑维持保证金
        liquidation_percent = ((entry_price - liquidation_price) / entry_price) * 100
        
        # 6. 计算分批止盈价格
        # 保守策略：风险收益比至少2:1
        risk_distance = entry_price - stop_loss_price
        
        take_profit_1 = entry_price + (risk_distance * 1.5)  # 1.5倍风险
        take_profit_2 = entry_price + (risk_distance * 2.5)  # 2.5倍风险
        take_profit_3 = entry_price + (risk_distance * 4.0)  # 4倍风险
        
        # 7. 计算各目标的盈利
        profit_at_tp1 = position_size * (take_profit_1 - entry_price) * 0.50  # 卖50%
        profit_at_tp2 = position_size * (take_profit_2 - entry_price) * 0.30  # 卖30%
        profit_at_tp3 = position_size * (take_profit_3 - entry_price) * 0.20  # 卖20%
        total_expected_profit = profit_at_tp1 + profit_at_tp2 + profit_at_tp3
        
        # 8. 计算盈利占本金的百分比
        profit_percent_tp1 = (profit_at_tp1 / self.capital) * 100
        profit_percent_tp2 = (profit_at_tp2 / self.capital) * 100
        profit_percent_tp3 = (profit_at_tp3 / self.capital) * 100
        total_profit_percent = (total_expected_profit / self.capital) * 100
        
        return {
            'capital': self.capital,
            'leverage': self.leverage,
            'position_value': self.position_value,
            'position_size': position_size,
            'entry_price': entry_price,
            
            # 止损信息
            'stop_loss_price': stop_loss_price,
            'stop_loss_percent': stop_loss_percent * 100,
            'max_loss': total_loss,
            'capital_loss_percent': capital_loss_percent,
            
            # 爆仓信息
            'liquidation_price': liquidation_price,
            'liquidation_percent': liquidation_percent,
            'margin_to_liquidation': capital_loss_percent / liquidation_percent if liquidation_percent > 0 else 0,
            
            # 止盈信息
            'take_profit_1': {
                'price': take_profit_1,
                'percent_change': ((take_profit_1 - entry_price) / entry_price) * 100,
                'profit': profit_at_tp1,
                'profit_percent': profit_percent_tp1,
                'position_close': 50
            },
            'take_profit_2': {
                'price': take_profit_2,
                'percent_change': ((take_profit_2 - entry_price) / entry_price) * 100,
                'profit': profit_at_tp2,
                'profit_percent': profit_percent_tp2,
                'position_close': 30
            },
            'take_profit_3': {
                'price': take_profit_3,
                'percent_change': ((take_profit_3 - entry_price) / entry_price) * 100,
                'profit': profit_at_tp3,
                'profit_percent': profit_percent_tp3,
                'position_close': 20
            },
            
            # 总计
            'total_expected_profit': total_expected_profit,
            'total_profit_percent': total_profit_percent,
            'risk_reward_ratio': total_expected_profit / abs(total_loss) if total_loss != 0 else 0
        }
    
    def format_report(self, plan: dict) -> str:
        """格式化交易计划报告"""
        lines = []
        lines.append("=" * 80)
        lines.append("💰 杠杆交易计划")
        lines.append("=" * 80)
        
        # 基本信息
        lines.append(f"\n📊 账户信息:")
        lines.append(f"   本金: ${plan['capital']:.2f} USDT")
        lines.append(f"   杠杆: {plan['leverage']}x")
        lines.append(f"   持仓价值: ${plan['position_value']:,.2f} USDT")
        lines.append(f"   入场价: ${plan['entry_price']:,.2f}")
        lines.append(f"   仓位大小: {plan['position_size']:.8f} BTC")
        
        # 风险管理
        lines.append(f"\n🛡️ 风险管理:")
        lines.append(f"   止损价: ${plan['stop_loss_price']:,.2f} (-{plan['stop_loss_percent']:.2f}%)")
        lines.append(f"   止损亏损: ${plan['max_loss']:.2f} USDT")
        lines.append(f"   本金损失: {plan['capital_loss_percent']:.2f}%")
        lines.append(f"   ")
        lines.append(f"   ⚠️  爆仓价: ${plan['liquidation_price']:,.2f} (-{plan['liquidation_percent']:.2f}%)")
        
        # 风险警告
        if plan['capital_loss_percent'] > 50:
            lines.append(f"   🚨 警告: 止损会导致本金损失超过50%！")
        
        if plan['liquidation_percent'] < plan['stop_loss_percent'] * 1.5:
            lines.append(f"   🚨 危险: 止损价接近爆仓价，建议降低杠杆！")
        
        # 止盈计划
        lines.append(f"\n🎯 止盈目标:")
        
        for i, tp_key in enumerate(['take_profit_1', 'take_profit_2', 'take_profit_3'], 1):
            tp = plan[tp_key]
            lines.append(f"   目标{i} ({tp['position_close']}%仓位):")
            lines.append(f"      价格: ${tp['price']:,.2f} (+{tp['percent_change']:.2f}%)")
            lines.append(f"      盈利: ${tp['profit']:.2f} USDT")
            lines.append(f"      本金收益: +{tp['profit_percent']:.2f}%")
        
        # 总计
        lines.append(f"\n📈 预期收益:")
        lines.append(f"   总盈利: ${plan['total_expected_profit']:.2f} USDT")
        lines.append(f"   本金收益: +{plan['total_profit_percent']:.2f}%")
        lines.append(f"   风险收益比: {plan['risk_reward_ratio']:.2f}:1")
        
        # 建议
        lines.append(f"\n💡 交易建议:")
        if plan['leverage'] >= 50:
            lines.append(f"   ⚠️  {plan['leverage']}x杠杆风险极高，建议降低到20x以下")
        elif plan['leverage'] >= 20:
            lines.append(f"   ⚠️  {plan['leverage']}x杠杆风险较高，适合经验丰富的交易者")
        else:
            lines.append(f"   ✅ {plan['leverage']}x杠杆相对稳健")
        
        if plan['risk_reward_ratio'] >= 2.0:
            lines.append(f"   ✅ 风险收益比良好 ({plan['risk_reward_ratio']:.2f}:1)")
        else:
            lines.append(f"   ⚠️  风险收益比偏低 ({plan['risk_reward_ratio']:.2f}:1)")
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)


def test_leverage_scenarios():
    """测试不同杠杆场景"""
    print("=" * 80)
    print("🧪 杠杆交易测试 - 多场景对比")
    print("=" * 80)
    
    # BTC入场价
    entry_price = 50000
    
    # 测试场景
    scenarios = [
        {
            'name': '场景1: 100U × 100x 杠杆（超高风险）',
            'capital': 100,
            'leverage': 100,
            'stop_loss_percent': 0.005  # 0.5% 止损（杠杆高，止损要小）
        },
        {
            'name': '场景2: 100U × 50x 杠杆（高风险）',
            'capital': 100,
            'leverage': 50,
            'stop_loss_percent': 0.01  # 1% 止损
        },
        {
            'name': '场景3: 100U × 20x 杠杆（中等风险）',
            'capital': 100,
            'leverage': 20,
            'stop_loss_percent': 0.02  # 2% 止损
        },
        {
            'name': '场景4: 100U × 10x 杠杆（稳健）',
            'capital': 100,
            'leverage': 10,
            'stop_loss_percent': 0.03  # 3% 止损
        },
        {
            'name': '场景5: 100U × 5x 杠杆（保守）',
            'capital': 100,
            'leverage': 5,
            'stop_loss_percent': 0.04  # 4% 止损
        },
        {
            'name': '场景6: 1000U × 100x 杠杆（对比）',
            'capital': 1000,
            'leverage': 100,
            'stop_loss_percent': 0.005  # 0.5% 止损
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"📋 {scenario['name']}")
        print(f"{'='*80}")
        
        calc = LeverageCalculator(scenario['capital'], scenario['leverage'])
        plan = calc.calculate_position(
            entry_price=entry_price,
            stop_loss_percent=scenario['stop_loss_percent']
        )
        
        print(calc.format_report(plan))
        results.append({'name': scenario['name'], 'plan': plan})
    
    # 对比总结
    print("\n" + "="*80)
    print("📊 场景对比总结")
    print("="*80)
    
    print(f"\n{'场景':<40} {'持仓价值':<15} {'止损亏损':<15} {'本金损失%':<12} {'预期收益%':<12} {'风险收益比':<10}")
    print("-" * 120)
    
    for result in results:
        name = result['name'].split(':')[1].strip()[:35]
        plan = result['plan']
        print(f"{name:<40} "
              f"${plan['position_value']:>10,.0f}    "
              f"${plan['max_loss']:>10,.2f}    "
              f"{plan['capital_loss_percent']:>8.2f}%     "
              f"{plan['total_profit_percent']:>8.2f}%     "
              f"{plan['risk_reward_ratio']:>6.2f}:1")
    
    # 关键建议
    print("\n" + "="*80)
    print("💡 关键建议")
    print("="*80)
    
    print("""
1. 杠杆越高，止损必须越严格：
   - 100x杠杆：建议止损 0.3-0.5%（价格波动150-250美元）
   - 50x杠杆：建议止损 0.5-1%（价格波动250-500美元）
   - 20x杠杆：建议止损 1-2%（价格波动500-1000美元）
   - 10x杠杆：建议止损 2-3%（价格波动1000-1500美元）

2. 100U × 100x的风险：
   - 持仓价值10000U，但本金只有100U
   - 价格下跌0.5%就会触发止损，亏损50U（本金50%）
   - 价格下跌1%左右就会爆仓，血本无归
   - 极度不适合新手，即使老手也要谨慎

3. 推荐策略：
   - 新手：5-10x杠杆，止损2-3%
   - 进阶：10-20x杠杆，止损1-2%
   - 专业：20-50x杠杆，止损0.5-1%
   - 极限：50-100x杠杆，只适合超短线，极小仓位

4. 资金管理：
   - 单笔交易风险控制在总资金的1-2%
   - 100U账户，建议单次亏损不超过1-2U
   - 使用高杠杆时，必须用更小的仓位或更严格的止损

5. 实战建议：
   - 100U × 100x 不如 1000U × 10x（相同持仓价值，风险更低）
   - 高杠杆要配合小仓位，不要满仓
   - 设置好止损后，严格执行，不要侥幸
   - 波动率高的时候，降低杠杆或减少仓位
""")
    
    print("="*80)


def main():
    """主函数"""
    test_leverage_scenarios()
    
    print("\n" + "="*80)
    print("✅ 测试完成！")
    print("="*80)
    print("\n建议阅读:")
    print("  - DECISION_ENGINE_GUIDE.md: 决策引擎使用指南")
    print("  - 风险警告: 杠杆交易风险极高，请务必谨慎！")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
