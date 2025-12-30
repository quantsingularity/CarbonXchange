# Example 3: Advanced Trading Strategies

This example demonstrates advanced order types, stop-loss, and automated trading strategies.

## Stop-Limit Orders

Protect your positions with stop-limit orders:

```python
import requests

API_BASE = "http://localhost:5000/api"
headers = {"Authorization": f"Bearer {access_token}"}

# Place stop-limit sell order
# If price drops to $24.00, sell at $23.50 or better
stop_limit_order = {
    "order_type": "stop_limit",
    "side": "sell",
    "quantity": 100,
    "credit_type": "renewable_energy",
    "stop_price": 24.00,  # Trigger price
    "price": 23.50,  # Limit price
    "time_in_force": "GTC"
}

response = requests.post(
    f"{API_BASE}/trading/orders",
    json=stop_limit_order,
    headers=headers
)

order = response.json()['order']
print(f"Stop-Limit Order: {order['id']}")
print(f"Triggers at: ${order['stop_price']}")
print(f"Sells at: ${order['price']} or better")
```

## Dollar-Cost Averaging (DCA) Strategy

Automate regular purchases:

```python
import time
from datetime import datetime

def dca_strategy(client, credit_type, amount_per_purchase, interval_days):
    """
    Dollar-cost averaging strategy

    Args:
        client: TradingClient instance
        credit_type: Type of credit to purchase
        amount_per_purchase: Amount in USD per purchase
        interval_days: Days between purchases
    """
    while True:
        try:
            # Get current market price
            market = client.get_market_data(credit_type)
            current_price = market[0]['last_price']

            # Calculate quantity
            quantity = int(amount_per_purchase / current_price)

            # Place market order
            order = client.place_order(
                order_type="market",
                side="buy",
                quantity=quantity,
                credit_type=credit_type
            )

            print(f"{datetime.now()}: Purchased {quantity} tCO2e @ ${current_price}")
            print(f"Order ID: {order['id']}")

            # Wait for next interval
            time.sleep(interval_days * 24 * 60 * 60)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3600)  # Wait 1 hour on error

# Run DCA strategy: $1000 every 7 days
# dca_strategy(client, "renewable_energy", 1000, 7)
```

## Grid Trading Strategy

Profit from price volatility:

```python
def grid_trading_strategy(client, credit_type, grid_size=10, grid_spacing=0.5):
    """
    Grid trading strategy

    Args:
        client: TradingClient instance
        credit_type: Type of credit to trade
        grid_size: Number of grid levels
        grid_spacing: Price spacing between grid levels (%)
    """
    # Get current price
    market = client.get_market_data(credit_type)
    current_price = market[0]['last_price']

    # Place buy orders below current price
    for i in range(1, grid_size + 1):
        buy_price = current_price * (1 - (grid_spacing * i) / 100)

        order = client.place_order(
            order_type="limit",
            side="buy",
            quantity=10,  # Fixed quantity per grid level
            credit_type=credit_type,
            price=round(buy_price, 2),
            time_in_force="GTC"
        )

        print(f"Buy order at ${buy_price:.2f}: {order['id']}")

    # Place sell orders above current price
    for i in range(1, grid_size + 1):
        sell_price = current_price * (1 + (grid_spacing * i) / 100)

        order = client.place_order(
            order_type="limit",
            side="sell",
            quantity=10,
            credit_type=credit_type,
            price=round(sell_price, 2),
            time_in_force="GTC"
        )

        print(f"Sell order at ${sell_price:.2f}: {order['id']}")

# Execute grid strategy
# grid_trading_strategy(client, "renewable_energy", grid_size=5, grid_spacing=1.0)
```

## Portfolio Rebalancing

Maintain target allocation:

```python
def rebalance_portfolio(client, target_allocation):
    """
    Rebalance portfolio to target allocation

    Args:
        client: TradingClient instance
        target_allocation: Dict of {credit_type: percentage}
            Example: {"renewable_energy": 60, "reforestation": 40}
    """
    # Get current portfolio
    portfolio = client.get_portfolio()
    total_value = portfolio['total_value']

    # Calculate current allocation
    current_allocation = {}
    for holding in portfolio['holdings']:
        credit_type = holding['credit_type']
        value = holding['quantity'] * holding['current_market_price']
        current_allocation[credit_type] = (value / total_value) * 100

    # Determine trades needed
    for credit_type, target_pct in target_allocation.items():
        current_pct = current_allocation.get(credit_type, 0)
        diff_pct = target_pct - current_pct

        if abs(diff_pct) < 1.0:  # Within 1% is close enough
            continue

        # Get current price
        market = client.get_market_data(credit_type)
        current_price = market[0]['last_price']

        # Calculate quantity to trade
        value_to_trade = (diff_pct / 100) * total_value
        quantity = abs(int(value_to_trade / current_price))

        if diff_pct > 0:  # Need to buy more
            print(f"Buy {quantity} {credit_type} (currently {current_pct:.1f}%, target {target_pct}%)")
            order = client.place_order(
                order_type="market",
                side="buy",
                quantity=quantity,
                credit_type=credit_type
            )
        else:  # Need to sell some
            print(f"Sell {quantity} {credit_type} (currently {current_pct:.1f}%, target {target_pct}%)")
            order = client.place_order(
                order_type="market",
                side="sell",
                quantity=quantity,
                credit_type=credit_type
            )

        print(f"Rebalance order: {order['id']}")

# Rebalance to 60/40 allocation
# target = {
#     "renewable_energy": 60,
#     "reforestation": 40
# }
# rebalance_portfolio(client, target)
```

## Risk Management

Implement position sizing and stop-loss:

```python
class RiskManager:
    def __init__(self, client, max_position_pct=20, max_loss_pct=5):
        """
        Initialize risk manager

        Args:
            client: TradingClient instance
            max_position_pct: Maximum position size as % of portfolio
            max_loss_pct: Maximum loss before stop-loss triggers (%)
        """
        self.client = client
        self.max_position_pct = max_position_pct
        self.max_loss_pct = max_loss_pct

    def calculate_position_size(self, credit_type, price):
        """Calculate safe position size"""
        portfolio = self.client.get_portfolio()
        total_value = portfolio['total_value']

        max_position_value = total_value * (self.max_position_pct / 100)
        max_quantity = int(max_position_value / price)

        return max_quantity

    def place_safe_order(self, credit_type, side, price):
        """Place order with risk management"""
        # Calculate position size
        quantity = self.calculate_position_size(credit_type, price)

        # Place main order
        order = self.client.place_order(
            order_type="limit",
            side=side,
            quantity=quantity,
            credit_type=credit_type,
            price=price,
            time_in_force="GTC"
        )

        print(f"Main order: {order['id']} for {quantity} tCO2e")

        # Place stop-loss if buying
        if side == "buy":
            stop_price = price * (1 - self.max_loss_pct / 100)
            stop_order = self.client.place_order(
                order_type="stop_limit",
                side="sell",
                quantity=quantity,
                credit_type=credit_type,
                stop_price=round(stop_price, 2),
                price=round(stop_price * 0.99, 2),  # 1% slippage
                time_in_force="GTC"
            )
            print(f"Stop-loss order: {stop_order['id']} at ${stop_price:.2f}")

        return order

# Usage
risk_mgr = RiskManager(client, max_position_pct=20, max_loss_pct=5)

# Place order with automatic risk management
order = risk_mgr.place_safe_order(
    credit_type="renewable_energy",
    side="buy",
    price=25.00
)
```

## Next Steps

- Review [API Reference](../API.md) for complete trading capabilities
- See [Feature Matrix](../FEATURE_MATRIX.md) for all trading features
- Check [Troubleshooting](../TROUBLESHOOTING.md) for common trading issues
