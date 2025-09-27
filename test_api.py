#!/usr/bin/env python3
"""
Test script to debug Pyth API calls
"""

import requests
import json

def test_pyth_api():
    """Test the Pyth API directly"""
    print("🧪 Testing Pyth Network API...")
    
    # Test URL and parameters
    base_url = "https://hermes.pyth.network"
    btc_feed_id = "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"
    
    # Test 1: Direct URL construction
    print("\n📡 Test 1: Direct URL with query parameters")
    url1 = f"{base_url}/api/latest_price_feeds?ids[]={btc_feed_id}&verbose=true&binary=false"
    print(f"URL: {url1}")
    
    try:
        response = requests.get(url1, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response length: {len(data)}")
            if data:
                price_data = data[0]['price']
                price = float(price_data['price']) * (10 ** price_data['expo'])
                print(f"✅ BTC Price: ${price:,.2f}")
            else:
                print("❌ Empty response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Using requests params
    print("\n📡 Test 2: Using requests params")
    try:
        response = requests.get(
            f"{base_url}/api/latest_price_feeds",
            params={"ids[]": btc_feed_id, "verbose": "true", "binary": "false"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response length: {len(data)}")
            if data:
                price_data = data[0]['price']
                price = float(price_data['price']) * (10 ** price_data['expo'])
                print(f"✅ BTC Price: ${price:,.2f}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Multiple feeds
    print("\n📡 Test 3: Multiple feeds")
    eth_feed_id = "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"
    
    try:
        params = [
            ("ids[]", btc_feed_id),
            ("ids[]", eth_feed_id),
            ("verbose", "true"),
            ("binary", "false")
        ]
        
        response = requests.get(
            f"{base_url}/api/latest_price_feeds",
            params=params,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response length: {len(data)}")
            
            symbols = {"0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43": "BTC/USD",
                      "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace": "ETH/USD"}
            
            for item in data:
                feed_id = item['id']
                if feed_id in symbols:
                    symbol = symbols[feed_id]
                    price_data = item['price']
                    price = float(price_data['price']) * (10 ** price_data['expo'])
                    print(f"✅ {symbol}: ${price:,.2f}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_pyth_api()