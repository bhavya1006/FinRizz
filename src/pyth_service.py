"""
Pyth Network Price Service

This module provides functionality to fetch real-time price data from Pyth Network
using their REST API. It includes both synchronous and asynchronous methods.
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import json

import requests
import aiohttp
from asyncio_throttle import Throttler

from .config import PRICE_FEEDS, PYTH_CONFIG, REQUEST_CONFIG


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PythPriceService:
    """
    Service class for fetching real-time price data from Pyth Network
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize the Pyth Price Service
        
        Args:
            base_url: Base URL for Pyth API (optional, uses config default)
        """
        self.base_url = base_url or PYTH_CONFIG["base_url"]
        self.endpoints = PYTH_CONFIG["endpoints"]
        self.session = None
        
        # Rate limiting (Pyth allows generous limits, but good practice)
        self.throttler = Throttler(rate_limit=10, period=1)
        
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            self.session.close()

    def get_price_feed_ids(self) -> Dict[str, str]:
        """
        Get all available price feed IDs
        
        Returns:
            Dictionary mapping asset symbols to feed IDs
        """
        return PRICE_FEEDS.copy()

    def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest price for a single asset
        
        Args:
            symbol: Asset symbol (e.g., 'BTC/USD')
            
        Returns:
            Price data dictionary or None if failed
        """
        if symbol not in PRICE_FEEDS:
            logger.error(f"Symbol {symbol} not found in price feeds")
            return None
            
        feed_id = PRICE_FEEDS[symbol]
        return self._fetch_price_data([feed_id], symbol)

    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get latest prices for multiple assets
        
        Args:
            symbols: List of asset symbols
            
        Returns:
            Dictionary mapping symbols to their price data
        """
        valid_symbols = [s for s in symbols if s in PRICE_FEEDS]
        if not valid_symbols:
            logger.warning("No valid symbols provided")
            return {}
            
        feed_ids = [PRICE_FEEDS[symbol] for symbol in valid_symbols]
        
        # Batch requests if too many symbols
        all_data = {}
        batch_size = REQUEST_CONFIG["batch_size"]
        
        for i in range(0, len(valid_symbols), batch_size):
            batch_symbols = valid_symbols[i:i + batch_size]
            batch_feed_ids = feed_ids[i:i + batch_size]
            
            batch_data = self._fetch_price_data(batch_feed_ids, batch_symbols)
            if batch_data:
                all_data.update(batch_data)
                
        return all_data

    def _fetch_price_data(self, feed_ids: List[str], symbols: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
        """
        Internal method to fetch price data from Pyth API
        
        Args:
            feed_ids: List of Pyth feed IDs
            symbols: Single symbol string or list of symbols
            
        Returns:
            Price data dictionary
        """
        url = f"{self.base_url}{self.endpoints['latest_price_feeds']}"
        
        params = {
            "ids[]": feed_ids,
            "verbose": "true",
            "binary": "false"
        }
        
        for attempt in range(REQUEST_CONFIG["max_retries"]):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=REQUEST_CONFIG["timeout"]
                )
                response.raise_for_status()
                
                data = response.json()
                return self._parse_price_data(data, symbols)
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < REQUEST_CONFIG["max_retries"] - 1:
                    time.sleep(REQUEST_CONFIG["retry_delay"] * (attempt + 1))
                else:
                    logger.error(f"All {REQUEST_CONFIG['max_retries']} attempts failed")
                    return None
                    
        return None

    def _parse_price_data(self, raw_data: List, symbols: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Parse raw API response into structured price data
        
        Args:
            raw_data: Raw response from Pyth API (list of price data)
            symbols: Symbol(s) corresponding to the data
            
        Returns:
            Parsed price data
        """
        parsed_data = {}
        
        if not raw_data or not isinstance(raw_data, list):
            logger.warning("No data in API response")
            return parsed_data
            
        symbol_list = symbols if isinstance(symbols, list) else [symbols]
        
        for item in raw_data:
            feed_id = item.get("id")
            if not feed_id:
                continue
            
            # Find matching symbol (API returns IDs without 0x prefix)
            matching_symbol = None
            for symbol in symbol_list:
                if symbol in PRICE_FEEDS:
                    config_feed_id = PRICE_FEEDS[symbol].replace('0x', '')
                    if config_feed_id.lower() == feed_id.lower():
                        matching_symbol = symbol
                        break
            
            if not matching_symbol:
                continue
                
            price_data = item.get("price", {})
            
            if not price_data:
                continue
                
            # Extract price information
            price = float(price_data.get("price", 0)) * (10 ** price_data.get("expo", 0))
            confidence = float(price_data.get("conf", 0)) * (10 ** price_data.get("expo", 0))
            
            parsed_data[matching_symbol] = {
                "symbol": matching_symbol,
                "price": price,
                "confidence_interval": confidence,
                "timestamp": datetime.fromtimestamp(price_data.get("publish_time", 0)).isoformat(),
                "feed_id": feed_id,
                "raw_price": price_data.get("price"),
                "expo": price_data.get("expo"),
                "publish_time": price_data.get("publish_time")
            }
            
        return parsed_data if isinstance(symbols, list) else parsed_data.get(symbols, None)

    # Async methods for better performance
    async def get_latest_price_async(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Async version of get_latest_price"""
        if symbol not in PRICE_FEEDS:
            logger.error(f"Symbol {symbol} not found in price feeds")
            return None
            
        feed_id = PRICE_FEEDS[symbol]
        return await self._fetch_price_data_async([feed_id], symbol)

    async def get_multiple_prices_async(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Async version of get_multiple_prices"""
        valid_symbols = [s for s in symbols if s in PRICE_FEEDS]
        if not valid_symbols:
            logger.warning("No valid symbols provided")
            return {}
            
        feed_ids = [PRICE_FEEDS[symbol] for symbol in valid_symbols]
        
        # Batch requests
        all_data = {}
        batch_size = REQUEST_CONFIG["batch_size"]
        
        tasks = []
        for i in range(0, len(valid_symbols), batch_size):
            batch_symbols = valid_symbols[i:i + batch_size]
            batch_feed_ids = feed_ids[i:i + batch_size]
            
            task = self._fetch_price_data_async(batch_feed_ids, batch_symbols)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                all_data.update(result)
                
        return all_data

    async def _fetch_price_data_async(self, feed_ids: List[str], symbols: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
        """Async version of _fetch_price_data"""
        url = f"{self.base_url}{self.endpoints['latest_price_feeds']}"
        
        # Build parameters for multiple IDs
        params = [("ids[]", feed_id) for feed_id in feed_ids]
        params.extend([("verbose", "true"), ("binary", "false")])
        
        async with self.throttler:
            for attempt in range(REQUEST_CONFIG["max_retries"]):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=params, timeout=REQUEST_CONFIG["timeout"]) as response:
                            response.raise_for_status()
                            data = await response.json()
                            return self._parse_price_data(data, symbols)
                            
                except Exception as e:
                    logger.warning(f"Async request attempt {attempt + 1} failed: {e}")
                    if attempt < REQUEST_CONFIG["max_retries"] - 1:
                        await asyncio.sleep(REQUEST_CONFIG["retry_delay"] * (attempt + 1))
                    else:
                        logger.error(f"All {REQUEST_CONFIG['max_retries']} attempts failed")
                        return None
                        
        return None

    def stream_prices(self, symbols: List[str], interval: float = 5.0, callback=None):
        """
        Stream real-time prices with specified interval
        
        Args:
            symbols: List of symbols to stream
            interval: Update interval in seconds
            callback: Optional callback function for each price update
        """
        logger.info(f"Starting price stream for {symbols} with {interval}s interval")
        
        try:
            while True:
                prices = self.get_multiple_prices(symbols)
                
                if callback:
                    callback(prices)
                else:
                    print(f"\n=== Price Update at {datetime.now().isoformat()} ===")
                    for symbol, data in prices.items():
                        if data:
                            print(f"{symbol}: ${data['price']:.4f} (±${data['confidence_interval']:.4f})")
                        else:
                            print(f"{symbol}: No data available")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Price stream stopped by user")
        except Exception as e:
            logger.error(f"Price stream error: {e}")


def get_available_symbols() -> List[str]:
    """Get list of all available symbols"""
    return list(PRICE_FEEDS.keys())


def print_price_info(symbol: str, price_data: Dict[str, Any]) -> None:
    """Pretty print price information"""
    if not price_data:
        print(f"No data available for {symbol}")
        return
        
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                                 {symbol:^20}                                   ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Price: ${price_data['price']:>20.4f}                                           ║
║ Confidence: ±${price_data['confidence_interval']:>16.4f}                       ║
║ Timestamp: {price_data['timestamp']:>20}                                        ║
║ Feed ID: {price_data['feed_id'][:20]}...                                        ║
╚══════════════════════════════════════════════════════════════════════════════════╝
""")