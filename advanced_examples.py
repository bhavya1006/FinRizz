"""
Advanced Pyth Network Integration Examples

This module provides more advanced usage patterns for integrating Pyth price feeds
into applications, including data analysis, alerting, and portfolio tracking.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, asdict
import statistics

from src.pyth_service import PythPriceService


@dataclass
class PriceAlert:
    """Price alert configuration"""
    symbol: str
    target_price: float
    condition: str  # 'above', 'below'
    created_at: datetime
    triggered: bool = False
    
    def check_trigger(self, current_price: float) -> bool:
        """Check if alert should be triggered"""
        if self.triggered:
            return False
            
        if self.condition == 'above' and current_price >= self.target_price:
            self.triggered = True
            return True
        elif self.condition == 'below' and current_price <= self.target_price:
            self.triggered = True
            return True
            
        return False


class PriceTracker:
    """Advanced price tracking with analytics and alerts"""
    
    def __init__(self):
        self.price_service = PythPriceService()
        self.price_history: Dict[str, List[Dict]] = {}
        self.alerts: List[PriceAlert] = []
        self.is_tracking = False
        self.tracking_thread = None
        
    def add_alert(self, symbol: str, target_price: float, condition: str) -> None:
        """Add a price alert"""
        alert = PriceAlert(
            symbol=symbol,
            target_price=target_price,
            condition=condition,
            created_at=datetime.now()
        )
        self.alerts.append(alert)
        print(f"🚨 Alert added: {symbol} {condition} ${target_price:.4f}")
        
    def start_tracking(self, symbols: List[str], interval: int = 10) -> None:
        """Start tracking prices in background"""
        if self.is_tracking:
            print("⚠️  Tracking already active")
            return
            
        self.is_tracking = True
        self.tracking_thread = threading.Thread(
            target=self._tracking_loop,
            args=(symbols, interval),
            daemon=True
        )
        self.tracking_thread.start()
        print(f"📡 Started tracking {len(symbols)} symbols every {interval}s")
        
    def stop_tracking(self) -> None:
        """Stop price tracking"""
        self.is_tracking = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=5)
        print("🛑 Price tracking stopped")
        
    def _tracking_loop(self, symbols: List[str], interval: int) -> None:
        """Main tracking loop"""
        while self.is_tracking:
            try:
                prices = self.price_service.get_multiple_prices(symbols)
                timestamp = datetime.now()
                
                # Store price history
                for symbol, data in prices.items():
                    if data:
                        price_point = {
                            'timestamp': timestamp,
                            'price': data['price'],
                            'confidence': data['confidence_interval']
                        }
                        
                        if symbol not in self.price_history:
                            self.price_history[symbol] = []
                            
                        self.price_history[symbol].append(price_point)
                        
                        # Check alerts
                        self._check_alerts(symbol, data['price'])
                        
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Tracking error: {e}")
                time.sleep(interval)
                
    def _check_alerts(self, symbol: str, current_price: float) -> None:
        """Check and trigger price alerts"""
        for alert in self.alerts:
            if alert.symbol == symbol and alert.check_trigger(current_price):
                print(f"""
🚨 PRICE ALERT TRIGGERED! 🚨
Symbol: {symbol}
Current Price: ${current_price:.4f}
Alert: {symbol} {alert.condition} ${alert.target_price:.4f}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
                
    def get_price_analytics(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        """Get price analytics for a symbol"""
        if symbol not in self.price_history:
            return {"error": f"No price history for {symbol}"}
            
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_prices = [
            p for p in self.price_history[symbol] 
            if p['timestamp'] >= cutoff_time
        ]
        
        if not recent_prices:
            return {"error": f"No recent price data for {symbol}"}
            
        prices = [p['price'] for p in recent_prices]
        
        return {
            "symbol": symbol,
            "period_hours": hours,
            "data_points": len(prices),
            "current_price": prices[-1],
            "highest_price": max(prices),
            "lowest_price": min(prices),
            "average_price": statistics.mean(prices),
            "median_price": statistics.median(prices),
            "price_change": prices[-1] - prices[0] if len(prices) > 1 else 0,
            "price_change_percent": ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 1 and prices[0] > 0 else 0,
            "volatility": statistics.stdev(prices) if len(prices) > 1 else 0,
            "first_timestamp": recent_prices[0]['timestamp'].isoformat(),
            "last_timestamp": recent_prices[-1]['timestamp'].isoformat()
        }
        
    def export_data(self, filename: str = None) -> str:
        """Export price history to JSON file"""
        if not filename:
            filename = f"price_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        # Convert datetime objects to strings for JSON serialization
        export_data = {}
        for symbol, history in self.price_history.items():
            export_data[symbol] = [
                {
                    'timestamp': point['timestamp'].isoformat(),
                    'price': point['price'],
                    'confidence': point['confidence']
                }
                for point in history
            ]
            
        # Add alerts data
        export_data['_alerts'] = [
            {
                'symbol': alert.symbol,
                'target_price': alert.target_price,
                'condition': alert.condition,
                'created_at': alert.created_at.isoformat(),
                'triggered': alert.triggered
            }
            for alert in self.alerts
        ]
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        print(f"📁 Data exported to {filename}")
        return filename


class PortfolioTracker:
    """Track a cryptocurrency portfolio with Pyth prices"""
    
    def __init__(self):
        self.price_service = PythPriceService()
        self.holdings: Dict[str, float] = {}  # symbol -> quantity
        
    def add_holding(self, symbol: str, quantity: float) -> None:
        """Add or update a holding"""
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
        print(f"💼 Added {quantity} {symbol} to portfolio")
        
    def remove_holding(self, symbol: str, quantity: float = None) -> None:
        """Remove holding (partially or completely)"""
        if symbol not in self.holdings:
            print(f"⚠️  {symbol} not found in portfolio")
            return
            
        if quantity is None:
            # Remove completely
            del self.holdings[symbol]
            print(f"🗑️  Removed all {symbol} from portfolio")
        else:
            # Remove partially
            self.holdings[symbol] = max(0, self.holdings[symbol] - quantity)
            if self.holdings[symbol] == 0:
                del self.holdings[symbol]
            print(f"📉 Removed {quantity} {symbol} from portfolio")
            
    def get_portfolio_value(self) -> Dict[str, Any]:
        """Get current portfolio valuation"""
        if not self.holdings:
            return {"error": "Portfolio is empty"}
            
        symbols = list(self.holdings.keys())
        prices = self.price_service.get_multiple_prices(symbols)
        
        total_value = 0
        holdings_value = {}
        
        for symbol, quantity in self.holdings.items():
            price_data = prices.get(symbol)
            if price_data:
                value = quantity * price_data['price']
                total_value += value
                holdings_value[symbol] = {
                    'quantity': quantity,
                    'price': price_data['price'],
                    'value': value,
                    'percentage': 0  # Will calculate after total
                }
            else:
                holdings_value[symbol] = {
                    'quantity': quantity,
                    'price': None,
                    'value': 0,
                    'percentage': 0
                }
                
        # Calculate percentages
        for symbol in holdings_value:
            if total_value > 0:
                holdings_value[symbol]['percentage'] = (holdings_value[symbol]['value'] / total_value) * 100
                
        return {
            'total_value': total_value,
            'holdings': holdings_value,
            'timestamp': datetime.now().isoformat()
        }
        
    def print_portfolio_summary(self) -> None:
        """Print a formatted portfolio summary"""
        portfolio = self.get_portfolio_value()
        
        if 'error' in portfolio:
            print(f"❌ {portfolio['error']}")
            return
            
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                              PORTFOLIO SUMMARY                                   ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Total Value: ${portfolio['total_value']:>20,.2f}                               ║
║ Timestamp: {portfolio['timestamp'][:19]:>22}                                     ║
╠══════════════════════════════════════════════════════════════════════════════════╣""")
        
        for symbol, data in portfolio['holdings'].items():
            if data['value'] > 0:
                print(f"║ {symbol:<12} {data['quantity']:>10.4f} @ ${data['price']:>8.4f} = ${data['value']:>12.2f} ({data['percentage']:>5.1f}%) ║")
            else:
                print(f"║ {symbol:<12} {data['quantity']:>10.4f} @ {'N/A':>8} = {'N/A':>12} ({'N/A':>5}) ║")
                
        print("╚══════════════════════════════════════════════════════════════════════════════════╝")


def demo_advanced_features():
    """Demonstrate advanced features"""
    print("🔬 Advanced Features Demo")
    print("=" * 50)
    
    # Portfolio tracking demo
    print("\n💼 Portfolio Tracking Demo")
    portfolio = PortfolioTracker()
    
    # Add some holdings
    portfolio.add_holding("BTC/USD", 0.5)
    portfolio.add_holding("ETH/USD", 2.0)
    portfolio.add_holding("SOL/USD", 100.0)
    
    # Show portfolio value
    portfolio.print_portfolio_summary()
    
    # Price tracking with analytics demo
    print("\n📊 Price Analytics Demo")
    tracker = PriceTracker()
    
    # Add some alerts
    tracker.add_alert("BTC/USD", 45000, "above")
    tracker.add_alert("ETH/USD", 2000, "below")
    
    # Simulate some price tracking (in real app, this would run continuously)
    print("\n📡 Starting price tracking simulation...")
    symbols = ["BTC/USD", "ETH/USD"]
    
    # Manually add some fake history for demo
    current_time = datetime.now()
    for symbol in symbols:
        tracker.price_history[symbol] = []
        # Add some fake historical data
        for i in range(10):
            price_point = {
                'timestamp': current_time - timedelta(minutes=i*10),
                'price': 40000 + (i * 100) if symbol == "BTC/USD" else 2500 + (i * 10),
                'confidence': 50 if symbol == "BTC/USD" else 5
            }
            tracker.price_history[symbol].append(price_point)
    
    # Show analytics
    for symbol in symbols:
        analytics = tracker.get_price_analytics(symbol, hours=2)
        print(f"\n📈 Analytics for {symbol}:")
        print(f"   Current: ${analytics.get('current_price', 0):.2f}")
        print(f"   24h Change: {analytics.get('price_change_percent', 0):.2f}%")
        print(f"   Volatility: ${analytics.get('volatility', 0):.2f}")
    
    # Export data
    filename = tracker.export_data()
    print(f"\n💾 Data exported to {filename}")


if __name__ == "__main__":
    try:
        demo_advanced_features()
        print("\n🎉 Advanced features demo completed!")
        
    except Exception as e:
        print(f"❌ Error in advanced demo: {e}")
        import traceback
        traceback.print_exc()