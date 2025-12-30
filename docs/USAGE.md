# Usage Guide

This guide demonstrates typical usage patterns and workflows for the CarbonXchange platform, covering both CLI operations and programmatic API usage.

## Table of Contents

- [User Roles and Workflows](#user-roles-and-workflows)
- [CLI Usage](#cli-usage)
- [Web Interface Usage](#web-interface-usage)
- [API Usage (Library)](#api-usage-library)
- [Common Workflows](#common-workflows)
- [Trading Operations](#trading-operations)
- [Portfolio Management](#portfolio-management)
- [Compliance and Reporting](#compliance-and-reporting)

## User Roles and Workflows

CarbonXchange supports multiple user roles:

| Role                  | Capabilities                           | Typical Workflow                                   |
| --------------------- | -------------------------------------- | -------------------------------------------------- |
| **Individual Trader** | Buy/sell credits, view portfolio       | Register → KYC → Trade → Monitor                   |
| **Corporate Buyer**   | Bulk purchases, compliance reporting   | Register → KYC → Purchase → Retire → Report        |
| **Credit Issuer**     | Issue new credits, manage projects     | Register → Verify → Issue → Monitor                |
| **Administrator**     | Platform management, user verification | Manage users → Monitor system → Generate reports   |
| **Auditor**           | View audit logs, compliance reports    | Access logs → Review transactions → Export reports |

## CLI Usage

CarbonXchange provides several CLI scripts for development, deployment, and maintenance.

### Environment Management

Manage development environment and dependencies:

```bash
# Set up complete development environment
./scripts/dev_env/cx_env_manager.sh --all

# Check system prerequisites
./scripts/dev_env/cx_env_manager.sh --check

# Update dependencies
./scripts/dev_env/cx_env_manager.sh --update

# Clean build artifacts
./scripts/maintenance/cx_cleanup.sh
```

### Service Orchestration

Control platform services:

```bash
# Start all services
./scripts/orchestration/cx_service_orchestrator.sh start

# Stop all services
./scripts/orchestration/cx_service_orchestrator.sh stop

# Restart specific service
./scripts/orchestration/cx_service_orchestrator.sh restart backend

# Check service status
./scripts/orchestration/cx_service_orchestrator.sh status

# View logs
./scripts/orchestration/cx_service_orchestrator.sh logs backend
```

**Available services:**

- `backend` - Flask API server
- `frontend` - React web application
- `database` - PostgreSQL server
- `redis` - Redis cache
- `blockchain` - Local blockchain node (if configured)

### Testing

Run automated tests:

```bash
# Run all tests
./scripts/testing/cx_test_runner.sh --all

# Run unit tests only
./scripts/testing/cx_test_runner.sh --unit

# Run integration tests
./scripts/testing/cx_test_runner.sh --integration

# Generate coverage report
./scripts/testing/cx_test_runner.sh --coverage

# Run specific test file
./scripts/testing/cx_test_runner.sh --file tests/test_trading_service.py
```

### Deployment

Deploy to different environments:

```bash
# Deploy to development
./scripts/deployment/cx_deploy.sh deploy dev

# Deploy to staging
./scripts/deployment/cx_deploy.sh deploy staging

# Deploy to production (with confirmation)
./scripts/deployment/cx_deploy.sh deploy production

# Rollback deployment
./scripts/deployment/cx_deploy.sh rollback production

# Check deployment status
./scripts/deployment/cx_deploy.sh status production
```

### Documentation Generation

Generate API documentation:

```bash
# Generate all documentation
./scripts/docs/cx_docs_generator.sh --all

# Generate API docs only
./scripts/docs/cx_docs_generator.sh --api

# Generate changelog
./scripts/docs/cx_docs_generator.sh --changelog
```

### Data Management

Manage application data:

```bash
# Backup database
./scripts/data/cx_data_manager.sh backup

# Restore from backup
./scripts/data/cx_data_manager.sh restore backup_file.sql

# Export market data
./scripts/data/cx_data_manager.sh export market-data --output data.csv

# Import seed data
./scripts/data/cx_data_manager.sh import seed-data
```

### Version Management

Check and update version information:

```bash
# Display current version
./scripts/tools/cx_version.sh --current

# Bump version (patch)
./scripts/tools/cx_version.sh --bump patch

# Bump version (minor)
./scripts/tools/cx_version.sh --bump minor

# Bump version (major)
./scripts/tools/cx_version.sh --bump major
```

## Web Interface Usage

### Registration and Authentication

1. **Register New Account**
    - Navigate to `http://localhost:3000/register`
    - Provide email, password, and wallet address
    - Verify email (check logs in development)
    - Complete KYC verification

2. **Login**
    - Navigate to `http://localhost:3000/login`
    - Enter credentials
    - Enable MFA (recommended)
    - Access dashboard

3. **Enable Two-Factor Authentication**
    - Go to Settings → Security
    - Click "Enable 2FA"
    - Scan QR code with authenticator app
    - Enter verification code

### Trading Interface

**View Market Data:**

- Dashboard shows real-time prices
- Click "Market" to view detailed order book
- Filter by credit type, vintage year, project

**Place Order:**

1. Navigate to Trading → New Order
2. Select order type (Market, Limit, Stop-Limit)
3. Choose side (Buy/Sell)
4. Enter quantity
5. Set price (for limit orders)
6. Review and submit
7. Monitor execution in Orders tab

**Example Market Order:**

- Type: Market
- Side: Buy
- Quantity: 100 tCO2e
- Credit Type: Renewable Energy
- Execution: Immediate at best available price

**Example Limit Order:**

- Type: Limit
- Side: Sell
- Quantity: 50 tCO2e
- Price: $25.50 per tCO2e
- Time in Force: GTC (Good Till Cancelled)

### Portfolio Management

**View Portfolio:**

- Navigate to Portfolio tab
- View holdings by credit type
- See unrealized gains/losses
- Export portfolio report

**Retire Credits:**

1. Go to Portfolio → Select credits
2. Click "Retire"
3. Enter quantity to retire
4. Provide retirement reason
5. Confirm transaction
6. Receive retirement certificate

## API Usage (Library)

Use CarbonXchange as a Python library for programmatic access:

### Authentication

```python
import requests

API_BASE = "http://localhost:5000/api"

# Register new user
response = requests.post(f"{API_BASE}/auth/register", json={
    "email": "trader@example.com",
    "password": "SecurePass123!",
    "full_name": "Jane Trader",
    "user_type": "individual"
})
user_data = response.json()

# Login and get JWT token
response = requests.post(f"{API_BASE}/auth/login", json={
    "email": "trader@example.com",
    "password": "SecurePass123!"
})
auth = response.json()
token = auth["access_token"]

# Use token in headers
headers = {"Authorization": f"Bearer {token}"}
```

### Trading Operations

```python
# Get market data
response = requests.get(f"{API_BASE}/market/data", headers=headers)
market_data = response.json()

# Create limit order
order = {
    "order_type": "limit",
    "side": "buy",
    "quantity": 100,
    "price": 25.00,
    "credit_type": "renewable_energy",
    "time_in_force": "GTC"
}
response = requests.post(f"{API_BASE}/trading/orders",
                        json=order, headers=headers)
order_result = response.json()

# Check order status
order_id = order_result["order"]["id"]
response = requests.get(f"{API_BASE}/trading/orders/{order_id}",
                       headers=headers)
status = response.json()

# Cancel order
response = requests.delete(f"{API_BASE}/trading/orders/{order_id}",
                          headers=headers)
```

### Portfolio Management

```python
# Get portfolio summary
response = requests.get(f"{API_BASE}/users/portfolio", headers=headers)
portfolio = response.json()

# Get holdings
holdings = portfolio["holdings"]
for holding in holdings:
    print(f"{holding['credit_type']}: {holding['quantity']} @ ${holding['avg_price']}")

# Retire credits
retire_request = {
    "credit_type": "renewable_energy",
    "quantity": 50,
    "reason": "Corporate carbon neutrality initiative 2024"
}
response = requests.post(f"{API_BASE}/carbon-credits/retire",
                        json=retire_request, headers=headers)
retirement = response.json()
```

## Common Workflows

### Workflow 1: Individual Purchase for Offset

Goal: Purchase carbon credits to offset personal carbon footprint

```bash
# 1. Register and complete KYC (via web interface)

# 2. Check current market prices
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/market/data

# 3. Place market order to buy credits
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_type": "market",
    "side": "buy",
    "quantity": 10,
    "credit_type": "reforestation"
  }' \
  http://localhost:5000/api/trading/orders

# 4. Verify purchase in portfolio
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/users/portfolio

# 5. Retire credits immediately
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "credit_type": "reforestation",
    "quantity": 10,
    "reason": "Personal carbon offset 2024"
  }' \
  http://localhost:5000/api/carbon-credits/retire
```

### Workflow 2: Corporate Bulk Purchase

Goal: Purchase large quantity of credits for compliance

```python
import requests

API_BASE = "http://localhost:5000/api"
headers = {"Authorization": f"Bearer {token}"}

# 1. Calculate required credits based on emissions
annual_emissions_tonnes = 5000
required_credits = annual_emissions_tonnes

# 2. Search for suitable credits
response = requests.get(
    f"{API_BASE}/carbon-credits",
    headers=headers,
    params={
        "credit_type": "renewable_energy",
        "vintage_year": 2024,
        "min_quantity": required_credits,
        "verified": True
    }
)
available_credits = response.json()["credits"]

# 3. Place large limit order
order = {
    "order_type": "limit",
    "side": "buy",
    "quantity": required_credits,
    "price": 26.00,  # Willing to pay up to $26/tCO2e
    "credit_type": "renewable_energy",
    "vintage_year": 2024,
    "time_in_force": "GTD",  # Good till date
    "expires_at": "2024-12-31T23:59:59Z"
}
response = requests.post(f"{API_BASE}/trading/orders",
                        json=order, headers=headers)

# 4. Monitor order execution
order_id = response.json()["order"]["id"]
while True:
    response = requests.get(f"{API_BASE}/trading/orders/{order_id}",
                           headers=headers)
    order_status = response.json()["order"]

    if order_status["status"] in ["filled", "cancelled"]:
        break

    print(f"Order status: {order_status['status']}, "
          f"Filled: {order_status['filled_quantity']}/{order_status['quantity']}")
    time.sleep(60)  # Check every minute

# 5. Generate compliance report
response = requests.get(f"{API_BASE}/compliance/reports/holdings",
                       headers=headers)
report = response.json()
```

### Workflow 3: Credit Issuer Creates New Credits

Goal: Issue new carbon credits from verified project

```python
# 1. Register project (admin approval required)
project = {
    "name": "Solar Farm Delta",
    "type": "renewable_energy",
    "location": "California, USA",
    "description": "500MW solar installation",
    "verification_standard": "Gold Standard",
    "estimated_annual_credits": 100000
}
response = requests.post(f"{API_BASE}/carbon-credits/projects",
                        json=project, headers=headers)
project_id = response.json()["project"]["id"]

# 2. Submit verification documents
files = {
    'verification_report': open('verification.pdf', 'rb'),
    'methodology': open('methodology.pdf', 'rb')
}
response = requests.post(
    f"{API_BASE}/carbon-credits/projects/{project_id}/documents",
    files=files,
    headers=headers
)

# 3. After approval, mint credits (requires MINTER_ROLE)
mint_request = {
    "project_id": project_id,
    "quantity": 50000,
    "vintage_year": 2024,
    "verification_status": "verified"
}
response = requests.post(f"{API_BASE}/carbon-credits/mint",
                        json=mint_request, headers=headers)

# 4. List credits for sale
listing = {
    "credit_id": response.json()["credit"]["id"],
    "quantity": 50000,
    "price": 24.50,
    "min_purchase": 10
}
response = requests.post(f"{API_BASE}/carbon-credits/listings",
                        json=listing, headers=headers)
```

## Trading Operations

### Order Types

**Market Order** - Execute immediately at current market price:

```python
market_order = {
    "order_type": "market",
    "side": "buy",  # or "sell"
    "quantity": 100,
    "credit_type": "renewable_energy"
}
```

**Limit Order** - Execute only at specified price or better:

```python
limit_order = {
    "order_type": "limit",
    "side": "sell",
    "quantity": 200,
    "price": 27.50,
    "credit_type": "reforestation",
    "time_in_force": "GTC"  # Good Till Cancelled
}
```

**Stop-Limit Order** - Trigger limit order when stop price reached:

```python
stop_limit_order = {
    "order_type": "stop_limit",
    "side": "sell",
    "quantity": 150,
    "price": 24.00,  # Limit price
    "stop_price": 25.00,  # Trigger price
    "credit_type": "renewable_energy"
}
```

### Order Management

```bash
# List open orders
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/trading/orders?status=open

# Get specific order
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/trading/orders/{order_id}

# Cancel order
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/trading/orders/{order_id}

# Get trade history
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/trading/trades?user_id=me&limit=50
```

## Portfolio Management

### View and Analyze Portfolio

```python
# Get complete portfolio
response = requests.get(f"{API_BASE}/users/portfolio", headers=headers)
portfolio = response.json()

# Portfolio metrics
total_value = portfolio["total_value"]
cost_basis = portfolio["cost_basis"]
unrealized_pnl = portfolio["unrealized_pnl"]

# Analyze holdings
for holding in portfolio["holdings"]:
    credit_type = holding["credit_type"]
    quantity = holding["quantity"]
    avg_price = holding["average_price"]
    current_price = holding["current_market_price"]
    pnl = holding["unrealized_pnl"]

    print(f"{credit_type}: {quantity} units @ ${avg_price:.2f} "
          f"(Current: ${current_price:.2f}, P&L: ${pnl:.2f})")
```

### Export Portfolio Report

```bash
# Generate PDF report
curl -H "Authorization: Bearer $TOKEN" \
  -o portfolio_report.pdf \
  http://localhost:5000/api/users/portfolio/report?format=pdf

# Generate CSV holdings
curl -H "Authorization: Bearer $TOKEN" \
  -o holdings.csv \
  http://localhost:5000/api/users/portfolio/export?format=csv
```

## Compliance and Reporting

### Generate Compliance Reports

```python
# Holdings report for regulatory filing
response = requests.get(
    f"{API_BASE}/compliance/reports/holdings",
    headers=headers,
    params={
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "format": "pdf"
    }
)

# Save report
with open("compliance_report.pdf", "wb") as f:
    f.write(response.content)

# Transaction history for audit
response = requests.get(
    f"{API_BASE}/compliance/reports/transactions",
    headers=headers,
    params={"year": 2024}
)
transactions = response.json()

# Retirement certificate
response = requests.get(
    f"{API_BASE}/compliance/certificates/{retirement_id}",
    headers=headers
)
```

### KYC and Verification

```python
# Submit KYC documents
files = {
    'id_document': open('passport.pdf', 'rb'),
    'proof_of_address': open('utility_bill.pdf', 'rb')
}
data = {
    'document_type': 'passport',
    'document_number': 'P123456789',
    'country': 'USA'
}
response = requests.post(f"{API_BASE}/users/kyc/submit",
                        files=files, data=data, headers=headers)

# Check KYC status
response = requests.get(f"{API_BASE}/users/kyc/status", headers=headers)
kyc_status = response.json()["status"]  # pending, approved, rejected
```

## Next Steps

- Review [API Reference](API.md) for complete endpoint documentation
- See [Examples](examples/) for more use cases
- Check [Configuration](CONFIGURATION.md) for advanced settings
- Read [Troubleshooting](TROUBLESHOOTING.md) for common issues
