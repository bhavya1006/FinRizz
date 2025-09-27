# Pyth Network Real-time Price Fetcher

A comprehensive Python implementation for fetching real-time cryptocurrency prices using the Pyth Network REST API.

## 🚀 Quick Start

### 1. Minimal Setup (Recommended for beginners)

```bash
# Install only the core dependency
pip install requests

# Run the quick start script
python quick_start.py

# Or use the simple fetcher directly
python simple_price_fetcher.py
```

### 2. Full Setup (For advanced features)

```bash
# Install all dependencies
pip install -r requirements.txt

# Run comprehensive examples
python examples.py

# Run advanced features demo
python advanced_examples.py
```

## 📁 Project Structure

```
FinRizz/
├── README.md                   # This file
├── requirements.txt            # Full dependencies
├── requirements_minimal.txt    # Minimal dependencies
├── .env                       # Environment configuration
├── quick_start.py             # Fastest way to get started
├── simple_price_fetcher.py    # Lightweight price fetcher
├── examples.py                # Basic usage examples
├── advanced_examples.py       # Advanced features demo
├── web_api.py                 # REST API server
└── src/
    ├── config.py              # Price feed configurations
    └── pyth_service.py        # Full-featured service class
```

## 🎯 Features

### Core Features
- ✅ Real-time price fetching from Pyth Network
- ✅ Support for major cryptocurrencies (BTC, ETH, SOL, etc.)
- ✅ Simple and advanced API interfaces
- ✅ Error handling and retry logic
- ✅ Multiple price fetching with batching

### Advanced Features
- ✅ Asynchronous price fetching
- ✅ Price streaming and monitoring
- ✅ Portfolio tracking and valuation
- ✅ Price alerts and notifications
- ✅ Historical data analytics
- ✅ Web API server with REST endpoints
- ✅ Data export capabilities

## 📊 Supported Assets

Currently supports 20+ major cryptocurrencies including:

**Major Cryptocurrencies:**
- BTC/USD, ETH/USD, SOL/USD, BNB/USD
- ADA/USD, AVAX/USD, MATIC/USD, DOT/USD

**DeFi Tokens:**
- UNI/USD, LINK/USD, AAVE/USD, CRV/USD

**Stablecoins:**
- USDC/USD, USDT/USD, DAI/USD

**Traditional Assets:**
- GOLD/USD, EUR/USD, GBP/USD

*See `src/config.py` for the complete list and feed IDs.*

## 🔧 Usage Examples

### Simple Price Fetching

```python
from simple_price_fetcher import SimplePythPriceFetcher

# Initialize fetcher
fetcher = SimplePythPriceFetcher()

# Get single price
btc_price = fetcher.get_price("BTC/USD")
print(f"BTC Price: ${btc_price['price']:,.2f}")

# Get multiple prices
symbols = ["BTC/USD", "ETH/USD", "SOL/USD"]
prices = fetcher.get_multiple_prices(symbols)

for symbol, data in prices.items():
    print(f"{symbol}: ${data['price']:,.2f}")
```

### Advanced Usage

```python
from src.pyth_service import PythPriceService

# Initialize service
with PythPriceService() as service:
    # Get detailed price data
    btc_data = service.get_latest_price("BTC/USD")
    print(f"BTC: ${btc_data['price']:.4f} ±${btc_data['confidence_interval']:.4f}")
    
    # Stream prices
    service.stream_prices(["BTC/USD", "ETH/USD"], interval=5.0)
```

### Web API Server

```python
# Start the web server
python web_api.py

# Use the REST API
curl http://localhost:5000/price/BTC/USD
curl -X POST http://localhost:5000/prices -H "Content-Type: application/json" -d '{"symbols": ["BTC/USD", "ETH/USD"]}'
```

## 🌐 API Endpoints

When running the web server (`python web_api.py`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/health` | Service health check |
| GET | `/symbols` | List available symbols |
| GET | `/price/<symbol>` | Get single price |
| POST | `/prices` | Get multiple prices |

### Example API Usage

```bash
# Get BTC price
curl http://localhost:5000/price/BTC/USD

# Get multiple prices
curl -X POST http://localhost:5000/prices \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC/USD", "ETH/USD", "SOL/USD"]}'

# List all available symbols
curl http://localhost:5000/symbols
```

## 📦 Installation Options

### Option 1: Minimal Installation (Recommended for basic use)

```bash
# Clone the repository
git clone <your-repo-url>
cd FinRizz

# Install minimal requirements
pip install -r requirements_minimal.txt

# Run quick start
python quick_start.py
```

### Option 2: Full Installation (For all features)

```bash
# Install all requirements
pip install -r requirements.txt

# Run comprehensive examples
python examples.py
```

### Option 3: Manual Installation

```bash
# For basic functionality
pip install requests

# For advanced features, add:
pip install aiohttp asyncio-throttle pandas python-dotenv

# For web API
pip install flask flask-cors
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Application                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              Pyth Price Service                             │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐│
│  │  Simple Fetcher     │  │    Advanced Service             ││
│  │  - Basic prices     │  │    - Async operations           ││
│  │  - Minimal deps     │  │    - Price streaming            ││
│  │  - Fast setup       │  │    - Portfolio tracking         ││
│  └─────────────────────┘  └─────────────────────────────────┘│
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                 Pyth Network REST API                       │
│              https://hermes.pyth.network                    │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Configuration

### Environment Variables (.env file)

```bash
# Pyth Network Configuration
PYTH_REST_API_URL=https://hermes.pyth.network
```

### Custom Price Feeds

Add your own price feeds in `src/config.py`:

```python
PRICE_FEEDS = {
    "YOUR_TOKEN/USD": "0x...your_feed_id_here...",
    # Add more feeds as needed
}
```

Find more feed IDs at: https://pyth.network/developers/price-feed-ids

## 🚨 Error Handling

The service includes comprehensive error handling:

- **Network errors**: Automatic retries with exponential backoff
- **Invalid symbols**: Graceful handling with error messages
- **API rate limits**: Built-in throttling and respect for limits
- **Data validation**: Parsing and validation of API responses

## 📈 Performance Tips

1. **Batch requests**: Use `get_multiple_prices()` for multiple symbols
2. **Caching**: Implement caching for frequently accessed prices
3. **Async operations**: Use async methods for better performance
4. **Rate limiting**: Respect API rate limits with built-in throttling

## 🔄 Real-time Streaming

```python
from src.pyth_service import PythPriceService

def price_update_callback(prices):
    for symbol, data in prices.items():
        print(f"{symbol}: ${data['price']:.4f}")

with PythPriceService() as service:
    service.stream_prices(
        symbols=["BTC/USD", "ETH/USD"], 
        interval=5.0, 
        callback=price_update_callback
    )
```

## 🧪 Testing

```bash
# Run basic test
python quick_start.py

# Test all features
python examples.py

# Test advanced features
python advanced_examples.py

# Test web API
python web_api.py
# Then visit: http://localhost:5000
```

## 📊 Portfolio Tracking Example

```python
from advanced_examples import PortfolioTracker

# Create portfolio
portfolio = PortfolioTracker()

# Add holdings
portfolio.add_holding("BTC/USD", 0.5)
portfolio.add_holding("ETH/USD", 2.0)
portfolio.add_holding("SOL/USD", 100.0)

# Get current value
portfolio.print_portfolio_summary()
```

## 🚨 Price Alerts Example

```python
from advanced_examples import PriceTracker

# Set up price tracking with alerts
tracker = PriceTracker()

# Add alerts
tracker.add_alert("BTC/USD", 45000, "above")
tracker.add_alert("ETH/USD", 2000, "below")

# Start tracking
tracker.start_tracking(["BTC/USD", "ETH/USD"], interval=30)
```

## 📚 Resources

- **Pyth Network Documentation**: https://docs.pyth.network/
- **Price Feed IDs**: https://pyth.network/developers/price-feed-ids
- **Pyth REST API**: https://hermes.pyth.network/docs
- **Create Your First Pyth App**: https://docs.pyth.network/price-feeds/create-your-first-pyth-app/evm/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💡 Support

If you encounter any issues:

1. Check the examples in this repository
2. Review the Pyth Network documentation
3. Open an issue on GitHub
4. Make sure your internet connection is stable

## 🎉 What's Next?

After getting started:

1. **Integrate with your application**: Use the price data in your trading bots, portfolio trackers, or DeFi applications
2. **Set up monitoring**: Implement price alerts for your favorite assets
3. **Build a dashboard**: Create a web interface using the provided API
4. **Add more features**: Extend the service with additional Pyth Network features

---

**Happy trading with real-time Pyth Network prices! 🚀**
