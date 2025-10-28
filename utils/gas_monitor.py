"""
Gas费用监控模块
监控BTC和ETH的Gas费用
"""

import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GasFeeMonitor:
    """Gas费用监控器 - 只监控BTC和ETH"""
    
    def __init__(self, etherscan_key=""):
        """
        初始化Gas监控器
        
        Args:
            etherscan_key: Etherscan API密钥
        """
        self.etherscan_key = etherscan_key
        self.gas_history = []
    
    def get_eth_gas_estimate(self, gas_price_wei=2000000000):
        """
        获取ETH Gas估算
        
        Args:
            gas_price_wei: Gas价格（wei），默认2 Gwei
        
        Returns:
            Gas估算信息
        """
        try:
            url = "https://api.etherscan.io/v2/api"
            params = {
                "chainid": "1",
                "module": "gastracker",
                "action": "gasestimate",
                "gasprice": str(gas_price_wei),
                "apikey": self.etherscan_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                result = data["result"]
                logger.info(f"ETH Gas估算成功: {result}")
                return {
                    "asset": "ETH",
                    "network": "Ethereum",
                    "timestamp": datetime.now(),
                    "estimate": result,
                    "gas_price_gwei": gas_price_wei / 1e9,
                    "unit": "Gwei"
                }
            else:
                logger.warning(f"Etherscan API错误: {data.get('message', 'Unknown')}")
                return None
            
        except Exception as e:
            logger.error(f"获取ETH Gas估算失败: {e}")
            return None
    
    def get_eth_avg_gas_price(self, days=7):
        """
        获取ETH平均Gas价格
        
        Args:
            days: 获取最近几天的数据，默认7天
        
        Returns:
            平均Gas价格信息
        """
        try:
            from datetime import timedelta
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = "https://api.etherscan.io/v2/api"
            params = {
                "chainid": "1",
                "module": "stats",
                "action": "dailyavggasprice",
                "startdate": start_date.strftime("%Y-%m-%d"),
                "enddate": end_date.strftime("%Y-%m-%d"),
                "sort": "desc",
                "apikey": self.etherscan_key
            }
            
            # 增加超时时间并添加重试
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, params=params, timeout=30)
                    data = response.json()
                    break
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        logger.warning(f"Etherscan API超时，重试 {attempt + 1}/{max_retries}")
                        continue
                    else:
                        logger.error("Etherscan API超时，已达最大重试次数")
                        return None
            
            if data.get("status") == "1" and data.get("result"):
                results = data["result"]
                
                # 计算平均值
                if results:
                    avg_prices = []
                    for item in results:
                        # Gas价格单位是Wei，转换为Gwei
                        gas_price_gwei = float(item.get("avgGasPrice_Wei", 0)) / 1e9
                        avg_prices.append(gas_price_gwei)
                    
                    overall_avg = sum(avg_prices) / len(avg_prices) if avg_prices else 0
                    
                    gas_info = {
                        "asset": "ETH",
                        "network": "Ethereum",
                        "timestamp": datetime.now(),
                        "period_days": days,
                        "avg_gas_price_gwei": round(overall_avg, 2),
                        "latest_gas_price_gwei": round(avg_prices[0], 2) if avg_prices else 0,
                        "min_gas_price_gwei": round(min(avg_prices), 2) if avg_prices else 0,
                        "max_gas_price_gwei": round(max(avg_prices), 2) if avg_prices else 0,
                        "data_points": len(results),
                        "unit": "Gwei"
                    }
                    
                    logger.info(f"ETH平均Gas（{days}天）: {gas_info['avg_gas_price_gwei']} Gwei")
                    return gas_info
            else:
                logger.warning(f"获取平均Gas价格失败: {data.get('message', 'Unknown')}")
                return None
            
        except Exception as e:
            logger.error(f"获取ETH平均Gas价格失败: {e}")
            return None
    
    def get_eth_gas_from_ethgasstation(self):
        """
        从Etherscan V2 API获取Gas价格（备用方案）
        """
        try:
            url = "https://api.etherscan.io/v2/api"
            params = {
                "chainid": "1",
                "module": "gastracker",
                "action": "gasoracle",
                "apikey": self.etherscan_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                result = data["result"]
                # V2 API返回的是浮点数Gwei
                gas_info = {
                    "asset": "ETH",
                    "network": "Ethereum",
                    "timestamp": datetime.now(),
                    "safe_gas": float(result.get("SafeGasPrice", 0)),
                    "propose_gas": float(result.get("ProposeGasPrice", 0)),
                    "fast_gas": float(result.get("FastGasPrice", 0)),
                    "base_fee": float(result.get("suggestBaseFee", 0)),
                    "unit": "Gwei",
                    "source": "etherscan_gastracker"
                }
                logger.info(f"ETH Gas (Oracle): 安全={gas_info['safe_gas']:.4f}, 建议={gas_info['propose_gas']:.4f}, 快速={gas_info['fast_gas']:.4f} Gwei")
                return gas_info
            
            return None
            
        except Exception as e:
            logger.error(f"从Etherscan GasTracker获取失败: {e}")
            return None
    
    def get_eth_gas(self):
        """
        获取ETH当前Gas信息（综合）
        
        Returns:
            综合Gas信息
        """
        try:
            # 方法1: 尝试获取平均Gas价格（最近7天）
            avg_gas = self.get_eth_avg_gas_price(days=7)
            
            if avg_gas:
                gas_info = {
                    "asset": "ETH",
                    "network": "Ethereum",
                    "timestamp": datetime.now(),
                    "current_avg_gas": avg_gas["avg_gas_price_gwei"],
                    "latest_gas": avg_gas["latest_gas_price_gwei"],
                    "min_gas_7d": avg_gas["min_gas_price_gwei"],
                    "max_gas_7d": avg_gas["max_gas_price_gwei"],
                    "unit": "Gwei",
                    "source": "etherscan_stats"
                }
                
                logger.info(f"ETH Gas: 当前={gas_info['latest_gas']} Gwei, 7日均值={gas_info['current_avg_gas']} Gwei")
                return gas_info
            
            # 方法2: 如果失败，使用GasOracle API（更简单的API）
            logger.info("尝试使用备用Gas API...")
            gas_oracle = self.get_eth_gas_from_ethgasstation()
            
            if gas_oracle:
                # 转换为统一格式
                gas_info = {
                    "asset": "ETH",
                    "network": "Ethereum",
                    "timestamp": datetime.now(),
                    "current_avg_gas": gas_oracle["propose_gas"],
                    "latest_gas": gas_oracle["propose_gas"],
                    "min_gas_7d": gas_oracle["safe_gas"],
                    "max_gas_7d": gas_oracle["fast_gas"],
                    "unit": "Gwei",
                    "source": "etherscan_gastracker"
                }
                
                logger.info(f"ETH Gas (备用): 建议={gas_info['latest_gas']} Gwei")
                return gas_info
            
            return None
            
        except Exception as e:
            logger.error(f"获取ETH Gas失败: {e}")
            return None
    
    def get_btc_fee(self):
        """
        获取BTC网络费用（使用mempool.space API）
        BTC使用sat/vB作为单位
        """
        try:
            url = "https://mempool.space/api/v1/fees/recommended"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            fee_info = {
                "asset": "BTC",
                "network": "Bitcoin",
                "timestamp": datetime.now(),
                "fastest_fee": data["fastestFee"],      # sat/vB
                "half_hour_fee": data["halfHourFee"],   # sat/vB
                "hour_fee": data["hourFee"],            # sat/vB
                "economy_fee": data.get("economyFee", data["hourFee"]),  # sat/vB
                "minimum_fee": data.get("minimumFee", 1),
                "unit": "sat/vB"
            }
            logger.info(f"BTC Fee: {fee_info['half_hour_fee']} sat/vB")
            return fee_info
            
        except Exception as e:
            logger.error(f"获取BTC费用失败: {e}")
            return None
    
    def get_all_fees(self):
        """获取BTC和ETH的费用"""
        fees = {}
        
        # ETH Gas
        eth_gas = self.get_eth_gas()
        if eth_gas:
            fees["ETH"] = eth_gas
        
        # BTC Fee
        btc_fee = self.get_btc_fee()
        if btc_fee:
            fees["BTC"] = btc_fee
        
        return fees
    
    def should_trade_eth(self, max_gas_gwei=50):
        """判断ETH Gas费是否适合交易"""
        gas_info = self.get_eth_gas()
        
        if not gas_info:
            logger.warning("无法获取ETH Gas信息")
            return False
        
        # 使用最新的Gas价格
        current_gas = gas_info["latest_gas"]
        
        if current_gas <= max_gas_gwei:
            logger.info(f"✅ ETH Gas合理: {current_gas} <= {max_gas_gwei} Gwei")
            return True
        else:
            logger.warning(f"⚠️ ETH Gas过高: {current_gas} > {max_gas_gwei} Gwei")
            return False
    
    def should_trade_btc(self, max_fee_sat_vb=20):
        """判断BTC费用是否适合交易"""
        fee_info = self.get_btc_fee()
        
        if not fee_info:
            logger.warning("无法获取BTC费用信息")
            return False
        
        current_fee = fee_info["half_hour_fee"]
        
        if current_fee <= max_fee_sat_vb:
            logger.info(f"✅ BTC费用合理: {current_fee} <= {max_fee_sat_vb} sat/vB")
            return True
        else:
            logger.warning(f"⚠️ BTC费用过高: {current_fee} > {max_fee_sat_vb} sat/vB")
            return False
    
    def check_trading_conditions(self, max_eth_gas=50, max_btc_fee=20):
        """
        检查BTC和ETH的交易条件
        
        Returns:
            dict: {"BTC": bool, "ETH": bool, "details": {...}}
        """
        result = {
            "BTC": False,
            "ETH": False,
            "details": {}
        }
        
        # 检查ETH
        eth_suitable = self.should_trade_eth(max_eth_gas)
        result["ETH"] = eth_suitable
        result["details"]["ETH"] = self.get_eth_gas()
        
        # 检查BTC
        btc_suitable = self.should_trade_btc(max_btc_fee)
        result["BTC"] = btc_suitable
        result["details"]["BTC"] = self.get_btc_fee()
        
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    monitor = GasFeeMonitor()
    
    eth_gas = monitor.get_ethereum_gas()
    print(f"ETH Gas: {eth_gas}")
    
    should_trade = monitor.should_trade_now(network="Ethereum", max_gas_gwei=30)
    print(f"适合交易: {should_trade}")
