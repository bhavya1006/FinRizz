"""
Simple Pyth Price Fetcher

A lightweight module for fetching cryptocurrency prices from Pyth Network
without heavy dependencies.
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class SimplePythPriceFetcher:
    """Simple price fetcher with minimal dependencies"""
    
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        
        # Essential price feeds (you can add more from config.py)
        self.feeds = {
            "BTC/USD": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
            "ETH/USD": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
            "SOL/USD": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
            "BNB/USD": "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",
            "USDC/USD": "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
            "USDT/USD": "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b"
        }
    
    def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Symbol like 'BTC/USD'
            
        Returns:
            Price data dictionary or None
        """
        if symbol not in self.feeds:
            print(f"Symbol {symbol} not supported")
            return None
            
        feed_id = self.feeds[symbol]
        url = f"{self.base_url}/api/latest_price_feeds"
        
        try:
            # Use proper parameter format for Python requests
            response = requests.get(
                url, 
                params={"ids[]": feed_id, "verbose": "true", "binary": "false"},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if not data:
                return None
                
            price_data = data[0]["price"]
            price = float(price_data["price"]) * (10 ** price_data["expo"])
            confidence = float(price_data["conf"]) * (10 ** price_data["expo"])
            
            return {
                "symbol": symbol,
                "price": price,
                "confidence": confidence,
                "timestamp": datetime.fromtimestamp(price_data["publish_time"]).isoformat(),
                "raw_data": price_data
            }
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Get prices for multiple symbols"""
        results = {}
        
        valid_symbols = [s for s in symbols if s in self.feeds]
        if not valid_symbols:
            return results
            
        feed_ids = [self.feeds[symbol] for symbol in valid_symbols]
        url = f"{self.base_url}/api/latest_price_feeds"
        
        try:
            # Build parameters for multiple IDs
            params = [("ids[]", feed_id) for feed_id in feed_ids]
            params.extend([("verbose", "true"), ("binary", "false")])
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                return results
                
            # Map feed IDs back to symbols
            feed_to_symbol = {self.feeds[symbol]: symbol for symbol in valid_symbols}
            
            for item in data:
                feed_id = item["id"]
                # The API returns feed IDs without 0x prefix
                # Our config has them with 0x prefix, so we need to match properly
                
                matching_symbol = None
                for symbol in valid_symbols:
                    config_feed_id = self.feeds[symbol].replace('0x', '')
                    if config_feed_id.lower() == feed_id.lower():
                        matching_symbol = symbol
                        break
                
                if matching_symbol:
                    price_data = item["price"]
                    price = float(price_data["price"]) * (10 ** price_data["expo"])
                    confidence = float(price_data["conf"]) * (10 ** price_data["expo"])
                    
                    results[matching_symbol] = {
                        "symbol": matching_symbol,
                        "price": price,
                        "confidence": confidence,
                        "timestamp": datetime.fromtimestamp(price_data["publish_time"]).isoformat()
                    }
                    
        except Exception as e:
            print(f"Error fetching multiple prices: {e}")
            
        return results
    
    def available_symbols(self) -> List[str]:
        """Get list of available symbols"""
        return list(self.feeds.keys())


def quick_price_check():
    """Quick function to check current crypto prices"""
    fetcher = SimplePythPriceFetcher()
    
    print("🚀 Quick Crypto Price Check")
    print("=" * 40)
    
    # Get major crypto prices
    symbols = ["BTC/USD", "ETH/USD", "SOL/USD", "USDC/USD"]
    prices = fetcher.get_multiple_prices(symbols)
    
    for symbol, data in prices.items():
        if data:
            print(f"💰 {symbol:<10} ${data['price']:>10,.4f}")
        else:
            print(f"❌ {symbol:<10} {'No data':>10}")
    
    print(f"\n⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    quick_price_check()

import requests
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class SimplePythPriceFetcher:
    """Simple price fetcher with minimal dependencies"""
    
    def __init__(self):
        self.base_url = "https://hermes.pyth.network"
        
        # Essential price feeds (you can add more from config.py)
        self.feeds = {
            "BTC/USD": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
            "ETH/USD": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
            "SOL/USD": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
            "BNB/USD": "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",
            "USDC/USD": "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
            "USDT/USD": "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b"
        }
    
    def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Symbol like 'BTC/USD'
            
        Returns:
            Price data dictionary or None
        """
        if symbol not in self.feeds:
            print(f"Symbol {symbol} not supported")
            return None
            
        feed_id = self.feeds[symbol]
        url = f"{self.base_url}/api/latest_price_feeds"
        
        params = {
            "ids": feed_id,
            "verbose": "true",
            "binary": "false"
        }
        
        try:
            # Use proper parameter format for Python requests
            response = requests.get(
                url, 
                params={"ids[]": feed_id, "verbose": "true", "binary": "false"},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if not data:
                return None
                
            price_data = data[0]["price"]
            price = float(price_data["price"]) * (10 ** price_data["expo"])
            confidence = float(price_data["conf"]) * (10 ** price_data["expo"])
            
            return {
                "symbol": symbol,
                "price": price,
                "confidence": confidence,
                "timestamp": datetime.fromtimestamp(price_data["publish_time"]).isoformat(),
                "raw_data": price_data
            }
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Get prices for multiple symbols"""
        results = {}
        
        valid_symbols = [s for s in symbols if s in self.feeds]
        if not valid_symbols:
            return results
            
        feed_ids = [self.feeds[symbol] for symbol in valid_symbols]
        url = f"{self.base_url}/api/latest_price_feeds"
        
        try:
            # Build parameters for multiple IDs
            params = [("ids[]", feed_id) for feed_id in feed_ids]
            params.extend([("verbose", "true"), ("binary", "false")])
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                return results
                
            # Map feed IDs back to symbols
            feed_to_symbol = {self.feeds[symbol]: symbol for symbol in valid_symbols}
            
            for item in data:
                feed_id = item["id"]
                if feed_id in feed_to_symbol:
                    symbol = feed_to_symbol[feed_id]
                    price_data = item["price"]
                    
                    price = float(price_data["price"]) * (10 ** price_data["expo"])
                    confidence = float(price_data["conf"]) * (10 ** price_data["expo"])
                    
                    results[symbol] = {
                        "symbol": symbol,
                        "price": price,
                        "confidence": confidence,
                        "timestamp": datetime.fromtimestamp(price_data["publish_time"]).isoformat()
                    }
                    
        except Exception as e:
            print(f"Error fetching multiple prices: {e}")
            
        return results
    
    def available_symbols(self) -> List[str]:
        """Get list of available symbols"""
        return list(self.feeds.keys())


def quick_price_check():
    """Quick function to check current crypto prices"""
    fetcher = SimplePythPriceFetcher()
    
    print("🚀 Quick Crypto Price Check")
    print("=" * 40)
    
    # Get major crypto prices
    symbols = ["BTC/USD", "ETH/USD", "SOL/USD", "USDC/USD"]
    prices = fetcher.get_multiple_prices(symbols)
    
    for symbol, data in prices.items():
        if data:
            print(f"💰 {symbol:<10} ${data['price']:>10,.4f}")
        else:
            print(f"❌ {symbol:<10} {'No data':>10}")
    
    print(f"\n⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    quick_price_check()