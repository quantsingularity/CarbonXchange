# Example 2: Basic Trading Operations

This example demonstrates placing orders, viewing portfolio, and managing trades.

## Prerequisites

- User registered and authenticated (see [Example 1](01-user-registration.md))
- KYC verified
- Sufficient balance (for buy orders)

## Step 1: View Market Data

```python
import requests

API_BASE = "http://localhost:5000/api"
headers = {"Authorization": f"Bearer {access_token}"}

# Get current market data
response = requests.get(f"{API_BASE}/market/data", headers=headers)
market_data = response.json()['market_data']

for credit in market_data:
    print(f"{credit['credit_type']}: ${credit['last_price']}")
    print(f"  24h Volume: {credit['volume_24h']}")
    print(f"  Bid: ${credit['bid_price']} | Ask: ${credit['ask_price']}")
```

## Step 2: Place Market Buy Order

```python
# Buy 100 tCO2e of renewable energy credits at market price
market_order = {
    "order_type": "market",
    "side": "buy",
    "quantity": 100,
    "credit_type": "renewable_energy"
}

response = requests.post(
    f"{API_BASE}/trading/orders",
    json=market_order,
    headers=headers
)

order = response.json()['order']
print(f"Order ID: {order['id']}")
print(f"Status: {order['status']}")
print(f"Quantity: {order['quantity']}")
```

## Step 3: Place Limit Sell Order

```python
# Sell 50 tCO2e at $27.50 or better
limit_order = {
    "order_type": "limit",
    "side": "sell",
    "quantity": 50,
    "price": 27.50,
    "credit_type": "renewable_energy",
    "time_in_force": "GTC"  # Good Till Cancelled
}

response = requests.post(
    f"{API_BASE}/trading/orders",
    json=limit_order,
    headers=headers
)

order = response.json()['order']
print(f"Limit Order ID: {order['id']}")
print(f"Price: ${order['price']}")
```

## Step 4: Check Order Status

```python
# Get specific order
order_id = order['id']
response = requests.get(
    f"{API_BASE}/trading/orders/{order_id}",
    headers=headers
)

order_status = response.json()['order']
print(f"Status: {order_status['status']}")
print(f"Filled: {order_status['filled_quantity']}/{order_status['quantity']}")
```

## Step 5: View Open Orders

```python
# List all open orders
response = requests.get(
    f"{API_BASE}/trading/orders?status=open",
    headers=headers
)

orders = response.json()['orders']
for order in orders:
    print(f"Order {order['id']}: {order['side']} {order['quantity']} @ ${order.get('price', 'market')}")
```

## Step 6: Cancel Order

```python
# Cancel an open order
response = requests.delete(
    f"{API_BASE}/trading/orders/{order_id}",
    headers=headers
)

if response.status_code == 200:
    print("Order cancelled successfully")
```

## Step 7: View Portfolio

```python
# Get portfolio summary
response = requests.get(f"{API_BASE}/users/portfolio", headers=headers)
portfolio = response.json()['portfolio']

print(f"Total Value: ${portfolio['total_value']:.2f}")
print(f"Cost Basis: ${portfolio['cost_basis']:.2f}")
print(f"Unrealized P&L: ${portfolio['unrealized_pnl']:.2f}")
print(f"Realized P&L: ${portfolio['realized_pnl']:.2f}")

print("\nHoldings:")
for holding in portfolio['holdings']:
    print(f"  {holding['credit_type']}: {holding['quantity']} tCO2e")
    print(f"    Avg Price: ${holding['average_price']:.2f}")
    print(f"    Current: ${holding['current_market_price']:.2f}")
    print(f"    P&L: ${holding['unrealized_pnl']:.2f}")
```

## Step 8: View Trade History

```python
# Get recent trades
response = requests.get(
    f"{API_BASE}/trading/trades?limit=10",
    headers=headers
)

trades = response.json()['trades']
for trade in trades:
    print(f"Trade {trade['id']}: {trade['side']} {trade['quantity']} @ ${trade['price']}")
    print(f"  Executed: {trade['executed_at']}")
```

## Complete Trading Client

```python
import requests
from typing import Dict, List, Optional

class TradingClient:
    def __init__(self, api_base: str, access_token: str):
        self.api_base = api_base
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def get_market_data(self, credit_type: Optional[str] = None) -> List[Dict]:
        """Get current market data"""
        params = {}
        if credit_type:
            params['credit_type'] = credit_type

        response = requests.get(
            f"{self.api_base}/market/data",
            headers=self.headers,
            params=params
        )
        return response.json()['market_data']

    def place_order(self, order_type: str, side: str, quantity: int,
                   credit_type: str, price: Optional[float] = None,
                   **kwargs) -> Dict:
        """Place a trading order"""
        data = {
            "order_type": order_type,
            "side": side,
            "quantity": quantity,
            "credit_type": credit_type,
            **kwargs
        }
        if price:
            data["price"] = price

        response = requests.post(
            f"{self.api_base}/trading/orders",
            json=data,
            headers=self.headers
        )
        return response.json()['order']

    def get_order(self, order_id: int) -> Dict:
        """Get order by ID"""
        response = requests.get(
            f"{self.api_base}/trading/orders/{order_id}",
            headers=self.headers
        )
        return response.json()['order']

    def cancel_order(self, order_id: int) -> bool:
        """Cancel an order"""
        response = requests.delete(
            f"{self.api_base}/trading/orders/{order_id}",
            headers=self.headers
        )
        return response.status_code == 200

    def get_portfolio(self) -> Dict:
        """Get portfolio summary"""
        response = requests.get(
            f"{self.api_base}/users/portfolio",
            headers=self.headers
        )
        return response.json()['portfolio']

# Usage
client = TradingClient(API_BASE, access_token)

# Check market
market = client.get_market_data("renewable_energy")
current_price = market[0]['last_price']
print(f"Current price: ${current_price}")

# Place limit buy order
order = client.place_order(
    order_type="limit",
    side="buy",
    quantity=100,
    credit_type="renewable_energy",
    price=current_price * 0.98,  # 2% below market
    time_in_force="GTC"
)

print(f"Order placed: {order['id']}")

# Check portfolio
portfolio = client.get_portfolio()
print(f"Portfolio value: ${portfolio['total_value']}")
```

## Next Steps

- See [Example 3](03-advanced-trading.md) for advanced order types
- Review [API Reference](../API.md) for complete trading endpoints
- Check [Feature Matrix](../FEATURE_MATRIX.md) for all trading features
