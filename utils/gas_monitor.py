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
    
    def get_eth_gas(self):
        """获取ETH网络Gas价格"""
        try:
            url = "https://api.etherscan.io/api"
            params = {
                "module": "gastracker",
                "action": "gasoracle",
                "apikey": self.etherscan_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data["status"] == "1":
                result = data["result"]
                gas_info = {
                    "asset": "ETH",
                    "network": "Ethereum",
                    "timestamp": datetime.now(),
                    "safe_gas": int(result["SafeGasPrice"]),
                    "propose_gas": int(result["ProposeGasPrice"]),
                    "fast_gas": int(result["FastGasPrice"]),
                    "base_fee": float(result.get("suggestBaseFee", 0)),
                    "unit": "Gwei"
                }
                logger.info(f"ETH Gas: {gas_info['propose_gas']} Gwei")
                return gas_info
            else:
                logger.warning(f"Etherscan API错误: {data.get('message', 'Unknown')}")
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
        
        current_gas = gas_info["propose_gas"]
        
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
