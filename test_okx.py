import os
import time
import schedule
from openai import OpenAI
import ccxt
import pandas as pd
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

# 初始化DeepSeek客户端
deepseek_client = OpenAI(
    api_key="sk-asj9zBIXzGJpbWz5lPs9cWpcXDexAGootwULVSKjjcifVZ7d",
    base_url="https://api.probex.top/v1/"
    # base_url="https://api.probex.top/v1/chat/completions"
)

# 初始化OKX交易所
exchange = ccxt.okx({
    'apiKey': 'xxxxx',
    'secret': 'xxxx',
    'password': 'xxxx',  # OKX需要交易密码
})

# 交易参数配置
TRADE_CONFIG = {
    'symbol': 'BTC/USDT:USDT',  # OKX的合约符号格式
    'amount': 0.0001,  # 交易数量 (BTC)
    'leverage': 10,  # 杠杆倍数
    'timeframe': '15m',  # 使用15分钟K线
    'limit': 96, # 24 小时数据
    'test_mode': False,  # 测试模式
}

# 全局变量存储历史数据
price_history = []
signal_history = []
position = None


def setup_exchange():
    """设置交易所参数"""
    try:
        # OKX设置杠杆
        exchange.set_leverage(
            TRADE_CONFIG['leverage'],
            TRADE_CONFIG['symbol'],
            {'mgnMode': 'cross'}  # 全仓模式，也可用'isolated'逐仓
        )
        print(f"设置杠杆倍数: {TRADE_CONFIG['leverage']}x")

        # 获取余额
        balance = exchange.fetch_balance()
        usdt_balance = balance['USDT']['free']
        print(f"当前USDT余额: {usdt_balance:.2f}")

        # 设置持仓模式 (双向持仓)
        # exchange.set_position_mode(False, TRADE_CONFIG['symbol'])
        print("设置单向持仓")

        return True
    except Exception as e:
        print(f"交易所设置失败: {e}")
        return False

def calculate_technical_indicators(df):
    """计算技术指标 - 来自第一个策略"""
    try:
        # MACD指标计算
        # 计算快速和慢速EMA
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        # 计算MACD线（快线减慢线）
        df['macd'] = df['ema_12'] - df['ema_26']
        # 计算信号线（MACD的9日EMA）
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        # 计算MACD柱状图
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # 相对强弱指数 (RSI-16)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=16).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=16).mean()
        rs = gain / loss
        df['rsi_16'] = 100 - (100 / (1 + rs))  # RSI = 100 - (100 / (1 + RS))

        # 布林带策略计算 (20日布林带)
        # 计算中轨（20日简单移动平均）
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        # 计算标准差
        bb_std = df['close'].rolling(window=20).std()
        # 计算上轨 (中轨 + 2倍标准差)
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        # 计算下轨 (中轨 - 2倍标准差)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        # 计算带宽 ((上轨 - 下轨) / 中轨)
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        # 计算%B指标 ((收盘价 - 下轨) / (上轨 - 下轨))
        df['bb_percent_b'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        # 填充NaN值
        df = df.bfill().ffill()

        return df
    except Exception as e:
        print(f"技术指标计算失败: {e}")
        return df



def get_btc_ohlcv():
    """获取BTC/USDT的K线数据"""
    try:
        # 获取最近10根K线
        ohlcv = exchange.fetch_ohlcv(TRADE_CONFIG['symbol'], TRADE_CONFIG['timeframe'], limit=TRADE_CONFIG['limit'])
        m_ohlcv = exchange.fetch_ohlcv(TRADE_CONFIG['symbol'], '1m', limit=100)
        # 转换为DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        # 一分钟
        m_df = pd.DataFrame(m_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        m_df['timestamp'] = pd.to_datetime(m_df['timestamp'], unit='ms')

        current_data = df.iloc[-1]
        previous_data = df.iloc[-2] if len(df) > 1 else current_data

         # 计算技术指标
        # df = calculate_technical_indicators(df)
        return {
            'price': current_data['close'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'high': current_data['high'],
            'low': current_data['low'],
            'volume': current_data['volume'],
            'timeframe': TRADE_CONFIG['timeframe'],
            'price_change': ((current_data['close'] - previous_data['close']) / previous_data['close']) * 100,
            'kline_data': df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].to_dict('records'),
            # 'kline_data': df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].tail(10).to_dict('records'),
            "m_df":m_df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].to_dict('records'),
            # 'technical_data': {
            #     'rsi_16': df['rsi_16'].tail(10).tolist(),
            #     'macd': df['macd'].tail(10).tolist(),
            #     'macd_signal': df['macd_signal'].tail(10).tolist(),
            #     'macd_histogram': df['macd_histogram'].tail(10).tolist(),
            #     'bollinger_bands': {
            #         'upper': df['bb_upper'].tail(10).tolist(),
            #         'middle': df['bb_middle'].tail(10).tolist(),
            #         'lower': df['bb_lower'].tail(10).tolist(),
            #         'bandwidth': df['bb_bandwidth'].tail(10).tolist(),
            #         'percent_b': df['bb_percent_b'].tail(10).tolist()
            #     }
            # },
        }
    except Exception as e:
        print(f"获取K线数据失败: {e}")
        return None


def get_current_position():
    """获取当前持仓情况"""
    try:
        positions = exchange.fetch_positions([TRADE_CONFIG['symbol']])

        for pos in positions:
            if pos['symbol'] == TRADE_CONFIG['symbol']:
                contracts = float(pos['contracts']) if pos['contracts'] else 0

                if contracts > 0:
                    return {
                        'side': pos['side'],  # 'long' or 'short'
                        'size': contracts,
                        'entry_price': float(pos['entryPrice']) if pos['entryPrice'] else 0,
                        'unrealized_pnl': float(pos['unrealizedPnl']) if pos['unrealizedPnl'] else 0,
                        'leverage': float(pos['leverage']) if pos['leverage'] else TRADE_CONFIG['leverage'],
                        'symbol': pos['symbol']
                    }

        return None

    except Exception as e:
        print(f"获取持仓失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_with_deepseek(price_data):
    """使用DeepSeek分析市场并生成交易信号"""

    # 添加当前价格到历史记录
    price_history.append(price_data)
    if len(price_history) > 20:
        price_history.pop(0)

    # 构建K线数据文本
    kline_text = f"【最近100根{TRADE_CONFIG['timeframe']}K线数据】\n"
    for i, kline in enumerate(price_data['kline_data']):
        print(kline)
        trend = "阳线" if kline['close'] > kline['open'] else "阴线"
        change = ((kline['close'] - kline['open']) / kline['open']) * 100
        kline_text += f"K线{i + 1}: {trend} 时间: {kline['timestamp']} 开盘:{kline['open']:.2f} 收盘:{kline['close']:.2f} 最高价:{kline['high']} 最低价: {kline['low']} 涨跌:{change:+.2f}%\n"
    # 构建技术指标文本
    if len(price_history) >= 5:
        closes = [data['price'] for data in price_history[-5:]]
        sma_5 = sum(closes) / len(closes)
        price_vs_sma = ((price_data['price'] - sma_5) / sma_5) * 100

        indicator_text = f"【技术指标】\n5周期均价: {sma_5:.2f}\n当前价格相对于均线: {price_vs_sma:+.2f}%"
    else:
        indicator_text = "【技术指标】\n数据不足计算技术指标"

    # 最近1m的k线数据
    kline_text_1m = f"【最近100根1mK线数据】\n"
    for i, kline in enumerate(price_data['m_df']):
        trend = "阳线" if kline['close'] > kline['open'] else "阴线"
        change = ((kline['close'] - kline['open']) / kline['open']) * 100
        kline_text_1m += f"K线{i + 1}: {trend} 时间: {kline['timestamp']} 开盘:{kline['open']:.2f} 收盘:{kline['close']:.2f} 最高价:{kline['high']} 最低价: {kline['low']} 涨跌:{change:+.2f}%\n"

    # 添加上次交易信号
    signal_text = ""
    if signal_history:
        last_signal = signal_history[-1]
        signal_text = f"\n【上次交易信号】\n信号: {last_signal.get('signal', 'N/A')}\n信心: {last_signal.get('confidence', 'N/A')}"

    # 添加当前持仓信息
    current_pos = get_current_position()
    position_text = "无持仓" if not current_pos else f"{current_pos['side']}仓, 数量: {current_pos['size']}, 盈亏: {current_pos['unrealized_pnl']:.2f}USDT"

    prompt = f"""
    你是一个专业的加密货币交易分析师。请基于以下BTC/USDT {TRADE_CONFIG['timeframe']}周期数据进行分析：

    {kline_text}

    {kline_text_1m}

    {indicator_text}

    {signal_text}

    【当前行情】
    - 当前价格: ${price_data['price']:,.2f}
    - 时间: {price_data['timestamp']}
    - 本K线最高: ${price_data['high']:,.2f}
    - 本K线最低: ${price_data['low']:,.2f}
    - 本K线成交量: {price_data['volume']:.2f} BTC
    - 价格变化: {price_data['price_change']:+.2f}%
    - 当前持仓: {position_text}


    【防频繁交易重要原则】
    1. **趋势持续性优先**: 不要因单根K线或短期波动改变整体趋势判断
    2. **持仓稳定性**: 除非趋势明确强烈反转，否则保持现有持仓方向
    3. **反转确认**: 需要至少2-3个技术指标同时确认趋势反转才改变信号
    4. **成本意识**: 减少不必要的仓位调整，每次交易都有成本



    【分析要求】
    1. 基于{TRADE_CONFIG['timeframe']}K线趋势以及1mk线趋势,你需要根据k线数据计算出macd,rsi,动量等指标
    2. 基于15mk和指标判断当前的趋势,再根据1mk线分析当前对否一个合理的交易点位,并给出交易信号: BUY(买入) / SELL(卖出) / HOLD(观望)
    3. 简要分析理由（考虑趋势连续性、支撑阻力、成交量等因素）
    4. 基于技术分析建议合理的止损价位
    5. 基于技术分析建议合理的止盈价位
    6. 评估信号信心程度
    7. 给出达到止盈止损的大概时间(需要持仓多久)

    请用以下JSON格式回复：
    {{
        "signal": "BUY|SELL|HOLD",
        "reason": "分析理由",
        "stop_loss": int(具体价格),
        "take_profit": int(具体价格),
        "hold_time": 预期持仓时间,
        "confidence": "HIGH|MEDIUM|LOW"
        "technical":"技术指标分析"
    }}
    """
    print("-"*30)
    print(TRADE_CONFIG['timeframe'])
    print(f"prompt:{prompt}")
    result = ""
    try:
        response = deepseek_client.chat.completions.create(
            # model="deepseek-chat",
            model="deepseek-v3.1",
            # group= "default",
            messages=[
                {"role": "system",
                 "content": f"您是一位急需资金为母亲治疗癌症的交易员，你现在需要从加密货币交易市场赚取足够的金额治疗你的母亲，专注于{TRADE_CONFIG['timeframe']}周期趋势分析。请结合K线形态和技术指标做出判断。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )

        # 安全解析JSON
        result = response.choices[0].message.content
        start_idx = result.find('{')
        end_idx = result.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = result[start_idx:end_idx]
            signal_data = json.loads(json_str)
        else:
            print(f"无法解析JSON: {result}")
            return None

        # 保存信号到历史记录
        signal_data['timestamp'] = price_data['timestamp']
        signal_history.append(signal_data)
        if len(signal_history) > 30:
            signal_history.pop(0)

        return signal_data

    except Exception as e:
        print(f"DeepSeek分析失败: {e}")
        print(f"result: {result}")
        return None


def execute_trade(signal_data, price_data):
    """执行交易"""
    global position

    current_position = get_current_position()

    print(f"交易信号: {signal_data['signal']}")
    print(f"信心程度: {signal_data['confidence']}")
    print(f"理由: {signal_data['reason']}")
    print(f"止损: ${signal_data['stop_loss']:,.2f}")
    print(f"止盈: ${signal_data['take_profit']:,.2f}")
    print(f"持仓大概时间: ${signal_data['hold_time']}")
    print(f"技术指标分析: ${signal_data['technical']}")
    print(f"当前持仓: {current_position}")

    if TRADE_CONFIG['test_mode']:
        print("测试模式 - 仅模拟交易")
        return

    try:
        if signal_data['signal'] == 'BUY':
            if current_position and current_position['side'] == 'short':
                print("平空仓并开多仓...")
                # 平空仓
                exchange.create_market_order(
                    TRADE_CONFIG['symbol'],
                    'buy',
                    current_position['size'],
                    params={'reduceOnly': True, 'tag': 'f1ee03b510d5SUDE'}
                )
                time.sleep(1)
                # 开多仓
                exchange.create_market_order(
                    TRADE_CONFIG['symbol'],
                    'buy',
                    TRADE_CONFIG['amount'],
                    params={'tag': 'f1ee03b510d5SUDE'}
                )
            elif not current_position:
                print("开多仓...")
                exchange.create_market_order(
                    TRADE_CONFIG['symbol'],
                    'buy',
                    TRADE_CONFIG['amount'],
                    params={'tag': 'f1ee03b510d5SUDE'}
                )
            else:
                print("已持有多仓，无需操作")

        elif signal_data['signal'] == 'SELL':
            if current_position and current_position['side'] == 'long':
                print("平多仓并开空仓...")
                # 平多仓
                exchange.create_market_order(
                    TRADE_CONFIG['symbol'],
                    'sell',
                    current_position['size'],
                    params={'reduceOnly': True, 'tag': 'f1ee03b510d5SUDE'}
                )
                time.sleep(1)
                # 开空仓
                exchange.create_market_order(
                    TRADE_CONFIG['symbol'],
                    'sell',
                    TRADE_CONFIG['amount'],
                    params={'tag': 'f1ee03b510d5SUDE'}
                )
            elif not current_position:
                print("开空仓...")
                exchange.create_market_order(
                    TRADE_CONFIG['symbol'],
                    'sell',
                    TRADE_CONFIG['amount'],
                    params={'tag': 'f1ee03b510d5SUDE'}
                )
            else:
                print("已持有空仓，无需操作")

        elif signal_data['signal'] == 'HOLD':
            print("建议观望，不执行交易")
            return

        print("订单执行成功")
        # 更新持仓信息
        time.sleep(2)
        position = get_current_position()
        print(f"更新后持仓: {position}")

    except Exception as e:
        print(f"订单执行失败: {e}")
        import traceback
        traceback.print_exc()


def trading_bot():
    """主交易机器人函数"""
    print("\n" + "=" * 60)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 获取K线数据
    price_data = get_btc_ohlcv()
    if not price_data:
        return

    print(f"BTC当前价格: ${price_data['price']:,.2f}")
    print(f"数据周期: {TRADE_CONFIG['timeframe']}")
    # print(f"价格变化: {price_data['price_change']:+.2f}%")

    # 2. 使用DeepSeek分析
    signal_data = analyze_with_deepseek(price_data)
    if not signal_data:
        return

    # 3. 执行交易
    execute_trade(signal_data, price_data)


def main():
    """主函数"""
    print("BTC/USDT OKX自动交易机器人启动成功！")
    ac = exchange.fetch_balance()

    if TRADE_CONFIG['test_mode']:
        print("当前为模拟模式，不会真实下单")
    else:
        print("实盘交易模式，请谨慎操作！")

    print(f"交易周期: {TRADE_CONFIG['timeframe']}")
    print("已启用K线数据分析和持仓跟踪功能")

    # 设置交易所
    if not setup_exchange():
        print("交易所初始化失败，程序退出")
        return
    

    # 根据时间周期设置执行频率
    if TRADE_CONFIG['timeframe'] == '1h':
        schedule.every().hour.at(":01").do(trading_bot)
        print("执行频率: 每小时一次")
    elif TRADE_CONFIG['timeframe'] == '15m':
        schedule.every(15).minutes.do(trading_bot)
        print("执行频率: 每15分钟一次")
    else:
        schedule.every().hour.at(":01").do(trading_bot)
        print("执行频率: 每小时一次")

    # 立即执行一次
    trading_bot()

    # 循环执行
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()