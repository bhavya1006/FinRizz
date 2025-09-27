#!/usr/bin/env python3
"""
Simple Demo - Pyth Oracle Integration

This demonstrates the complete workflow:
1. Fetch prices from Hermes API (off-chain)
2. Update prices on blockchain (on-chain) 
3. Read prices from smart contract (on-chain consumption)
"""

from pyth_oracle import PythOracle, get_prices

def demo_off_chain_only():
    """Demo: Just fetch prices from Hermes (no blockchain needed)"""
    print("🔥 DEMO 1: Off-chain price fetching (Hermes API)")
    print("=" * 55)
    
    # This works without any API keys!
    prices = get_prices(["BTC/USD", "ETH/USD", "SOL/USD"])
    
    for symbol, data in prices.items():
        print(f"💰 {symbol}: ${data.price:,.2f} (confidence: ±${data.confidence:.2f})")
        print(f"   📅 Updated: {data.timestamp}")
        print(f"   🆔 Feed ID: {data.feed_id[:10]}...")
        print()

def demo_full_integration():
    """Demo: Complete integration including on-chain operations"""
    print("⛓️  DEMO 2: Full integration (Hermes + Blockchain)")
    print("=" * 55)
    
    oracle = PythOracle()
    
    if not oracle.w3:
        print("⚠️  Blockchain not configured!")
        print("   To enable on-chain features, set these in .env:")
        print("   - RPC_URL (get from Alchemy/Infura)")
        print("   - PRIVATE_KEY (your wallet private key)")  
        print("   - PYTH_CONTRACT (Pyth contract address)")
        print("\n   For now, showing off-chain data only...")
        
        # Show off-chain prices
        prices = oracle.fetch_prices(["BTC/USD", "ETH/USD"])
        for symbol, data in prices.items():
            print(f"📡 Hermes - {symbol}: ${data.price:,.2f}")
        return
    
    # Full workflow if blockchain is configured
    symbols = ["BTC/USD", "ETH/USD"]
    
    print("📡 Step 1: Fetching from Hermes...")
    hermes_prices = oracle.fetch_prices(symbols)
    for symbol, data in hermes_prices.items():
        print(f"   💰 {symbol}: ${data.price:,.2f}")
    
    print("\n⛓️  Step 2: Updating on-chain...")
    success = oracle.update_on_chain_prices(["BTC/USD"])
    
    if success:
        print("   ✅ On-chain update successful!")
        
        print("\n📖 Step 3: Reading from blockchain...")
        on_chain_data = oracle.get_on_chain_price("BTC/USD")
        
        if on_chain_data:
            print(f"   📊 On-chain BTC/USD: ${on_chain_data.price:,.2f}")
            print(f"   ⏰ On-chain timestamp: {on_chain_data.timestamp}")
        else:
            print("   ❌ Failed to read on-chain price")
    else:
        print("   ❌ On-chain update failed")

def demo_continuous_monitoring():
    """Demo: Continuous price monitoring"""
    print("🔄 DEMO 3: Continuous monitoring")
    print("=" * 35)
    print("Press Ctrl+C to stop...\n")
    
    oracle = PythOracle()
    
    try:
        for i in range(10):  # Show 10 updates
            prices = oracle.fetch_prices(["BTC/USD", "ETH/USD"])
            
            print(f"📊 Update #{i+1} - {prices['BTC/USD'].timestamp.strftime('%H:%M:%S')}")
            for symbol, data in prices.items():
                print(f"   {symbol}: ${data.price:,.2f}")
            
            print("   ---")
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("🛑 Monitoring stopped by user")

if __name__ == "__main__":
    import time
    
    print("🚀 Pyth Oracle - Integration Demos")
    print("=" * 40)
    print()
    
    # Demo 1: Basic off-chain fetching
    demo_off_chain_only()
    print("\n" + "="*60 + "\n")
    
    # Demo 2: Full integration  
    demo_full_integration()
    print("\n" + "="*60 + "\n")
    
    # Demo 3: Continuous monitoring (uncomment to enable)
    # demo_continuous_monitoring()
    
    print("✨ Done! Check pyth_oracle.py for the full implementation.")