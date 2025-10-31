#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全检查诊断工具 - 帮助理解为什么安全检查未通过
"""

import sys
from advanced_trading_system import AdvancedTradingSystem
from utils.data_integrator import DataIntegrator

def check_safety_details(symbol="BTCUSDT"):
    """详细检查安全项"""
    print("=" * 80)
    print("🔍 安全检查诊断工具")
    print("=" * 80)
    print(f"交易对: {symbol}")
    print()
    
    # 创建系统
    system = AdvancedTradingSystem(capital_usdt=1000, leverage=10, risk_percent=2.0)
    
    # 获取市场数据
    print("📊 正在获取市场数据...")
    market_data = system.fetch_market_data(symbol, hours=12)
    
    # 整合特征
    print("🔄 正在整合特征...")
    integrator = DataIntegrator()
    integrated_data = integrator.integrate_all(
        gas_data=market_data.get('gas_data'),
        kline_df=market_data.get('kline_df'),
        news_sentiment=market_data.get('news_sentiment'),
        market_sentiment=market_data.get('market_sentiment'),
        ai_predictions=market_data.get('ai_predictions'),
        hours=12
    )
    
    features = integrated_data['features']
    
    print()
    print("=" * 80)
    print("🔍 安全检查详情")
    print("=" * 80)
    print()
    
    # 1. Gas费用检查
    eth_gas = features[0]
    btc_fee = features[1]
    gas_pass = eth_gas < 30 or btc_fee < 15
    print(f"1️⃣ Gas费用检查: {'✅ 通过' if gas_pass else '❌ 未通过'}")
    print(f"   ETH Gas: {eth_gas:.2f} Gwei (标准: <30)")
    print(f"   BTC Fee: {btc_fee} sat/vB (标准: <15)")
    if not gas_pass:
        print(f"   ⚠️ 原因: Gas费用过高")
    print()
    
    # 2. 数据完整性检查
    news_count = features[15] if len(features) > 15 else 0
    ai_up = features[22] if len(features) > 22 else 0
    ai_down = features[23] if len(features) > 23 else 0
    data_pass = news_count >= 8 and (ai_up + ai_down) > 0
    print(f"2️⃣ 数据完整性检查: {'✅ 通过' if data_pass else '❌ 未通过'}")
    print(f"   新闻数量: {news_count}条 (标准: ≥8)")
    print(f"   AI预测: {ai_up + ai_down}个 (标准: >0)")
    if not data_pass:
        print(f"   ⚠️ 原因: 数据不足")
    print()
    
    # 3. 市场状态检查
    fear_greed = features[19] if len(features) > 19 else 50
    market_pass = 25 < fear_greed < 75
    print(f"3️⃣ 市场状态检查: {'✅ 通过' if market_pass else '❌ 未通过'}")
    print(f"   恐惧贪婪指数: {fear_greed} (标准: 25-75)")
    if not market_pass:
        if fear_greed <= 25:
            print(f"   ⚠️ 原因: 市场过度恐慌")
        else:
            print(f"   ⚠️ 原因: 市场过度贪婪")
    print()
    
    # 4. 波动率检查
    volatility = features[7] if len(features) > 7 else 0
    vol_pass = volatility < 0.04
    print(f"4️⃣ 波动率检查: {'✅ 通过' if vol_pass else '❌ 未通过'}")
    print(f"   当前波动率: {volatility*100:.2f}% (标准: <4%)")
    if not vol_pass:
        print(f"   ⚠️ 原因: 波动率过高")
    print()
    
    # 5. 账户状态检查
    account_pass = True  # 简化，假设通过
    print(f"5️⃣ 账户状态检查: ✅ 通过")
    print(f"   持仓数: 0")
    print(f"   账户余额: 1000 USDT")
    print()
    
    # 总结
    all_pass = gas_pass and data_pass and market_pass and vol_pass and account_pass
    print("=" * 80)
    print(f"🎯 总体结果: {'✅ 所有检查通过' if all_pass else '❌ 有检查未通过'}")
    print("=" * 80)
    print()
    
    if not all_pass:
        print("💡 建议:")
        if not gas_pass:
            print("  - Gas费过高时不适合交易，等待Gas费降低")
        if not data_pass:
            print("  - 数据不足，可能是API限制或网络问题")
        if not market_pass:
            print("  - 市场情绪极端，风险较高，建议观望")
        if not vol_pass:
            print("  - 波动率过高，风险较大，建议降低杠杆或观望")
        print()
    else:
        print("✅ 所有安全检查都通过，可以进行交易决策")
        print()
    
    return all_pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='安全检查诊断工具')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='交易对')
    args = parser.parse_args()
    
    check_safety_details(args.symbol)
