"""
Pyth Network Price Service Example Usage

This script demonstrates how to use the PythPriceService to fetch real-time
cryptocurrency prices from the Pyth Network.
"""

import asyncio
import time
from src.pyth_service import PythPriceService, get_available_symbols, print_price_info


def main():
    """Main example function"""
    print("🚀 Pyth Network Price Fetcher")
    print("=" * 50)
    
    # Initialize the service
    with PythPriceService() as price_service:
        
        # Example 1: Get single price
        print("\n📊 Example 1: Single Price Fetch")
        btc_price = price_service.get_latest_price("BTC/USD")
        if btc_price:
            print_price_info("BTC/USD", btc_price)
        else:
            print("❌ Failed to fetch BTC price")
        
        # Example 2: Get multiple prices
        print("\n📈 Example 2: Multiple Price Fetch")
        symbols = ["BTC/USD", "ETH/USD", "SOL/USD", "BNB/USD"]
        prices = price_service.get_multiple_prices(symbols)
        
        for symbol, data in prices.items():
            if data:
                print(f"💰 {symbol}: ${data['price']:.4f} (±${data['confidence_interval']:.4f})")
            else:
                print(f"❌ {symbol}: No data")
        
        # Example 3: Show available symbols
        print("\n📋 Example 3: Available Symbols")
        available = get_available_symbols()
        print(f"Total available symbols: {len(available)}")
        print("First 10 symbols:", ", ".join(available[:10]))
        
        # Example 4: Price streaming (uncomment to test)
        # print("\n🔄 Example 4: Price Streaming (5 updates)")
        # stream_symbols = ["BTC/USD", "ETH/USD"]
        # counter = 0
        # 
        # def stream_callback(prices):
        #     global counter
        #     counter += 1
        #     print(f"\n--- Stream Update #{counter} ---")
        #     for symbol, data in prices.items():
        #         if data:
        #             print(f"{symbol}: ${data['price']:.4f}")
        #     
        #     if counter >= 5:
        #         raise KeyboardInterrupt("Demo complete")
        # 
        # try:
        #     price_service.stream_prices(stream_symbols, interval=2.0, callback=stream_callback)
        # except KeyboardInterrupt:
        #     print("✅ Streaming demo completed")


async def async_example():
    """Async example function"""
    print("\n⚡ Async Example")
    print("=" * 30)
    
    price_service = PythPriceService()
    
    # Async single price
    btc_data = await price_service.get_latest_price_async("BTC/USD")
    if btc_data:
        print(f"🔄 Async BTC/USD: ${btc_data['price']:.4f}")
    
    # Async multiple prices
    symbols = ["ETH/USD", "SOL/USD", "ADA/USD", "DOT/USD"]
    start_time = time.time()
    prices = await price_service.get_multiple_prices_async(symbols)
    end_time = time.time()
    
    print(f"⏱️  Fetched {len(prices)} prices in {end_time - start_time:.2f} seconds")
    for symbol, data in prices.items():
        if data:
            print(f"   {symbol}: ${data['price']:.4f}")


def demo_error_handling():
    """Demonstrate error handling"""
    print("\n🛡️  Error Handling Demo")
    print("=" * 30)
    
    with PythPriceService() as price_service:
        # Try to get price for non-existent symbol
        invalid_price = price_service.get_latest_price("INVALID/USD")
        if invalid_price is None:
            print("✅ Correctly handled invalid symbol")
        
        # Try multiple with some invalid symbols
        mixed_symbols = ["BTC/USD", "INVALID/USD", "ETH/USD", "FAKE/USD"]
        prices = price_service.get_multiple_prices(mixed_symbols)
        print(f"📊 Got {len(prices)} valid prices from {len(mixed_symbols)} requested symbols")


def price_comparison_demo():
    """Demo showing price comparison between multiple assets"""
    print("\n💱 Price Comparison Demo")
    print("=" * 30)
    
    with PythPriceService() as price_service:
        # Compare major cryptocurrencies
        major_cryptos = ["BTC/USD", "ETH/USD", "SOL/USD", "ADA/USD"]
        prices = price_service.get_multiple_prices(major_cryptos)
        
        print("Major Cryptocurrency Prices:")
        print("-" * 40)
        
        sorted_prices = sorted(prices.items(), key=lambda x: x[1]['price'] if x[1] else 0, reverse=True)
        
        for i, (symbol, data) in enumerate(sorted_prices, 1):
            if data:
                price = data['price']
                confidence = data['confidence_interval']
                confidence_pct = (confidence / price) * 100 if price > 0 else 0
                
                print(f"{i}. {symbol:<10} ${price:>12,.4f} (±{confidence_pct:.2f}%)")
            else:
                print(f"{i}. {symbol:<10} {'No data':>12}")


if __name__ == "__main__":
    try:
        # Run synchronous examples
        main()
        demo_error_handling()
        price_comparison_demo()
        
        # Run async example
        print("\n" + "=" * 50)
        asyncio.run(async_example())
        
        print("\n🎉 All examples completed successfully!")
        print("\nTo run price streaming, uncomment the streaming section in main()")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()