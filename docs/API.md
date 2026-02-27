# API Reference

Complete reference for the CarbonXchange REST API. All endpoints require authentication unless otherwise noted.

## Table of Contents

- [Base URL and Versioning](#base-url-and-versioning)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Authentication](#authentication-endpoints)
  - [User Management](#user-management)
  - [Carbon Credits](#carbon-credits)
  - [Trading](#trading)
  - [Market Data](#market-data)
  - [Compliance](#compliance)
  - [Admin](#admin)

## Base URL and Versioning

| Environment | Base URL                            |
| ----------- | ----------------------------------- |
| Development | `http://localhost:5000/api`         |
| Production  | `https://api.carbonxchange.com/api` |

**Current Version**: 1.0.0

All endpoints are prefixed with `/api`.

## Authentication

CarbonXchange uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

**Token Expiration:**

- Access Token: 15 minutes
- Refresh Token: 7 days

## Rate Limiting

Rate limits are enforced to ensure fair usage:

| Endpoint Type                   | Rate Limit    | Window   |
| ------------------------------- | ------------- | -------- |
| Authentication (login/register) | 5 requests    | 1 minute |
| Trading operations              | 100 requests  | 1 minute |
| Market data                     | 1000 requests | 1 minute |
| General API                     | 1000 requests | 1 hour   |

Rate limit headers in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "status_code": 400
}
```

**Common HTTP Status Codes:**

| Code | Meaning                                 |
| ---- | --------------------------------------- |
| 200  | Success                                 |
| 201  | Created                                 |
| 400  | Bad Request - Invalid input             |
| 401  | Unauthorized - Missing or invalid token |
| 403  | Forbidden - Insufficient permissions    |
| 404  | Not Found                               |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error                   |
| 503  | Service Unavailable                     |

## Endpoints

### Authentication Endpoints

#### POST /api/auth/register

Register a new user account.

**Parameters:**

| Name         | Type   | Required? | Default | Description                                                  | Example            |
| ------------ | ------ | :-------: | :-----: | ------------------------------------------------------------ | ------------------ |
| email        | string |    Yes    |    -    | User email address                                           | "user@example.com" |
| password     | string |    Yes    |    -    | Password (min 8 chars, uppercase, lowercase, number, symbol) | "SecureP@ss123"    |
| full_name    | string |    Yes    |    -    | User's full name                                             | "John Doe"         |
| user_type    | string |    Yes    |    -    | User type: individual, corporate, issuer, admin              | "individual"       |
| company_name | string |    No     |  null   | Company name (required for corporate)                        | "Acme Corp"        |
| phone        | string |    No     |  null   | Phone number                                                 | "+1234567890"      |

**Request Example:**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "password": "SecureP@ss123",
    "full_name": "Jane Trader",
    "user_type": "individual",
    "phone": "+1234567890"
  }'
```

**Response Example (201):**

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "trader@example.com",
    "full_name": "Jane Trader",
    "user_type": "individual",
    "status": "pending_verification",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### POST /api/auth/login

Authenticate user and receive JWT tokens.

**Parameters:**

| Name     | Type   | Required? | Default | Description         | Example            |
| -------- | ------ | :-------: | :-----: | ------------------- | ------------------ |
| email    | string |    Yes    |    -    | User email          | "user@example.com" |
| password | string |    Yes    |    -    | User password       | "SecureP@ss123"    |
| mfa_code | string |    No     |  null   | MFA code if enabled | "123456"           |

**Request Example:**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "password": "SecureP@ss123"
  }'
```

**Response Example (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "trader@example.com",
    "full_name": "Jane Trader",
    "user_type": "individual",
    "is_verified": true,
    "mfa_enabled": false
  }
}
```

#### POST /api/auth/refresh

Refresh access token using refresh token.

**Parameters:**

| Name          | Type   | Required? | Default | Description         | Example                   |
| ------------- | ------ | :-------: | :-----: | ------------------- | ------------------------- |
| refresh_token | string |    Yes    |    -    | Valid refresh token | "eyJhbGciOiJIUzI1NiIs..." |

**Response Example (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### POST /api/auth/logout

Logout user and invalidate tokens.

**Request Example:**

```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer <token>"
```

**Response Example (200):**

```json
{
  "message": "Logged out successfully"
}
```

#### POST /api/auth/mfa/enable

Enable two-factor authentication.

**Response Example (200):**

```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgo...",
  "secret": "JBSWY3DPEHPK3PXP",
  "message": "Scan QR code with authenticator app"
}
```

#### POST /api/auth/mfa/verify

Verify and activate MFA.

**Parameters:**

| Name | Type   | Required? | Default | Description      | Example  |
| ---- | ------ | :-------: | :-----: | ---------------- | -------- |
| code | string |    Yes    |    -    | 6-digit MFA code | "123456" |

### User Management

#### GET /api/users/profile

Get current user profile.

**Request Example:**

```bash
curl -X GET http://localhost:5000/api/users/profile \
  -H "Authorization: Bearer <token>"
```

**Response Example (200):**

```json
{
  "user": {
    "id": 1,
    "email": "trader@example.com",
    "full_name": "Jane Trader",
    "user_type": "individual",
    "status": "active",
    "is_verified": true,
    "kyc_status": "approved",
    "mfa_enabled": true,
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:22:00Z"
  }
}
```

#### PUT /api/users/profile

Update user profile.

**Parameters:**

| Name                     | Type   | Required? | Default | Description           | Example                       |
| ------------------------ | ------ | :-------: | :-----: | --------------------- | ----------------------------- |
| full_name                | string |    No     |    -    | Updated full name     | "Jane Smith"                  |
| phone                    | string |    No     |    -    | Updated phone         | "+1234567890"                 |
| notification_preferences | object |    No     |    -    | Notification settings | {"email": true, "sms": false} |

#### GET /api/users/portfolio

Get user's portfolio summary.

**Request Example:**

```bash
curl -X GET http://localhost:5000/api/users/portfolio \
  -H "Authorization: Bearer <token>"
```

**Response Example (200):**

```json
{
  "portfolio": {
    "total_value": 125000.5,
    "cost_basis": 120000.0,
    "unrealized_pnl": 5000.5,
    "realized_pnl": 2500.0,
    "holdings": [
      {
        "credit_type": "renewable_energy",
        "quantity": 5000,
        "average_price": 24.0,
        "current_market_price": 25.0,
        "unrealized_pnl": 5000.0,
        "percentage_of_portfolio": 100.0
      }
    ],
    "last_updated": "2024-01-20T14:30:00Z"
  }
}
```

#### POST /api/users/kyc/submit

Submit KYC documentation.

**Parameters:**

| Name             | Type   | Required? | Default | Description                                  | Example      |
| ---------------- | ------ | :-------: | :-----: | -------------------------------------------- | ------------ |
| document_type    | string |    Yes    |    -    | Type: passport, drivers_license, national_id | "passport"   |
| document_number  | string |    Yes    |    -    | Document ID number                           | "P123456789" |
| country          | string |    Yes    |    -    | Issuing country code                         | "USA"        |
| id_document      | file   |    Yes    |    -    | Scanned ID document (PDF/image)              | (binary)     |
| proof_of_address | file   |    Yes    |    -    | Utility bill or bank statement               | (binary)     |

### Carbon Credits

#### GET /api/carbon-credits

List available carbon credits.

**Query Parameters:**

| Name         | Type    | Required? | Default | Description                | Example            |
| ------------ | ------- | :-------: | :-----: | -------------------------- | ------------------ |
| page         | integer |    No     |    1    | Page number                | 1                  |
| per_page     | integer |    No     |   50    | Items per page (max 100)   | 50                 |
| credit_type  | string  |    No     |   all   | Filter by type             | "renewable_energy" |
| vintage_year | integer |    No     |   all   | Filter by vintage year     | 2024               |
| verified     | boolean |    No     |   all   | Only verified credits      | true               |
| min_quantity | integer |    No     |    -    | Minimum available quantity | 100                |

**Credit Types:**

- `renewable_energy`
- `reforestation`
- `energy_efficiency`
- `methane_capture`
- `carbon_capture`

**Request Example:**

```bash
curl -X GET "http://localhost:5000/api/carbon-credits?credit_type=renewable_energy&verified=true" \
  -H "Authorization: Bearer <token>"
```

**Response Example (200):**

```json
{
  "credits": [
    {
      "id": 101,
      "credit_type": "renewable_energy",
      "project_name": "Solar Farm Delta",
      "project_id": 42,
      "quantity_available": 50000,
      "price": 25.5,
      "vintage_year": 2024,
      "verification_status": "verified",
      "verification_standard": "Gold Standard",
      "location": "California, USA",
      "created_at": "2024-01-10T00:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 50,
  "pages": 3
}
```

#### GET /api/carbon-credits/{id}

Get detailed information about specific carbon credit.

**Response Example (200):**

```json
{
  "credit": {
    "id": 101,
    "credit_type": "renewable_energy",
    "project_name": "Solar Farm Delta",
    "project_id": 42,
    "quantity_total": 100000,
    "quantity_available": 50000,
    "quantity_retired": 50000,
    "price": 25.5,
    "vintage_year": 2024,
    "verification_status": "verified",
    "verification_standard": "Gold Standard",
    "methodology": "ACM0002",
    "location": "California, USA",
    "project_description": "500MW solar installation generating renewable energy",
    "issuer": {
      "id": 5,
      "name": "Green Energy Co",
      "verified": true
    },
    "documents": [
      {
        "type": "verification_report",
        "url": "/api/files/verification_101.pdf",
        "uploaded_at": "2024-01-10T00:00:00Z"
      }
    ],
    "created_at": "2024-01-10T00:00:00Z"
  }
}
```

#### POST /api/carbon-credits/projects

Create new carbon credit project (Issuer role required).

**Parameters:**

| Name                     | Type    | Required? | Default | Description            | Example            |
| ------------------------ | ------- | :-------: | :-----: | ---------------------- | ------------------ |
| name                     | string  |    Yes    |    -    | Project name           | "Solar Farm Delta" |
| type                     | string  |    Yes    |    -    | Credit type            | "renewable_energy" |
| location                 | string  |    Yes    |    -    | Project location       | "California, USA"  |
| description              | string  |    Yes    |    -    | Detailed description   | "500MW solar..."   |
| verification_standard    | string  |    Yes    |    -    | Standard               | "Gold Standard"    |
| estimated_annual_credits | integer |    Yes    |    -    | Annual credit estimate | 100000             |
| methodology              | string  |    No     |    -    | Methodology code       | "ACM0002"          |

#### POST /api/carbon-credits/retire

Retire carbon credits permanently.

**Parameters:**

| Name        | Type    | Required? |   Default    | Description              | Example                            |
| ----------- | ------- | :-------: | :----------: | ------------------------ | ---------------------------------- |
| credit_type | string  |    Yes    |      -       | Type of credit to retire | "renewable_energy"                 |
| quantity    | integer |    Yes    |      -       | Quantity to retire       | 100                                |
| reason      | string  |    Yes    |      -       | Retirement reason        | "Corporate carbon neutrality 2024" |
| beneficiary | string  |    No     | current_user | On whose behalf          | "Acme Corporation"                 |

**Response Example (200):**

```json
{
  "retirement": {
    "id": 501,
    "user_id": 1,
    "credit_type": "renewable_energy",
    "quantity": 100,
    "reason": "Corporate carbon neutrality 2024",
    "retired_at": "2024-01-20T15:00:00Z",
    "certificate_url": "/api/compliance/certificates/501"
  },
  "message": "Credits retired successfully"
}
```

### Trading

#### POST /api/trading/orders

Create new trading order.

**Parameters:**

| Name          | Type    |  Required?  | Default | Description                           | Example                |
| ------------- | ------- | :---------: | :-----: | ------------------------------------- | ---------------------- |
| order_type    | string  |     Yes     |    -    | Order type: market, limit, stop_limit | "limit"                |
| side          | string  |     Yes     |    -    | Side: buy or sell                     | "buy"                  |
| quantity      | number  |     Yes     |    -    | Quantity in tCO2e                     | 100                    |
| credit_type   | string  |     Yes     |    -    | Type of credit                        | "renewable_energy"     |
| price         | number  | Conditional |    -    | Price (required for limit orders)     | 25.50                  |
| stop_price    | number  |     No      |    -    | Stop price (for stop_limit)           | 24.00                  |
| time_in_force | string  |     No      |  "GTC"  | GTC, GTD, IOC, FOK                    | "GTC"                  |
| vintage_year  | integer |     No      |    -    | Preferred vintage year                | 2024                   |
| project_id    | integer |     No      |    -    | Specific project                      | 42                     |
| expires_at    | string  |     No      |    -    | Expiry datetime (ISO 8601)            | "2024-12-31T23:59:59Z" |
| notes         | string  |     No      |    -    | Order notes                           | "Bulk purchase for Q1" |

**Time in Force Options:**

- `GTC` - Good Till Cancelled
- `GTD` - Good Till Date (requires expires_at)
- `IOC` - Immediate or Cancel
- `FOK` - Fill or Kill

**Request Example:**

```bash
curl -X POST http://localhost:5000/api/trading/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_type": "limit",
    "side": "buy",
    "quantity": 100,
    "credit_type": "renewable_energy",
    "price": 25.00,
    "time_in_force": "GTC"
  }'
```

**Response Example (201):**

```json
{
  "order": {
    "id": 1001,
    "user_id": 1,
    "order_type": "limit",
    "side": "buy",
    "status": "open",
    "quantity": 100,
    "filled_quantity": 0,
    "remaining_quantity": 100,
    "price": 25.0,
    "average_fill_price": null,
    "credit_type": "renewable_energy",
    "time_in_force": "GTC",
    "created_at": "2024-01-20T15:30:00Z",
    "submitted_at": "2024-01-20T15:30:01Z",
    "expires_at": null
  },
  "message": "Order created successfully"
}
```

#### GET /api/trading/orders

List user's orders.

**Query Parameters:**

| Name     | Type    | Required? | Default | Description                              | Example |
| -------- | ------- | :-------: | :-----: | ---------------------------------------- | ------- |
| status   | string  |    No     |   all   | Filter: open, filled, cancelled, expired | "open"  |
| side     | string  |    No     |   all   | Filter: buy, sell                        | "buy"   |
| page     | integer |    No     |    1    | Page number                              | 1       |
| per_page | integer |    No     |   50    | Items per page                           | 50      |

#### GET /api/trading/orders/{order_id}

Get specific order details.

#### DELETE /api/trading/orders/{order_id}

Cancel an open order.

**Response Example (200):**

```json
{
  "message": "Order cancelled successfully",
  "order": {
    "id": 1001,
    "status": "cancelled",
    "cancelled_at": "2024-01-20T16:00:00Z"
  }
}
```

#### GET /api/trading/trades

Get trade execution history.

**Query Parameters:**

| Name       | Type    | Required? | Default | Description           | Example      |
| ---------- | ------- | :-------: | :-----: | --------------------- | ------------ |
| start_date | string  |    No     |    -    | Start date (ISO 8601) | "2024-01-01" |
| end_date   | string  |    No     |    -    | End date (ISO 8601)   | "2024-01-31" |
| page       | integer |    No     |    1    | Page number           | 1            |

**Response Example (200):**

```json
{
  "trades": [
    {
      "id": 5001,
      "order_id": 1001,
      "quantity": 50,
      "price": 25.1,
      "side": "buy",
      "credit_type": "renewable_energy",
      "executed_at": "2024-01-20T15:35:00Z",
      "counterparty_order_id": 1002
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 50
}
```

### Market Data

#### GET /api/market/data

Get current market data and prices.

**Query Parameters:**

| Name        | Type   | Required? | Default | Description           | Example            |
| ----------- | ------ | :-------: | :-----: | --------------------- | ------------------ |
| credit_type | string |    No     |   all   | Filter by credit type | "renewable_energy" |

**Request Example:**

```bash
curl -X GET http://localhost:5000/api/market/data \
  -H "Authorization: Bearer <token>"
```

**Response Example (200):**

```json
{
  "market_data": [
    {
      "credit_type": "renewable_energy",
      "last_price": 25.5,
      "bid_price": 25.4,
      "ask_price": 25.6,
      "volume_24h": 125000,
      "price_change_24h": 0.5,
      "price_change_pct_24h": 2.0,
      "high_24h": 26.0,
      "low_24h": 24.8,
      "total_supply": 5000000,
      "circulating_supply": 3500000,
      "last_updated": "2024-01-20T15:30:00Z"
    }
  ]
}
```

#### GET /api/market/orderbook

Get order book for specific credit type.

**Query Parameters:**

| Name        | Type    | Required? | Default | Description            | Example            |
| ----------- | ------- | :-------: | :-----: | ---------------------- | ------------------ |
| credit_type | string  |    Yes    |    -    | Credit type            | "renewable_energy" |
| depth       | integer |    No     |   20    | Number of price levels | 20                 |

**Response Example (200):**

```json
{
  "orderbook": {
    "credit_type": "renewable_energy",
    "bids": [
      { "price": 25.4, "quantity": 1000 },
      { "price": 25.3, "quantity": 2500 },
      { "price": 25.2, "quantity": 1500 }
    ],
    "asks": [
      { "price": 25.6, "quantity": 800 },
      { "price": 25.7, "quantity": 1200 },
      { "price": 25.8, "quantity": 2000 }
    ],
    "last_updated": "2024-01-20T15:30:00Z"
  }
}
```

#### GET /api/market/history

Get historical price data.

**Query Parameters:**

| Name        | Type   | Required? | Default | Description                       | Example            |
| ----------- | ------ | :-------: | :-----: | --------------------------------- | ------------------ |
| credit_type | string |    Yes    |    -    | Credit type                       | "renewable_energy" |
| interval    | string |    No     |  "1h"   | Interval: 1m, 5m, 15m, 1h, 4h, 1d | "1d"               |
| start_date  | string |    No     | 30d_ago | Start date (ISO 8601)             | "2024-01-01"       |
| end_date    | string |    No     |   now   | End date (ISO 8601)               | "2024-01-31"       |

### Compliance

#### GET /api/compliance/reports/holdings

Generate holdings report for compliance.

**Query Parameters:**

| Name       | Type   | Required? | Default | Description            | Example      |
| ---------- | ------ | :-------: | :-----: | ---------------------- | ------------ |
| start_date | string |    No     |    -    | Report start date      | "2024-01-01" |
| end_date   | string |    No     |   now   | Report end date        | "2024-12-31" |
| format     | string |    No     | "json"  | Format: json, pdf, csv | "pdf"        |

#### GET /api/compliance/reports/transactions

Get transaction history for audit.

#### GET /api/compliance/certificates/{retirement_id}

Get retirement certificate.

**Response Example (200):**

```json
{
  "certificate": {
    "retirement_id": 501,
    "user_name": "Jane Trader",
    "credit_type": "renewable_energy",
    "quantity": 100,
    "project_name": "Solar Farm Delta",
    "vintage_year": 2024,
    "retired_at": "2024-01-20T15:00:00Z",
    "reason": "Corporate carbon neutrality 2024",
    "certificate_number": "CX-RET-501-2024",
    "blockchain_tx": "0x1234567890abcdef...",
    "pdf_url": "/api/compliance/certificates/501/download"
  }
}
```

### Admin

#### GET /api/admin/users

List all users (Admin role required).

#### PUT /api/admin/users/{user_id}/verify

Approve user KYC verification.

#### GET /api/admin/stats

Get platform statistics.

**Response Example (200):**

```json
{
  "stats": {
    "total_users": 1250,
    "active_users": 1100,
    "total_credits_issued": 10000000,
    "total_credits_traded": 5000000,
    "total_credits_retired": 2000000,
    "total_trade_volume": 125000000.0,
    "active_orders": 450,
    "trades_24h": 1200,
    "volume_24h": 30000000.0
  }
}
```

## Health and Info Endpoints

### GET /api/health

Health check endpoint (no authentication required).

**Response Example (200):**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T15:30:00Z",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "api": "healthy"
  }
}
```

### GET /api/info

API information endpoint (no authentication required).

**Response Example (200):**

```json
{
  "name": "CarbonXchange Backend API",
  "version": "1.0.0",
  "description": "Production-ready carbon credit trading platform API",
  "environment": "production",
  "features": [
    "User Management & KYC",
    "Carbon Credit Trading",
    "Portfolio Management",
    "Market Data & Analytics",
    "Compliance & Reporting",
    "Blockchain Integration"
  ],
  "endpoints": {
    "auth": "/api/auth",
    "users": "/api/users",
    "carbon_credits": "/api/carbon-credits",
    "trading": "/api/trading",
    "market": "/api/market",
    "compliance": "/api/compliance",
    "admin": "/api/admin"
  }
}
```

## Python Client Library Example

Here's a complete example using the API as a library:

```python
import requests
from typing import Dict, Any

class CarbonXchangeClient:
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.token = None

    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.token = data["access_token"]
        return data

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def get_market_data(self, credit_type: str = None) -> Dict[str, Any]:
        params = {"credit_type": credit_type} if credit_type else {}
        response = requests.get(
            f"{self.base_url}/market/data",
            headers=self._headers(),
            params=params
        )
        return response.json()

    def create_order(self, order_type: str, side: str, quantity: int,
                    credit_type: str, price: float = None, **kwargs) -> Dict[str, Any]:
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
            f"{self.base_url}/trading/orders",
            headers=self._headers(),
            json=data
        )
        return response.json()

    def get_portfolio(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/users/portfolio",
            headers=self._headers()
        )
        return response.json()

# Usage
client = CarbonXchangeClient()
client.login("trader@example.com", "SecureP@ss123")

# Get market data
market = client.get_market_data("renewable_energy")
print(f"Current price: ${market['market_data'][0]['last_price']}")

# Place order
order = client.create_order(
    order_type="limit",
    side="buy",
    quantity=100,
    credit_type="renewable_energy",
    price=25.00
)
print(f"Order created: {order['order']['id']}")

# Check portfolio
portfolio = client.get_portfolio()
print(f"Portfolio value: ${portfolio['portfolio']['total_value']}")
```

## Next Steps

- Review [Examples](examples/) for more detailed use cases
- Check [CLI Reference](CLI.md) for command-line tools
- See [Configuration](CONFIGURATION.md) for advanced settings
- Read [Troubleshooting](TROUBLESHOOTING.md) for common API issues
