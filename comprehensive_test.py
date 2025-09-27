#!/usr/bin/env python3
"""
Comprehensive Test Suite for Pyth Oracle Integration

This script helps debug and test all components systematically.
"""

from pyth_oracle import PythOracle, get_prices, test_api_connection
import requests
import time

def test_1_hermes_api():
    """Test 1: Hermes API connectivity"""
    print("🧪 TEST 1: Hermes API Connection")
    print("=" * 40)
    
    try:
        test_api_connection()
        print("✅ Hermes API: WORKING")
        return True
    except Exception as e:
        print(f"❌ Hermes API Error: {e}")
        return False

def test_2_price_fetching():
    """Test 2: Price data fetching"""
    print("\n🧪 TEST 2: Price Data Fetching")
    print("=" * 40)
    
    try:
        prices = get_prices(['BTC/USD', 'ETH/USD'])
        for symbol, data in prices.items():
            print(f"✅ {symbol}: ${data.price:,.2f} (±${data.confidence:.2f})")
        print("✅ Price Fetching: WORKING")
        return True
    except Exception as e:
        print(f"❌ Price Fetching Error: {e}")
        return False

def test_3_blockchain_connection():
    """Test 3: Blockchain connectivity"""
    print("\n🧪 TEST 3: Blockchain Connection")
    print("=" * 40)
    
    oracle = PythOracle()
    
    if not oracle.w3:
        print("❌ Web3 not initialized")
        return False
    
    try:
        # Test connection
        is_connected = oracle.w3.is_connected()
        print(f"✅ ThirdWeb RPC Connected: {is_connected}")
        
        # Check network
        chain_id = oracle.w3.eth.chain_id
        print(f"✅ Chain ID: {chain_id} (Expected: 11155111 for Sepolia)")
        
        # Check account
        account = oracle.account.address if oracle.account else "Not set"
        print(f"✅ Account: {account}")
        
        # Check balance
        balance = oracle.w3.eth.get_balance(oracle.account.address)
        balance_eth = oracle.w3.from_wei(balance, 'ether')
        print(f"💰 Balance: {balance_eth:.6f} SepoliaETH")
        
        if balance_eth < 0.001:
            print("⚠️  ISSUE: Insufficient balance for gas fees!")
            print("   Get free Sepolia ETH from:")
            print("   • https://sepoliafaucet.com/")
            print("   • https://faucet.sepolia.dev/")
            print("   • https://sepolia-faucet.pk910.de/")
            return False
        else:
            print("✅ Sufficient balance for testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Blockchain Error: {e}")
        return False

def test_4_contract_interaction():
    """Test 4: Smart contract interaction"""
    print("\n🧪 TEST 4: Contract Interaction")
    print("=" * 40)
    
    oracle = PythOracle()
    
    if not oracle.w3 or not oracle.pyth_contract:
        print("❌ Contract not initialized")
        return False
    
    try:
        # Test contract functions
        print("Testing contract read functions...")
        
        # Try to get update fee
        try:
            update_fee = oracle.pyth_contract.functions.getUpdateFee().call()
            print(f"✅ Update Fee: {oracle.w3.from_wei(update_fee, 'ether'):.6f} ETH")
        except Exception as e:
            print(f"⚠️  Update Fee Error: {e}")
        
        # Test reading a price (this should work even without updates)
        btc_feed_id = "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"
        feed_id_bytes = bytes.fromhex(btc_feed_id[2:])
        
        try:
            price_data = oracle.pyth_contract.functions.getPriceUnsafe(feed_id_bytes).call()
            print(f"✅ Contract Price Read: Success (data: {price_data[:2]}...)")
        except Exception as e:
            print(f"⚠️  Price Read Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Contract Interaction Error: {e}")
        return False

def test_5_vaa_data():
    """Test 5: VAA (Verifiable Action Approval) data fetching"""
    print("\n🧪 TEST 5: VAA Data Fetching")
    print("=" * 40)
    
    try:
        oracle = PythOracle()
        
        # Test VAA data fetch
        vaa_data = oracle.fetch_vaa_data(['BTC/USD'])
        
        if vaa_data:
            btc_vaa = vaa_data.get('BTC/USD')
            if btc_vaa:
                print(f"✅ VAA Data Length: {len(btc_vaa)} bytes")
                print(f"✅ VAA Preview: {btc_vaa[:20].hex()}...")
                return True
            else:
                print("❌ No VAA data for BTC/USD")
        else:
            print("❌ No VAA data received")
            
        return False
        
    except Exception as e:
        print(f"❌ VAA Data Error: {e}")
        return False

def test_6_gas_estimation():
    """Test 6: Gas estimation for transactions"""
    print("\n🧪 TEST 6: Gas Estimation")
    print("=" * 40)
    
    oracle = PythOracle()
    
    if not oracle.w3:
        print("❌ Web3 not available")
        return False
    
    try:
        # Get current gas price
        gas_price = oracle.w3.eth.gas_price
        gas_price_gwei = oracle.w3.from_wei(gas_price, 'gwei')
        print(f"✅ Current Gas Price: {gas_price_gwei:.2f} Gwei")
        
        # Estimate gas for a simple transaction
        balance = oracle.w3.eth.get_balance(oracle.account.address)
        print(f"✅ Account Balance: {oracle.w3.from_wei(balance, 'ether'):.6f} ETH")
        
        # Calculate cost for typical Pyth update
        estimated_gas = 150000  # Typical gas for updatePriceFeeds
        tx_cost = gas_price * estimated_gas
        tx_cost_eth = oracle.w3.from_wei(tx_cost, 'ether')
        print(f"✅ Estimated TX Cost: {tx_cost_eth:.6f} ETH")
        
        if balance < tx_cost:
            print(f"⚠️  Insufficient balance! Need at least {tx_cost_eth:.6f} ETH")
            return False
        else:
            print("✅ Sufficient balance for transaction")
            
        return True
        
    except Exception as e:
        print(f"❌ Gas Estimation Error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 COMPREHENSIVE PYTH ORACLE TEST SUITE")
    print("=" * 50)
    print()
    
    tests = [
        ("Hermes API", test_1_hermes_api),
        ("Price Fetching", test_2_price_fetching), 
        ("Blockchain Connection", test_3_blockchain_connection),
        ("Contract Interaction", test_4_contract_interaction),
        ("VAA Data", test_5_vaa_data),
        ("Gas Estimation", test_6_gas_estimation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your system is ready.")
    else:
        print("\n🔧 NEXT STEPS TO FIX ISSUES:")
        if not results[2][1]:  # Blockchain connection failed
            print("1. Get Sepolia ETH from faucets listed above")
        if not results[4][1]:  # VAA data failed
            print("2. VAA data issue - this affects on-chain updates")
        if not results[5][1]:  # Gas estimation failed  
            print("3. Gas/balance issues - get more Sepolia ETH")
        
        print("\nOnce fixed, run: python comprehensive_test.py")

if __name__ == "__main__":
    run_comprehensive_test()