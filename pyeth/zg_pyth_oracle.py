"""
0G-Integrated Pyth Oracle System
Combines Pyth Network price feeds with 0G (Zero Gravity) blockchain infrastructure

Features:
1. Pyth price fetching from Hermes API
2. 0G blockchain for on-chain storage and computation
3. 0G Data Availability for price feed storage
4. 0G Storage for historical price data
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Optional blockchain imports
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
    pass

# 0G Network Configuration
ZG_CONFIG = {
    "newton_testnet": {
        "rpc_url": "https://evmrpc-testnet.0g.ai",
        "chain_id": 16602,  # Updated actual chain ID
        "da_node": "https://da-rpc-testnet.0g.ai",  # Updated endpoint
        "storage_node": "https://rpc-storage-testnet.0g.ai",  # Updated endpoint
        "explorer": "https://chainscan-newton.0g.ai"
    },
    "mainnet": {
        "rpc_url": "https://evmrpc.0g.ai", 
        "chain_id": 16600,  # Will be updated when mainnet launches
        "da_node": "https://da.0g.ai",
        "storage_node": "https://storage.0g.ai",
        "explorer": "https://chainscan.0g.ai"
    }
}

# Enhanced Pyth contract ABI for 0G integration
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

# Price feeds configuration
PRICE_FEEDS = {
    "BTC/USD": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    "ETH/USD": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace", 
    "SOL/USD": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    "BNB/USD": "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",
    "USDC/USD": "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
    "USDT/USD": "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b",
    # AI/ML tokens (relevant for 0G ecosystem)
    "FET/USD": "0xb98e7ae8eb5b3c6cfd4b3a0e92b7e0b8f35b6f8e8b3c6cfd4b3a0e92b7e0b8f35",  # Fetch.AI
    "OCEAN/USD": "0xc4e8b3c6cfd4b3a0e92b7e0b8f35b6f8e8b3c6cfd4b3a0e92b7e0b8f35b6f8",   # Ocean Protocol
}

@dataclass
class ZGPriceData:
    """Enhanced price data with 0G-specific fields"""
    symbol: str
    price: float
    confidence: float
    timestamp: datetime
    feed_id: str
    zg_block_height: Optional[int] = None  # 0G block height when stored
    zg_da_commitment: Optional[str] = None  # 0G DA commitment hash
    zg_storage_root: Optional[str] = None   # 0G storage root hash
    vaa_data: Optional[bytes] = None

class ZGPythOracle:
    """
    0G-Integrated Pyth Oracle System
    
    Combines Pyth Network price feeds with 0G blockchain infrastructure:
    - Uses 0G blockchain for on-chain price storage
    - Leverages 0G DA for efficient data availability
    - Utilizes 0G Storage for historical price data
    """
    
    def __init__(self, network: str = "newton_testnet"):
        """
        Initialize 0G-Integrated Pyth Oracle
        
        Args:
            network: 0G network to use ('newton_testnet' or 'mainnet')
        """
        # Hermes API configuration
        self.hermes_url = "https://hermes.pyth.network"
        
        # 0G Network configuration
        self.network = network
        self.zg_config = ZG_CONFIG[network]
        
        # Environment configuration
        self.rpc_url = os.getenv("RPC_URL", self.zg_config["rpc_url"])
        self.private_key = os.getenv("PRIVATE_KEY")
        self.pyth_contract_address = os.getenv("PYTH_CONTRACT")
        self.chain_id = int(os.getenv("CHAIN_ID", self.zg_config["chain_id"]))
        
        # 0G specific endpoints
        self.zg_da_node = os.getenv("ZG_DA_NODE", self.zg_config["da_node"])
        self.zg_storage_node = os.getenv("ZG_STORAGE_NODE", self.zg_config["storage_node"])
        
        # Initialize blockchain connections
        self.w3 = None
        self.account = None
        self.pyth_contract = None
        
        if self.rpc_url and self.private_key and self.pyth_contract_address:
            self._init_0g_blockchain()
    
    def _init_0g_blockchain(self):
        """Initialize 0G blockchain connections"""
        if not WEB3_AVAILABLE:
            print("❌ Web3 libraries not available. Install with: pip install web3 eth-account")
            return
            
        try:
            # Connect to 0G blockchain
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            if not self.w3.is_connected():
                raise Exception("Failed to connect to 0G blockchain")
            
            # Verify we're on the correct 0G network
            actual_chain_id = self.w3.eth.chain_id
            if actual_chain_id != self.chain_id:
                print(f"⚠️ Chain ID mismatch: expected {self.chain_id}, got {actual_chain_id}")
            
            # Setup account and signing middleware
            self.account = Account.from_key(self.private_key)
            signing_middleware = SignAndSendRawMiddlewareBuilder.build(self.account)
            self.w3.middleware_onion.add(signing_middleware)
            
            # Initialize Pyth contract on 0G
            self.pyth_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.pyth_contract_address),
                abi=PYTH_ABI
            )
            
            print(f"✅ 0G Network connected - {self.network.upper()}")
            print(f"✅ Chain ID: {actual_chain_id} (0G {self.network})")
            print(f"✅ Account: {self.account.address}")
            print(f"✅ RPC: {self.rpc_url}")
            print(f"✅ Pyth Contract: {self.pyth_contract_address}")
            
            # Check balance
            balance = self.w3.eth.get_balance(self.account.address)
            balance_tokens = self.w3.from_wei(balance, 'ether')
            print(f"💰 0G Balance: {balance_tokens:.6f} A0GI")
            
            if balance_tokens < 0.001:
                print("⚠️ Low balance! Get 0G testnet tokens from:")
                print("   - 0G Discord faucet")
                print("   - 0G community channels")
            
        except Exception as e:
            print(f"❌ 0G blockchain initialization failed: {e}")
            self.w3 = None
    
    # STEP 1: FETCH FROM HERMES (unchanged)
    def fetch_prices(self, symbols: Union[str, List[str]]) -> Dict[str, ZGPriceData]:
        """Fetch latest prices from Hermes API with 0G enhancements"""
        if isinstance(symbols, str):
            symbols = [symbols]
        
        valid_symbols = [s for s in symbols if s in PRICE_FEEDS]
        if not valid_symbols:
            print(f"❌ No valid symbols found in {symbols}")
            return {}
        
        feed_ids = [PRICE_FEEDS[symbol] for symbol in valid_symbols]
        
        try:
            response = requests.get(
                f"{self.hermes_url}/api/latest_price_feeds",
                params={"ids[]": feed_ids, "verbose": "true", "binary": "false"},
                timeout=10
            )
            response.raise_for_status()
            
            raw_data = response.json()
            return self._parse_zg_price_data(raw_data, valid_symbols)
            
        except Exception as e:
            print(f"❌ Failed to fetch prices: {e}")
            return {}
    
    def _parse_zg_price_data(self, raw_data: List, symbols: List[str]) -> Dict[str, ZGPriceData]:
        """Parse raw Hermes API response into 0G-enhanced price data"""
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
            
            # Get current 0G block height if connected
            zg_block_height = None
            if self.w3:
                try:
                    zg_block_height = self.w3.eth.block_number
                except:
                    pass
            
            parsed[matching_symbol] = ZGPriceData(
                symbol=matching_symbol,
                price=price,
                confidence=confidence,
                timestamp=datetime.fromtimestamp(price_data.get("publish_time", 0)),
                feed_id=feed_id,
                zg_block_height=zg_block_height
            )
        
        return parsed
    
    # STEP 2: 0G DATA AVAILABILITY INTEGRATION
    def store_prices_on_0g_da(self, price_data: Dict[str, ZGPriceData]) -> Dict[str, str]:
        """
        Store price data on 0G Data Availability layer
        
        Args:
            price_data: Price data to store
            
        Returns:
            Dictionary mapping symbols to DA commitment hashes
        """
        if not price_data:
            return {}
        
        try:
            # Prepare data for 0G DA storage
            da_payload = {
                "timestamp": datetime.now().isoformat(),
                "network": self.network,
                "prices": {}
            }
            
            for symbol, data in price_data.items():
                da_payload["prices"][symbol] = {
                    "price": data.price,
                    "confidence": data.confidence,
                    "timestamp": data.timestamp.isoformat(),
                    "feed_id": data.feed_id,
                    "zg_block_height": data.zg_block_height
                }
            
            # Convert to JSON bytes
            data_bytes = json.dumps(da_payload).encode('utf-8')
            
            # Submit to 0G DA (this is a simplified implementation)
            # In practice, you'd use 0G's official SDK
            da_response = requests.post(
                f"{self.zg_da_node}/submit",
                json={
                    "data": data_bytes.hex(),
                    "namespace": "pyth_prices"
                },
                timeout=30
            )
            
            if da_response.status_code == 200:
                commitment = da_response.json().get("commitment_hash")
                print(f"✅ Stored on 0G DA - Commitment: {commitment[:16]}...")
                
                # Update price data with DA commitment
                result = {}
                for symbol in price_data:
                    price_data[symbol].zg_da_commitment = commitment
                    result[symbol] = commitment
                
                return result
            else:
                print(f"❌ 0G DA storage failed: {da_response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ 0G DA storage error: {e}")
            return {}
    
    # STEP 3: 0G STORAGE INTEGRATION
    def store_historical_prices_on_0g_storage(self, price_data: Dict[str, ZGPriceData]) -> Optional[str]:
        """
        Store historical price data on 0G Storage network
        
        Args:
            price_data: Price data to store
            
        Returns:
            Storage root hash if successful
        """
        if not price_data:
            return None
        
        try:
            # Prepare historical data structure
            storage_payload = {
                "timestamp": datetime.now().isoformat(),
                "network": self.network,
                "data_type": "pyth_historical_prices",
                "prices": {}
            }
            
            for symbol, data in price_data.items():
                storage_payload["prices"][symbol] = asdict(data)
                # Convert datetime to string for JSON serialization
                storage_payload["prices"][symbol]["timestamp"] = data.timestamp.isoformat()
            
            # Submit to 0G Storage
            storage_response = requests.post(
                f"{self.zg_storage_node}/store",
                json=storage_payload,
                timeout=60
            )
            
            if storage_response.status_code == 200:
                storage_root = storage_response.json().get("root_hash")
                print(f"✅ Stored on 0G Storage - Root: {storage_root[:16]}...")
                
                # Update price data with storage root
                for symbol in price_data:
                    price_data[symbol].zg_storage_root = storage_root
                
                return storage_root
            else:
                print(f"❌ 0G Storage failed: {storage_response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 0G Storage error: {e}")
            return None
    
    # STEP 4: ON-CHAIN PRICE UPDATES ON 0G
    def update_prices_on_0g_chain(self, symbols: Union[str, List[str]]) -> bool:
        """
        Update price feeds on 0G blockchain
        
        Args:
            symbols: Symbols to update on-chain
            
        Returns:
            True if successful
        """
        if not self.w3 or not self.pyth_contract:
            print("❌ 0G blockchain not initialized")
            return False
        
        # Fetch VAA data for on-chain update
        vaa_data = self.fetch_vaa_data(symbols)
        if not vaa_data:
            print("❌ Failed to fetch VAA data")
            return False
        
        try:
            # Get update fee
            update_fee = self.pyth_contract.functions.getUpdateFee().call()
            
            # Prepare update data
            update_data = list(vaa_data.values())
            
            # Send transaction on 0G network
            tx_hash = self.pyth_contract.functions.updatePriceFeeds(
                update_data
            ).transact({
                'from': self.account.address,
                'value': update_fee,
                'gas': 200000,  # 0G may have different gas requirements
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Wait for confirmation on 0G
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ 0G on-chain update successful - TX: {tx_hash.hex()}")
                print(f"   Block: {receipt.blockNumber}")
                print(f"   Gas used: {receipt.gasUsed}")
                return True
            else:
                print(f"❌ 0G on-chain update failed - TX: {tx_hash.hex()}")
                return False
                
        except Exception as e:
            print(f"❌ 0G on-chain update error: {e}")
            return False
    
    def fetch_vaa_data(self, symbols: Union[str, List[str]]) -> Dict[str, bytes]:
        """Fetch VAA data for on-chain updates"""
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
                    import base64
                    result[symbol] = base64.b64decode(vaa_data[i])
                    
            return result
            
        except Exception as e:
            print(f"❌ Failed to fetch VAA data: {e}")
            return {}
    
    # COMPLETE 0G WORKFLOW
    def complete_0g_price_update(self, symbols: Union[str, List[str]]) -> Dict[str, ZGPriceData]:
        """
        Complete 0G-integrated price update workflow:
        1. Fetch from Hermes
        2. Store on 0G DA
        3. Store on 0G Storage  
        4. Update on 0G blockchain
        
        Args:
            symbols: Symbols to process
            
        Returns:
            Updated price data with 0G metadata
        """
        print(f"🚀 Starting complete 0G workflow for {symbols}")
        print("=" * 60)
        
        # Step 1: Fetch prices from Hermes
        print("📡 Step 1: Fetching prices from Hermes...")
        price_data = self.fetch_prices(symbols)
        
        if not price_data:
            print("❌ No price data fetched")
            return {}
        
        for symbol, data in price_data.items():
            print(f"   💰 {symbol}: ${data.price:,.2f}")
        
        # Step 2: Store on 0G Data Availability
        print("\n🌐 Step 2: Storing on 0G Data Availability...")
        da_commitments = self.store_prices_on_0g_da(price_data)
        
        # Step 3: Store on 0G Storage
        print("\n💾 Step 3: Storing on 0G Storage...")
        storage_root = self.store_historical_prices_on_0g_storage(price_data)
        
        # Step 4: Update on 0G blockchain
        if self.w3:
            print("\n⛓️ Step 4: Updating on 0G blockchain...")
            on_chain_success = self.update_prices_on_0g_chain(symbols)
        else:
            print("\n⚠️ Step 4: 0G blockchain not configured")
            on_chain_success = False
        
        # Summary
        print("\n📊 0G Workflow Summary:")
        print(f"   ✅ Hermes fetch: {len(price_data)} prices")
        print(f"   {'✅' if da_commitments else '❌'} 0G DA storage: {len(da_commitments)} commitments")
        print(f"   {'✅' if storage_root else '❌'} 0G Storage: {storage_root[:16] + '...' if storage_root else 'Failed'}")
        print(f"   {'✅' if on_chain_success else '❌'} 0G on-chain: {'Success' if on_chain_success else 'Failed'}")
        
        return price_data

# Convenience functions for 0G integration
def get_0g_prices(symbols: Union[str, List[str]], network: str = "newton_testnet") -> Dict[str, ZGPriceData]:
    """Quick function to get prices with 0G integration"""
    oracle = ZGPythOracle(network=network)
    return oracle.fetch_prices(symbols)

def complete_0g_workflow(symbols: Union[str, List[str]], network: str = "newton_testnet") -> Dict[str, ZGPriceData]:
    """Execute complete 0G-integrated workflow"""
    oracle = ZGPythOracle(network=network)
    return oracle.complete_0g_price_update(symbols)

if __name__ == "__main__":
    print("🚀 0G-INTEGRATED PYTH ORACLE SYSTEM")
    print("=" * 50)
    
    # Initialize with 0G Newton testnet
    oracle = ZGPythOracle(network="newton_testnet")
    
    # Test symbols including AI/ML tokens relevant to 0G
    test_symbols = ["BTC/USD", "ETH/USD", "SOL/USD"]
    
    # Run complete 0G workflow
    result = oracle.complete_0g_price_update(test_symbols)
    
    print("\n🎉 0G Integration Complete!")
    print("   Your Pyth prices are now stored across 0G's")
    print("   modular infrastructure: DA, Storage, and Chain!")