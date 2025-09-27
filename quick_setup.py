#!/usr/bin/env python3
"""
Quick Setup Helper - Get Sepolia ETH and Test Basic Functions
"""

from pyth_oracle import PythOracle, get_prices

def check_wallet_status():
    """Check wallet and provide instructions"""
    print("🔍 WALLET STATUS CHECK")
    print("=" * 30)
    
    oracle = PythOracle()
    
    if not oracle.w3:
        print("❌ Blockchain not connected")
        return
    
    address = oracle.account.address
    balance = oracle.w3.eth.get_balance(address)
    balance_eth = oracle.w3.from_wei(balance, 'ether')
    
    print(f"📍 Wallet Address: {address}")
    print(f"💰 Current Balance: {balance_eth:.6f} SepoliaETH")
    
    if balance_eth < 0.001:
        print("\n🚨 ACTION NEEDED: Get Sepolia ETH")
        print("=" * 40)
        print("1. Copy your wallet address above")
        print("2. Go to ONE of these faucets:")
        print("   • https://sepoliafaucet.com/")
        print("   • https://faucet.sepolia.dev/") 
        print("   • https://sepolia-faucet.pk910.de/")
        print("3. Paste your address and request 0.1 ETH")
        print("4. Wait 30-60 seconds for confirmation")
        print("5. Run this script again to verify")
        return False
    else:
        print("✅ Sufficient balance for testing!")
        return True

def test_hermes_only():
    """Test just the Hermes API (no blockchain needed)"""
    print("\n🚀 TESTING HERMES API (No Gas Required)")
    print("=" * 50)
    
    try:
        prices = get_prices(['BTC/USD', 'ETH/USD', 'SOL/USD'])
        
        print("✅ LIVE PRICES FROM HERMES:")
        for symbol, data in prices.items():
            print(f"   💰 {symbol}: ${data.price:,.2f}")
            
        print("\n🎉 Hermes API working perfectly!")
        print("   This part needs NO gas fees or setup!")
        
        return True
        
    except Exception as e:
        print(f"❌ Hermes Error: {e}")
        return False

def main():
    print("🚀 PYTH ORACLE SETUP HELPER")
    print("=" * 35)
    
    # Test 1: Basic API (always works)
    hermes_ok = test_hermes_only()
    
    # Test 2: Wallet status
    wallet_ok = check_wallet_status()
    
    print("\n📊 SUMMARY")
    print("=" * 15)
    
    if hermes_ok:
        print("✅ Hermes API: WORKING (Step 1 complete)")
    else:
        print("❌ Hermes API: FAILED")
    
    if wallet_ok:
        print("✅ Wallet: FUNDED (Ready for on-chain operations)")
        print("\n🎯 NEXT STEP: Run full demo")
        print("   python demo.py")
    else:
        print("⏳ Wallet: NEEDS FUNDING (Get Sepolia ETH first)")
        print("\n🎯 NEXT STEP: Fund wallet then run")
        print("   python quick_setup.py")

if __name__ == "__main__":
    main()