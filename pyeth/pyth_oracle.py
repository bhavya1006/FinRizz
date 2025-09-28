"""
Complete Pyth Oracle Integration
Handles: Hermes data fetch -> On-chain update -> Price consumption

This single file replaces multiple scattered implementations with a unified approach.
"""

import os
import time
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass

# Optional blockchain imports - will be checked at runtime
try:
    from web3 import Web3
    from web3.middleware import SignAndSendRawMiddlewareBuilder
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Web3 libraries not available: {e}")
    WEB3_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

load_dotenv()

# Pyth Contract ABI (simplified - only the functions we need)
PYTH_ABI = [
    {
        "inputs": [{"name": "updateData", "type": "bytes[]"}],
        "name": "updatePriceFeeds",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"name": "id", "type": "bytes32"}],
        "name": "getPrice",
        "outputs": [
            {
                "components": [
                    {"name": "price", "type": "int64"},
                    {"name": "conf", "type": "uint64"},
                    {"name": "expo", "type": "int32"},
                    {"name": "publishTime", "type": "uint256"}
                ],
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "id", "type": "bytes32"}],
        "name": "getPriceUnsafe",
        "outputs": [
            {
                "components": [
                    {"name": "price", "type": "int64"},
                    {"name": "conf", "type": "uint64"},
                    {"name": "expo", "type": "int32"},
                    {"name": "publishTime", "type": "uint256"}
                ],
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getUpdateFee",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Core price feeds (you can expand this)
PRICE_FEEDS = {
    "BTC/USD": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    "ETH/USD": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace", 
    "SOL/USD": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    "BNB/USD": "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",
    "USDC/USD": "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
    "USDT/USD": "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b"
}

@dataclass
class PriceData:
    """Structured price data"""
    symbol: str
    price: float
    confidence: float
    timestamp: datetime
    feed_id: str
    vaa_data: Optional[bytes] = None  # For on-chain updates

class PythOracle:
    """
    Complete Pyth Oracle Integration
    
    Handles the full workflow:
    1. Fetch prices from Hermes API
    2. Update prices on-chain via updatePriceFeeds  
    3. Read prices from on-chain contract
    """
    
    def __init__(self, rpc_url: str = None, private_key: str = None, pyth_contract: str = None):
        """
        Initialize Pyth Oracle
        
        Args:
            rpc_url: Ethereum RPC endpoint (from env if not provided)
            private_key: Wallet private key (from env if not provided)  
            pyth_contract: Pyth contract address (from env if not provided)
        """
        # Hermes API configuration
        self.hermes_url = "https://hermes.pyth.network"
        
        # Blockchain configuration
        self.rpc_url = rpc_url or os.getenv("RPC_URL")
        self.private_key = private_key or os.getenv("PRIVATE_KEY") 
        self.pyth_contract_address = pyth_contract or os.getenv("PYTH_CONTRACT")
        
        # Initialize Web3 if blockchain config provided
        self.w3 = None
        self.account = None
        self.pyth_contract = None
        
        if self.rpc_url and self.private_key and self.pyth_contract_address:
            self._init_blockchain()
    
    def _init_blockchain(self):
        """Initialize blockchain connections"""
        if not WEB3_AVAILABLE:
            print("❌ Web3 libraries not available. Install with: pip install web3 eth-account")
            return
            
        try:
            # Connect to blockchain
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            if not self.w3.is_connected():
                raise Exception("Failed to connect to blockchain")
            
            # Setup account and signing middleware
            self.account = Account.from_key(self.private_key)
            
            # Use the new middleware builder pattern
            signing_middleware = SignAndSendRawMiddlewareBuilder.build(self.account)
            self.w3.middleware_onion.add(signing_middleware)
            
            # Initialize Pyth contract
            self.pyth_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.pyth_contract_address),
                abi=PYTH_ABI
            )
            
            print(f"✅ Blockchain connected - Account: {self.account.address}")
            print(f"✅ Pyth contract: {self.pyth_contract_address}")
            print(f"✅ Using ThirdWeb RPC: {self.rpc_url}")
            
        except Exception as e:
            print(f"❌ Blockchain initialization failed: {e}")
            self.w3 = None
    
    # STEP 1: FETCH FROM HERMES
    def fetch_prices(self, symbols: Union[str, List[str]]) -> Dict[str, PriceData]:
        """
        Fetch latest prices from Hermes API
        
        Args:
            symbols: Single symbol or list of symbols (e.g., 'BTC/USD' or ['BTC/USD', 'ETH/USD'])
            
        Returns:
            Dictionary mapping symbols to PriceData objects
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        # Validate symbols
        valid_symbols = [s for s in symbols if s in PRICE_FEEDS]
        if not valid_symbols:
            print(f"❌ No valid symbols found in {symbols}")
            return {}
        
        feed_ids = [PRICE_FEEDS[symbol] for symbol in valid_symbols]
        
        try:
            # Fetch from Hermes
            response = requests.get(
                f"{self.hermes_url}/api/latest_price_feeds",
                params={"ids[]": feed_ids, "verbose": "true", "binary": "false"},
                timeout=10
            )
            response.raise_for_status()
            
            raw_data = response.json()
            return self._parse_price_data(raw_data, valid_symbols)
            
        except Exception as e:
            print(f"❌ Failed to fetch prices: {e}")
            return {}
    
    def fetch_vaa_data(self, symbols: Union[str, List[str]]) -> Dict[str, bytes]:
        """
        Fetch VAA (Verifiable Action Approval) data for on-chain updates
        
        Args:
            symbols: Single symbol or list of symbols
            
        Returns:
            Dictionary mapping symbols to VAA bytes data
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        valid_symbols = [s for s in symbols if s in PRICE_FEEDS]
        if not valid_symbols:
            return {}
        
        feed_ids = [PRICE_FEEDS[symbol] for symbol in valid_symbols]
        
        try:
            response = requests.get(
                f"{self.hermes_url}/api/latest_vaas",
                params={"ids[]": feed_ids},
                timeout=10
            )
            response.raise_for_status()
            
            vaa_data = response.json()
            result = {}
            
            for i, symbol in enumerate(valid_symbols):
                if i < len(vaa_data):
                    # VAA data is returned as base64, convert to bytes
                    import base64
                    result[symbol] = base64.b64decode(vaa_data[i])
                    
            return result
            
        except Exception as e:
            print(f"❌ Failed to fetch VAA data: {e}")
            return {}
    
    # STEP 2: UPDATE ON-CHAIN
    def update_on_chain_prices(self, symbols: Union[str, List[str]]) -> bool:
        """
        Update price feeds on-chain using Pyth's updatePriceFeeds function
        
        Args:
            symbols: Symbols to update on-chain
            
        Returns:
            True if successful, False otherwise
        """
        if not self.w3 or not self.pyth_contract:
            print("❌ Blockchain not initialized. Check RPC_URL, PRIVATE_KEY, and PYTH_CONTRACT in .env")
            return False
        
        # Fetch VAA data for on-chain update
        vaa_data = self.fetch_vaa_data(symbols)
        if not vaa_data:
            print("❌ Failed to fetch VAA data for on-chain update")
            return False
        
        try:
            # Get update fee (no parameters needed for getUpdateFee)
            update_fee = self.pyth_contract.functions.getUpdateFee().call()
            
            # Prepare update data
            update_data = list(vaa_data.values())
            
            # Send transaction
            tx_hash = self.pyth_contract.functions.updatePriceFeeds(
                update_data
            ).transact({
                'from': self.account.address,
                'value': update_fee
            })
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ On-chain update successful - TX: {tx_hash.hex()}")
                return True
            else:
                print(f"❌ On-chain update failed - TX: {tx_hash.hex()}")
                return False
                
        except Exception as e:
            print(f"❌ On-chain update error: {e}")
            return False
    
    # STEP 3: CONSUME ON-CHAIN PRICES  
    def get_on_chain_price(self, symbol: str, safe: bool = True) -> Optional[PriceData]:
        """
        Read price from on-chain Pyth contract
        
        Args:
            symbol: Symbol to read (e.g., 'BTC/USD')
            safe: Use getPrice (safe) vs getPriceUnsafe (faster but less validation)
            
        Returns:
            PriceData object or None if failed
        """
        if not self.w3 or not self.pyth_contract:
            print("❌ Blockchain not initialized")
            return None
        
        if symbol not in PRICE_FEEDS:
            print(f"❌ Symbol {symbol} not supported")
            return None
        
        try:
            feed_id = PRICE_FEEDS[symbol]
            feed_id_bytes = bytes.fromhex(feed_id[2:])  # Remove 0x prefix
            
            if safe:
                price_struct = self.pyth_contract.functions.getPrice(feed_id_bytes).call()
            else:
                price_struct = self.pyth_contract.functions.getPriceUnsafe(feed_id_bytes).call()
            
            # Parse price struct: (price, conf, expo, publishTime)
            raw_price, confidence, expo, publish_time = price_struct
            
            # Convert to human readable price
            price = raw_price * (10 ** expo)
            conf = confidence * (10 ** expo)
            
            return PriceData(
                symbol=symbol,
                price=price,
                confidence=conf,
                timestamp=datetime.fromtimestamp(publish_time),
                feed_id=feed_id
            )
            
        except Exception as e:
            print(f"❌ Failed to read on-chain price for {symbol}: {e}")
            return None
    
    def _parse_price_data(self, raw_data: List, symbols: List[str]) -> Dict[str, PriceData]:
        """Parse raw Hermes API response"""
        parsed = {}
        
        for item in raw_data:
            feed_id = item.get("id", "")
            
            # Match feed ID to symbol
            matching_symbol = None
            for symbol in symbols:
                if PRICE_FEEDS[symbol].replace('0x', '').lower() == feed_id.lower():
                    matching_symbol = symbol
                    break
            
            if not matching_symbol:
                continue
            
            price_data = item.get("price", {})
            if not price_data:
                continue
            
            # Calculate human-readable price
            raw_price = float(price_data.get("price", 0))
            expo = price_data.get("expo", 0)
            price = raw_price * (10 ** expo)
            
            raw_conf = float(price_data.get("conf", 0))  
            confidence = raw_conf * (10 ** expo)
            
            parsed[matching_symbol] = PriceData(
                symbol=matching_symbol,
                price=price,
                confidence=confidence,
                timestamp=datetime.fromtimestamp(price_data.get("publish_time", 0)),
                feed_id=feed_id
            )
        
        return parsed

# Convenience functions for quick usage
def get_prices(symbols: Union[str, List[str]]) -> Dict[str, PriceData]:
    """Quick function to get current prices from Hermes"""
    oracle = PythOracle()
    return oracle.fetch_prices(symbols)

def update_and_read_prices(symbols: Union[str, List[str]]) -> Dict[str, PriceData]:
    """Update prices on-chain then read them back"""
    oracle = PythOracle()
    
    # Update on-chain
    if oracle.update_on_chain_prices(symbols):
        time.sleep(2)  # Wait for blockchain confirmation
        
        # Read back from chain
        if isinstance(symbols, str):
            symbols = [symbols]
        
        result = {}
        for symbol in symbols:
            price_data = oracle.get_on_chain_price(symbol)
            if price_data:
                result[symbol] = price_data
        
        return result
    
    return {}

def test_api_connection():
    """Test Pyth API connectivity and response format"""
    print("🧪 Testing Pyth Network API Connection")
    print("=" * 45)
    
    base_url = "https://hermes.pyth.network"
    btc_feed_id = "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"
    
    try:
        # Test direct API call
        response = requests.get(
            f"{base_url}/api/latest_price_feeds",
            params={"ids[]": btc_feed_id, "verbose": "true", "binary": "false"},
            timeout=10
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Response Time: {response.elapsed.total_seconds():.3f}s")
        print(f"📡 Final URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                price_data = data[0]['price']
                price = float(price_data['price']) * (10 ** price_data['expo'])
                print(f"✅ BTC Price: ${price:,.2f}")
                print(f"✅ API Connection: WORKING")
            else:
                print("❌ Empty response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        
    print("=" * 45)

# Example usage
if __name__ == "__main__":
    print("🚀 Pyth Oracle - Complete Integration Example")
    print("=" * 60)
    
    oracle = PythOracle()
    
    # API Connection Test
    test_api_connection()
    print()
    
    # Step 1: Fetch from Hermes
    print("📡 Step 1: Fetching prices from Hermes...")
    symbols = ["BTC/USD", "ETH/USD", "SOL/USD"]
    prices = oracle.fetch_prices(symbols)
    
    for symbol, data in prices.items():
        print(f"💰 {symbol}: ${data.price:,.2f} (±${data.confidence:.2f}) at {data.timestamp}")
    
    # Step 2 & 3: Update on-chain and read back
    if oracle.w3:  # Only if blockchain is configured
        print("\n⛓️  Step 2: Updating prices on-chain...")
        success = oracle.update_on_chain_prices(["BTC/USD"])
        
        if success:
            print("\n📖 Step 3: Reading price from on-chain contract...")
            on_chain_price = oracle.get_on_chain_price("BTC/USD")
            if on_chain_price:
                print(f"📊 On-chain BTC/USD: ${on_chain_price.price:,.2f}")
            else:
                print("❌ Failed to read on-chain price")
    else:
        print("\n⚠️  Blockchain not configured - skipping on-chain steps")
        print("   To enable: Set RPC_URL, PRIVATE_KEY, PYTH_CONTRACT in .env")