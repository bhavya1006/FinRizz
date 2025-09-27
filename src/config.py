"""
Pyth Network Price Feed IDs Configuration

This file contains the feed IDs for various cryptocurrencies and assets
supported by Pyth Network. You can find more feed IDs at:
https://pyth.network/developers/price-feed-ids
"""

# Popular Cryptocurrency Price Feeds
PRICE_FEEDS = {
    # Major Cryptocurrencies
    "BTC/USD": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    "ETH/USD": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    "SOL/USD": "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    "BNB/USD": "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",
    "ADA/USD": "0x2a01deaec9e51a579277b34b122399984d0bbf57e2458a7e42fecd2829867a0d",
    "AVAX/USD": "0x93da3352f9f1d105fdfe4971cfa80e9dd777bfc5d0f683ebb6e1294b92137bb7",
    "MATIC/USD": "0x5de33a9112c2b700b8d30b8a3402c103578ccfa2765696471cc672bd5cf6ac52",
    "DOT/USD": "0xca3eed9b267293f6595901c734c7525ce8ef49adafe8284606ceb307afa2ca5b",
    
    # DeFi Tokens
    "UNI/USD": "0x78d185a741d07edb3412b09008b7c5cfb9bbbd7d568bf00ba737b456ba171501",
    "LINK/USD": "0x8ac0c70fff57e9aefdf5edf44b51d62c2d433653cbb2cf5cc06bb115af04d221",
    "AAVE/USD": "0x2b9ab1e972a281585084148ba1389800799bd4be63b957507db82dc7c9c0e702",
    "CRV/USD": "0xa19d04ac696c7a6616d291c7e5d1377cc8be437c327b75adb5dc1bad745fcae8",
    
    # Stablecoins
    "USDC/USD": "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
    "USDT/USD": "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b",
    "DAI/USD": "0xb0948a5e5313200c632b51bb5ca32f6de0d36e9950a942d19751e833f70dabfd",
    
    # Traditional Assets (if available)
    "GOLD/USD": "0x765d2ba906dbc32ca17cc11f5310a89e9ee1f6420508c63861f2f8ba4ee34bb2",
    "EUR/USD": "0xa995d00bb36a63cef7fd2c287dc105fc8f3d93779f062f09551b0af3e81ec30b",
    "GBP/USD": "0x84c2dde9633d93d1bcad84e7dc41c9d56578b7ec52fabedc1f335d673df0a7c1",
    
    # Add more as needed...
}

# Pyth Network API Configuration
PYTH_CONFIG = {
    "base_url": "https://hermes.pyth.network",
    "endpoints": {
        "latest_price_feeds": "/api/latest_price_feeds",
        "price_feed_ids": "/api/price_feed_ids",
        "latest_vaas": "/api/latest_vaas",
        "get_vaa": "/api/get_vaa",
        "get_vaa_ccip": "/api/get_vaa_ccip",
    }
}

# Request configuration
REQUEST_CONFIG = {
    "timeout": 10,  # seconds
    "max_retries": 3,
    "retry_delay": 1,  # seconds
    "batch_size": 20,  # max feed IDs per request
}