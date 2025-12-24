# CarbonXchange API Documentation

## Overview

The CarbonXchange API provides comprehensive access to carbon credit trading, portfolio management, risk assessment, and compliance features. This RESTful API is designed to meet financial industry standards with robust security, real-time data access, and advanced trading capabilities.

### Base URL

```
Production: https://api.carbonxchange.com/v1
Staging: https://staging-api.carbonxchange.com/v1
Development: http://localhost:8000/api/v1
```

### Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Rate Limiting

API requests are rate-limited to ensure system stability:

- **Standard users**: 1000 requests per hour
- **Premium users**: 5000 requests per hour
- **Institutional users**: 10000 requests per hour

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Response Format

All API responses follow a consistent JSON format:

```json
{
    "success": true,
    "data": {},
    "message": "Operation completed successfully",
    "timestamp": "2023-12-01T10:30:00Z",
    "request_id": "req_123456789"
}
```

Error responses include additional error details:

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request parameters",
        "details": {
            "field": "quantity",
            "reason": "Must be greater than 0"
        }
    },
    "timestamp": "2023-12-01T10:30:00Z",
    "request_id": "req_123456789"
}
```

## Authentication Endpoints

### POST /auth/login

Authenticate user and receive JWT token.

**Request Body:**

```json
{
    "email": "user@example.com",
    "password": "secure_password",
    "mfa_code": "123456"
}
```

**Response:**

```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_in": 3600,
        "token_type": "Bearer",
        "user": {
            "id": 123,
            "email": "user@example.com",
            "role": "trader",
            "kyc_status": "approved"
        }
    }
}
```

### POST /auth/refresh

Refresh JWT token using refresh token.

**Request Body:**

```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### POST /auth/logout

Invalidate current session and tokens.

## User Management Endpoints

### GET /users/profile

Get current user profile information.

**Response:**

```json
{
    "success": true,
    "data": {
        "id": 123,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "trader",
        "kyc_status": "approved",
        "risk_level": "medium",
        "created_at": "2023-01-15T09:00:00Z",
        "last_login": "2023-12-01T10:30:00Z",
        "preferences": {
            "timezone": "UTC",
            "currency": "USD",
            "notifications": {
                "email": true,
                "sms": false,
                "push": true
            }
        }
    }
}
```

### PUT /users/profile

Update user profile information.

**Request Body:**

```json
{
    "first_name": "John",
    "last_name": "Doe",
    "preferences": {
        "timezone": "America/New_York",
        "currency": "USD"
    }
}
```

### GET /users/kyc-status

Get KYC verification status and requirements.

**Response:**

```json
{
    "success": true,
    "data": {
        "status": "pending",
        "level": "tier_2",
        "required_documents": ["government_id", "proof_of_address", "bank_statement"],
        "submitted_documents": [
            {
                "type": "government_id",
                "status": "approved",
                "submitted_at": "2023-11-15T14:30:00Z"
            }
        ],
        "next_steps": ["Submit proof of address", "Submit bank statement"]
    }
}
```

## Trading Endpoints

### GET /trading/orders

Get user's trading orders with filtering and pagination.

**Query Parameters:**

- `status` (optional): Filter by order status (active, filled, cancelled)
- `symbol` (optional): Filter by trading symbol
- `side` (optional): Filter by order side (buy, sell)
- `from_date` (optional): Start date for filtering (ISO 8601)
- `to_date` (optional): End date for filtering (ISO 8601)
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50, max: 200)

**Response:**

```json
{
    "success": true,
    "data": {
        "orders": [
            {
                "id": "ord_123456789",
                "symbol": "CARBON_CREDIT_A",
                "side": "buy",
                "type": "limit",
                "quantity": "1000.00",
                "price": "85.50",
                "filled_quantity": "750.00",
                "remaining_quantity": "250.00",
                "status": "partially_filled",
                "created_at": "2023-12-01T09:00:00Z",
                "updated_at": "2023-12-01T10:15:00Z",
                "expires_at": "2023-12-02T09:00:00Z",
                "execution_strategy": "twap",
                "vintage_year": 2023
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 50,
            "total": 125,
            "pages": 3
        }
    }
}
```

### POST /trading/orders

Place a new trading order.

**Request Body:**

```json
{
    "symbol": "CARBON_CREDIT_A",
    "side": "buy",
    "type": "limit",
    "quantity": "1000.00",
    "price": "85.50",
    "time_in_force": "GTC",
    "execution_strategy": "twap",
    "strategy_params": {
        "duration_minutes": 60,
        "max_participation_rate": 0.1
    },
    "vintage_year": 2023,
    "client_order_id": "my_order_123"
}
```

**Response:**

```json
{
    "success": true,
    "data": {
        "order_id": "ord_123456789",
        "status": "accepted",
        "estimated_execution_time": "2023-12-01T10:00:00Z",
        "child_orders": [
            {
                "id": "ord_123456790",
                "quantity": "100.00",
                "scheduled_time": "2023-12-01T09:05:00Z"
            }
        ]
    }
}
```

### DELETE /trading/orders/{order_id}

Cancel an existing order.

**Response:**

```json
{
    "success": true,
    "data": {
        "order_id": "ord_123456789",
        "status": "cancelled",
        "cancelled_at": "2023-12-01T10:30:00Z",
        "cancelled_quantity": "250.00"
    }
}
```

### GET /trading/executions

Get trade executions for the user.

**Query Parameters:**

- `symbol` (optional): Filter by trading symbol
- `from_date` (optional): Start date for filtering
- `to_date` (optional): End date for filtering
- `page` (optional): Page number
- `limit` (optional): Items per page

**Response:**

```json
{
    "success": true,
    "data": {
        "executions": [
            {
                "id": "exec_123456789",
                "order_id": "ord_123456789",
                "symbol": "CARBON_CREDIT_A",
                "side": "buy",
                "quantity": "100.00",
                "price": "85.45",
                "value": "8545.00",
                "fee": "8.55",
                "executed_at": "2023-12-01T09:15:00Z",
                "counterparty": "market_maker_001",
                "settlement_date": "2023-12-03T09:15:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 50,
            "total": 45,
            "pages": 1
        }
    }
}
```

## Portfolio Management Endpoints

### GET /portfolio/summary

Get portfolio summary and performance metrics.

**Response:**

```json
{
    "success": true,
    "data": {
        "total_value": "125000.00",
        "cash_balance": "25000.00",
        "invested_value": "100000.00",
        "unrealized_pnl": "5000.00",
        "realized_pnl": "2500.00",
        "total_return": "0.075",
        "daily_return": "0.012",
        "positions": [
            {
                "symbol": "CARBON_CREDIT_A",
                "quantity": "1000.00",
                "average_price": "80.00",
                "current_price": "85.50",
                "market_value": "85500.00",
                "unrealized_pnl": "5500.00",
                "weight": "0.684",
                "vintage_year": 2023
            }
        ],
        "performance": {
            "1d": "0.012",
            "1w": "0.045",
            "1m": "0.089",
            "3m": "0.156",
            "1y": "0.234"
        }
    }
}
```

### GET /portfolio/risk-metrics

Get detailed portfolio risk analysis.

**Response:**

```json
{
    "success": true,
    "data": {
        "var_95": "-2500.00",
        "var_99": "-4200.00",
        "expected_shortfall": "-3100.00",
        "max_drawdown": "-0.15",
        "sharpe_ratio": 1.34,
        "beta": 0.87,
        "volatility": 0.128,
        "correlation_matrix": {
            "CARBON_CREDIT_A": {
                "CARBON_CREDIT_B": 0.65,
                "CARBON_CREDIT_C": 0.42
            }
        },
        "risk_attribution": [
            {
                "symbol": "CARBON_CREDIT_A",
                "contribution": "0.45",
                "marginal_var": "-1125.00"
            }
        ],
        "stress_tests": {
            "market_crash": "-15000.00",
            "regulatory_change": "-8000.00",
            "liquidity_crisis": "-12000.00"
        }
    }
}
```

### POST /portfolio/optimize

Optimize portfolio allocation based on risk preferences.

**Request Body:**

```json
{
    "risk_tolerance": "moderate",
    "target_return": 0.12,
    "constraints": {
        "max_position_size": 0.3,
        "min_position_size": 0.05,
        "excluded_assets": ["CARBON_CREDIT_D"]
    },
    "rebalance_threshold": 0.05
}
```

**Response:**

```json
{
    "success": true,
    "data": {
        "recommended_allocation": {
            "CARBON_CREDIT_A": 0.35,
            "CARBON_CREDIT_B": 0.25,
            "CARBON_CREDIT_C": 0.2,
            "CASH": 0.2
        },
        "expected_return": 0.118,
        "expected_volatility": 0.145,
        "sharpe_ratio": 1.28,
        "rebalancing_trades": [
            {
                "symbol": "CARBON_CREDIT_A",
                "action": "sell",
                "quantity": "200.00",
                "current_weight": 0.4,
                "target_weight": 0.35
            }
        ]
    }
}
```

## Market Data Endpoints

### GET /market/symbols

Get list of available trading symbols.

**Response:**

```json
{
    "success": true,
    "data": {
        "symbols": [
            {
                "symbol": "CARBON_CREDIT_A",
                "name": "Renewable Energy Carbon Credits",
                "type": "carbon_credit",
                "vintage_year": 2023,
                "methodology": "VCS",
                "project_location": "Brazil",
                "min_trade_size": "1.00",
                "tick_size": "0.01",
                "trading_hours": {
                    "start": "09:00:00",
                    "end": "17:00:00",
                    "timezone": "UTC"
                },
                "settlement_period": "T+2"
            }
        ]
    }
}
```

### GET /market/quotes/{symbol}

Get real-time quote for a symbol.

**Response:**

```json
{
    "success": true,
    "data": {
        "symbol": "CARBON_CREDIT_A",
        "bid": "85.45",
        "ask": "85.55",
        "last": "85.50",
        "volume": "15000.00",
        "high": "86.20",
        "low": "84.80",
        "open": "85.00",
        "change": "0.50",
        "change_percent": "0.59",
        "timestamp": "2023-12-01T10:30:00Z",
        "market_status": "open"
    }
}
```

### GET /market/depth/{symbol}

Get order book depth for a symbol.

**Query Parameters:**

- `depth` (optional): Number of levels to return (default: 10, max: 50)

**Response:**

```json
{
    "success": true,
    "data": {
        "symbol": "CARBON_CREDIT_A",
        "bids": [
            {
                "price": "85.45",
                "quantity": "500.00",
                "orders": 3
            },
            {
                "price": "85.40",
                "quantity": "750.00",
                "orders": 5
            }
        ],
        "asks": [
            {
                "price": "85.55",
                "quantity": "300.00",
                "orders": 2
            },
            {
                "price": "85.60",
                "quantity": "600.00",
                "orders": 4
            }
        ],
        "timestamp": "2023-12-01T10:30:00Z"
    }
}
```

### GET /market/history/{symbol}

Get historical price data for a symbol.

**Query Parameters:**

- `interval` (required): Time interval (1m, 5m, 15m, 1h, 4h, 1d)
- `from_date` (required): Start date (ISO 8601)
- `to_date` (required): End date (ISO 8601)
- `limit` (optional): Maximum number of data points (default: 1000)

**Response:**

```json
{
    "success": true,
    "data": {
        "symbol": "CARBON_CREDIT_A",
        "interval": "1h",
        "data": [
            {
                "timestamp": "2023-12-01T09:00:00Z",
                "open": "85.00",
                "high": "85.30",
                "low": "84.90",
                "close": "85.20",
                "volume": "1200.00"
            }
        ]
    }
}
```

## Risk Management Endpoints

### GET /risk/limits

Get current risk limits for the user.

**Response:**

```json
{
    "success": true,
    "data": {
        "position_limits": {
            "max_position_value": "50000.00",
            "max_concentration": 0.3,
            "max_leverage": 2.0
        },
        "trading_limits": {
            "daily_volume_limit": "100000.00",
            "daily_trade_count": 50,
            "max_order_size": "10000.00"
        },
        "risk_limits": {
            "max_var_95": "-5000.00",
            "max_drawdown": "-0.20",
            "min_sharpe_ratio": 0.5
        },
        "current_usage": {
            "position_value": "25000.00",
            "daily_volume": "15000.00",
            "daily_trades": 8,
            "current_var_95": "-2500.00"
        }
    }
}
```

### POST /risk/stress-test

Run stress test scenarios on portfolio.

**Request Body:**

```json
{
    "scenarios": [
        {
            "name": "market_crash",
            "shocks": {
                "CARBON_CREDIT_A": -0.3,
                "CARBON_CREDIT_B": -0.25
            }
        },
        {
            "name": "regulatory_change",
            "shocks": {
                "CARBON_CREDIT_A": -0.15,
                "CARBON_CREDIT_B": -0.2
            }
        }
    ]
}
```

**Response:**

```json
{
    "success": true,
    "data": {
        "results": [
            {
                "scenario": "market_crash",
                "portfolio_impact": "-15000.00",
                "percentage_impact": "-0.12",
                "position_impacts": [
                    {
                        "symbol": "CARBON_CREDIT_A",
                        "impact": "-10000.00"
                    }
                ]
            }
        ]
    }
}
```

## Compliance Endpoints

### GET /compliance/status

Get compliance status for the user.

**Response:**

```json
{
    "success": true,
    "data": {
        "overall_status": "compliant",
        "last_check": "2023-12-01T08:00:00Z",
        "next_check": "2023-12-08T08:00:00Z",
        "checks": [
            {
                "type": "kyc_verification",
                "status": "passed",
                "last_updated": "2023-11-15T10:00:00Z"
            },
            {
                "type": "sanctions_screening",
                "status": "passed",
                "last_updated": "2023-12-01T08:00:00Z"
            },
            {
                "type": "pep_screening",
                "status": "passed",
                "last_updated": "2023-12-01T08:00:00Z"
            }
        ],
        "required_actions": [],
        "restrictions": []
    }
}
```

### GET /compliance/reports

Get compliance reports and audit trails.

**Query Parameters:**

- `type` (optional): Report type (trading, kyc, sanctions)
- `from_date` (optional): Start date for filtering
- `to_date` (optional): End date for filtering

**Response:**

```json
{
    "success": true,
    "data": {
        "reports": [
            {
                "id": "rpt_123456789",
                "type": "trading",
                "period": "2023-11",
                "status": "completed",
                "generated_at": "2023-12-01T09:00:00Z",
                "download_url": "https://api.carbonxchange.com/v1/compliance/reports/rpt_123456789/download"
            }
        ]
    }
}
```

## Analytics Endpoints

### GET /analytics/trading-signals/{symbol}

Get AI-generated trading signals for a symbol.

**Query Parameters:**

- `algorithm` (optional): Algorithm type (momentum, mean_reversion, ml_ensemble)
- `timeframe` (optional): Analysis timeframe (1h, 4h, 1d)

**Response:**

```json
{
    "success": true,
    "data": {
        "signals": [
            {
                "symbol": "CARBON_CREDIT_A",
                "signal_type": "buy",
                "strength": 0.75,
                "confidence": 0.82,
                "price_target": "88.00",
                "stop_loss": "82.00",
                "timeframe": "1d",
                "algorithm": "ml_ensemble",
                "generated_at": "2023-12-01T10:30:00Z",
                "expires_at": "2023-12-01T18:30:00Z"
            }
        ]
    }
}
```

### GET /analytics/market-sentiment

Get market sentiment analysis.

**Response:**

```json
{
    "success": true,
    "data": {
        "overall_sentiment": "bullish",
        "sentiment_score": 0.65,
        "confidence": 0.78,
        "factors": [
            {
                "factor": "news_sentiment",
                "score": 0.72,
                "weight": 0.3
            },
            {
                "factor": "technical_indicators",
                "score": 0.58,
                "weight": 0.4
            },
            {
                "factor": "market_flow",
                "score": 0.68,
                "weight": 0.3
            }
        ],
        "updated_at": "2023-12-01T10:30:00Z"
    }
}
```

## WebSocket API

### Connection

Connect to real-time data streams via WebSocket:

```
wss://api.carbonxchange.com/v1/ws
```

### Authentication

Send authentication message after connection:

```json
{
    "type": "auth",
    "token": "your_jwt_token"
}
```

### Subscriptions

#### Market Data

```json
{
    "type": "subscribe",
    "channel": "quotes",
    "symbol": "CARBON_CREDIT_A"
}
```

#### Order Updates

```json
{
    "type": "subscribe",
    "channel": "orders"
}
```

#### Trade Executions

```json
{
    "type": "subscribe",
    "channel": "executions"
}
```

### Message Formats

#### Quote Update

```json
{
    "type": "quote",
    "symbol": "CARBON_CREDIT_A",
    "bid": "85.45",
    "ask": "85.55",
    "last": "85.50",
    "timestamp": "2023-12-01T10:30:00Z"
}
```

#### Order Update

```json
{
    "type": "order_update",
    "order_id": "ord_123456789",
    "status": "filled",
    "filled_quantity": "1000.00",
    "timestamp": "2023-12-01T10:30:00Z"
}
```

## Error Codes

| Code                       | Description                         |
| -------------------------- | ----------------------------------- |
| `AUTHENTICATION_REQUIRED`  | Valid authentication token required |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions     |
| `VALIDATION_ERROR`         | Request validation failed           |
| `RESOURCE_NOT_FOUND`       | Requested resource not found        |
| `RATE_LIMIT_EXCEEDED`      | API rate limit exceeded             |
| `INSUFFICIENT_BALANCE`     | Insufficient account balance        |
| `MARKET_CLOSED`            | Market is currently closed          |
| `ORDER_REJECTED`           | Order rejected by risk management   |
| `COMPLIANCE_CHECK_FAILED`  | User failed compliance check        |
| `SYSTEM_MAINTENANCE`       | System under maintenance            |

## SDKs and Libraries

### Python SDK

```bash
pip install carbonxchange-python
```

```python
from carbonxchange import CarbonXchangeClient

client = CarbonXchangeClient(api_key='your_api_key')
orders = client.trading.get_orders()
```

### JavaScript SDK

```bash
npm install carbonxchange-js
```

```javascript
import CarbonXchange from 'carbonxchange-js';

const client = new CarbonXchange({ apiKey: 'your_api_key' });
const orders = await client.trading.getOrders();
```
