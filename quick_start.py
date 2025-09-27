#!/usr/bin/env python3
"""
Quick Start Script for Pyth Network Price Fetching

This script provides the fastest way to start fetching prices from Pyth Network.
Run this after installing the requirements.
"""

import sys
import subprocess
import os

def check_and_install_requirements():
    """Check if requirements are installed and install if needed"""
    try:
        import requests
        print("✅ Core dependencies already installed")
        return True
    except ImportError:
        print("📦 Installing core dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            print("✅ Core dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def main():
    """Main quick start function"""
    print("🚀 Pyth Network Price Fetcher - Quick Start")
    print("=" * 50)
    
    # Check dependencies
    if not check_and_install_requirements():
        print("Please install requirements manually: pip install requests")
        return
    
    # Import after ensuring dependencies
    from simple_price_fetcher import SimplePythPriceFetcher
    
    # Initialize fetcher
    fetcher = SimplePythPriceFetcher()
    
    print("\n📊 Fetching current prices...")
    
    # Get sample prices
    symbols = ["BTC/USD", "ETH/USD", "SOL/USD"]
    
    for symbol in symbols:
        print(f"\n🔍 Fetching {symbol}...")
        price_data = fetcher.get_price(symbol)
        
        if price_data:
            print(f"✅ {symbol}: ${price_data['price']:,.4f}")
            print(f"   Confidence: ±${price_data['confidence']:,.4f}")
            print(f"   Updated: {price_data['timestamp']}")
        else:
            print(f"❌ Failed to fetch {symbol}")
    
    print(f"\n📋 Available symbols: {', '.join(fetcher.available_symbols())}")
    
    print("""
🎉 Quick start completed successfully!

Next steps:
1. Check examples.py for more detailed usage
2. Run: python examples.py
3. For advanced features: python advanced_examples.py

Need help? Check the README.md file.
""")

if __name__ == "__main__":
    main()