"""
Web API Server for Pyth Network Prices

A simple Flask-based web server that provides RESTful API endpoints
for fetching cryptocurrency prices from Pyth Network.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

# Try to import the full service, fall back to simple fetcher
try:
    from src.pyth_service import PythPriceService
    USE_FULL_SERVICE = True
except ImportError:
    from simple_price_fetcher import SimplePythPriceFetcher
    USE_FULL_SERVICE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize price service
if USE_FULL_SERVICE:
    price_service = PythPriceService()
    logger.info("Using full PythPriceService")
else:
    price_service = SimplePythPriceFetcher()
    logger.info("Using SimplePythPriceFetcher")


@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        "service": "Pyth Network Price API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "GET /": "This help message",
            "GET /health": "Service health check",
            "GET /symbols": "List available symbols",
            "GET /price/<symbol>": "Get price for single symbol",
            "POST /prices": "Get prices for multiple symbols",
            "GET /api/v1/price/<symbol>": "Alternative price endpoint"
        },
        "example_usage": {
            "single_price": "/price/BTC/USD",
            "multiple_prices": "POST /prices with JSON body: {\"symbols\": [\"BTC/USD\", \"ETH/USD\"]}"
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test fetching a price to ensure service is working
        if USE_FULL_SERVICE:
            test_price = price_service.get_latest_price("BTC/USD")
        else:
            test_price = price_service.get_price("BTC/USD")
            
        status = "healthy" if test_price else "degraded"
        
        return jsonify({
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "service_type": "full" if USE_FULL_SERVICE else "simple"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/symbols')
def get_symbols():
    """Get list of available symbols"""
    try:
        if USE_FULL_SERVICE:
            symbols = price_service.get_price_feed_ids()
            available_symbols = list(symbols.keys())
        else:
            available_symbols = price_service.available_symbols()
            
        return jsonify({
            "symbols": available_symbols,
            "count": len(available_symbols),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/price/<path:symbol>')
def get_price(symbol):
    """Get price for a single symbol"""
    try:
        # Replace - with / for URL-friendly symbols (e.g., BTC-USD -> BTC/USD)
        symbol = symbol.replace('-', '/')
        
        if USE_FULL_SERVICE:
            price_data = price_service.get_latest_price(symbol)
        else:
            price_data = price_service.get_price(symbol)
            
        if price_data:
            return jsonify({
                "success": True,
                "data": price_data,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": f"No data available for {symbol}",
                "timestamp": datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/prices', methods=['POST'])
def get_multiple_prices():
    """Get prices for multiple symbols"""
    try:
        data = request.get_json()
        if not data or 'symbols' not in data:
            return jsonify({
                "success": False,
                "error": "Request body must contain 'symbols' array"
            }), 400
            
        symbols = data['symbols']
        if not isinstance(symbols, list):
            return jsonify({
                "success": False,
                "error": "'symbols' must be an array"
            }), 400
            
        # Replace - with / in symbols
        symbols = [s.replace('-', '/') for s in symbols]
        
        if USE_FULL_SERVICE:
            prices = price_service.get_multiple_prices(symbols)
        else:
            prices = price_service.get_multiple_prices(symbols)
            
        return jsonify({
            "success": True,
            "data": prices,
            "requested_symbols": symbols,
            "received_count": len(prices),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


# Alternative API endpoints with versioning
@app.route('/api/v1/price/<path:symbol>')
def get_price_v1(symbol):
    """Alternative versioned price endpoint"""
    return get_price(symbol)


@app.route('/api/v1/prices', methods=['POST'])
def get_multiple_prices_v1():
    """Alternative versioned multiple prices endpoint"""
    return get_multiple_prices()


@app.route('/api/v1/symbols')
def get_symbols_v1():
    """Alternative versioned symbols endpoint"""
    return get_symbols()


@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": [
            "/", "/health", "/symbols", "/price/<symbol>", 
            "POST /prices", "/api/v1/..."
        ],
        "timestamp": datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Custom 500 handler"""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500


def create_app(config=None):
    """Application factory"""
    if config:
        app.config.update(config)
    return app


if __name__ == '__main__':
    print("""
🌐 Starting Pyth Network Price API Server
==========================================
    
API Endpoints:
- GET  /                    - API documentation
- GET  /health              - Health check
- GET  /symbols             - List available symbols
- GET  /price/<symbol>      - Get single price (e.g., /price/BTC/USD or /price/BTC-USD)
- POST /prices              - Get multiple prices
- GET  /api/v1/...          - Versioned endpoints

Example Usage:
- Single price: http://localhost:5000/price/BTC/USD
- Multiple prices: POST to http://localhost:5000/prices with {"symbols": ["BTC/USD", "ETH/USD"]}

Press Ctrl+C to stop the server
""")
    
    app.run(
        host='0.0.0.0',  # Accept connections from any IP
        port=5000,
        debug=True,
        use_reloader=False  # Disable auto-reloader to prevent issues
    )