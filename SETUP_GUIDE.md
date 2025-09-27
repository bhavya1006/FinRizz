# 🚀 Complete Setup Guide for Pyth Network Price Fetcher

## What You Now Have

A complete, working real-time cryptocurrency price fetcher using Pyth Network's REST API with:

- ✅ **Real-time prices** for 20+ cryptocurrencies
- ✅ **Simple & Advanced APIs** 
- ✅ **Web server** with REST endpoints
- ✅ **Portfolio tracking**
- ✅ **Price alerts**
- ✅ **Error handling & retries**

## 📦 Installation Instructions

### Option 1: Quick Start (Minimal - RECOMMENDED)
```bash
# 1. Ensure you have Python 3.7+ installed
python --version

# 2. Install only the core dependency
pip install requests

# 3. Run the quick start
python quick_start.py
```

### Option 2: Full Installation (All Features)
```bash
# Install all dependencies
pip install -r requirements.txt

# Run comprehensive examples
python examples.py
```

### Option 3: Web API Server
```bash
# Install web dependencies
pip install requests flask flask-cors

# Start the web server
python web_api.py

# Test the API
curl http://localhost:5000/price/BTC/USD
```

## 🎯 What Each File Does

| File | Purpose | When to Use |
|------|---------|-------------|
| `quick_start.py` | **Start here!** Fastest way to get prices | First time setup |
| `simple_price_fetcher.py` | Lightweight price fetcher | Basic price fetching |
| `examples.py` | Basic usage examples | Learning the API |
| `advanced_examples.py` | Portfolio & alerts | Advanced features |
| `web_api.py` | REST API server | Building web apps |
| `src/pyth_service.py` | Full-featured service | Production apps |

## 🔥 Quick Examples

### Get Current Bitcoin Price
```python
from simple_price_fetcher import SimplePythPriceFetcher

fetcher = SimplePythPriceFetcher()
btc_price = fetcher.get_price("BTC/USD")
print(f"BTC: ${btc_price['price']:,.2f}")
```

### Get Multiple Prices
```python
symbols = ["BTC/USD", "ETH/USD", "SOL/USD"]
prices = fetcher.get_multiple_prices(symbols)

for symbol, data in prices.items():
    print(f"{symbol}: ${data['price']:,.2f}")
```

### Use the Web API
```bash
# Start server
python web_api.py

# Get BTC price
curl http://localhost:5000/price/BTC/USD

# Get multiple prices
curl -X POST http://localhost:5000/prices \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC/USD", "ETH/USD"]}'
```

## 🌐 Supported Cryptocurrencies

**Currently available:**
- BTC/USD, ETH/USD, SOL/USD, BNB/USD
- ADA/USD, AVAX/USD, MATIC/USD, DOT/USD  
- UNI/USD, LINK/USD, AAVE/USD, CRV/USD
- USDC/USD, USDT/USD, DAI/USD
- GOLD/USD, EUR/USD, GBP/USD

*See `src/config.py` for the complete list with feed IDs*

## 🚨 Troubleshooting

### "Import Error" or "Module not found"
```bash
# Make sure you have requests installed
pip install requests

# Or install all dependencies
pip install -r requirements.txt
```

### "No prices returned"
```bash
# Test your internet connection
curl https://hermes.pyth.network

# Run the API test script
python test_api.py
```

### "Symbol not supported"
```python
# Check available symbols
fetcher = SimplePythPriceFetcher()
print(fetcher.available_symbols())
```

## 📊 Architecture Overview

```
Your App
    ↓
SimplePythPriceFetcher (lightweight)
    OR
PythPriceService (full-featured)
    ↓
Pyth Network REST API
    ↓
Real-time Price Data
```

## 🎉 Next Steps

1. **Test the basic setup:**
   ```bash
   python quick_start.py
   ```

2. **Try the web API:**
   ```bash
   python web_api.py
   # Visit: http://localhost:5000
   ```

3. **Build your own app:**
   - Use `simple_price_fetcher.py` for basic needs
   - Use `src/pyth_service.py` for advanced features
   - Integrate with your existing Python applications

4. **Add more cryptocurrencies:**
   - Visit: https://pyth.network/developers/price-feed-ids
   - Add feed IDs to `src/config.py`

## 💡 Integration Examples

### Trading Bot
```python
fetcher = SimplePythPriceFetcher()

while True:
    btc = fetcher.get_price("BTC/USD")
    if btc['price'] > 50000:  # Your trading logic
        print("BTC above $50k - Time to sell!")
    time.sleep(60)
```

### Portfolio Tracker
```python
from advanced_examples import PortfolioTracker

portfolio = PortfolioTracker()
portfolio.add_holding("BTC/USD", 0.5)
portfolio.add_holding("ETH/USD", 2.0)
portfolio.print_portfolio_summary()
```

### Price Alerts
```python
from advanced_examples import PriceTracker

tracker = PriceTracker()
tracker.add_alert("BTC/USD", 45000, "above")
tracker.start_tracking(["BTC/USD"], interval=30)
```

## 🔗 Useful Resources

- **Pyth Network Docs:** https://docs.pyth.network/
- **More Price Feeds:** https://pyth.network/developers/price-feed-ids
- **API Documentation:** https://hermes.pyth.network/docs

## ✅ You're Ready!

Your Pyth Network price fetcher is now set up and working. You have everything you need to:

1. ✅ Fetch real-time crypto prices
2. ✅ Build trading applications  
3. ✅ Create portfolio trackers
4. ✅ Set up price monitoring
5. ✅ Integrate with web applications

**Happy coding! 🚀**