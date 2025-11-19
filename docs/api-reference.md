# API Reference

This document provides detailed information about the CarbonXchange API endpoints.

## Base URL
```
Development: http://localhost:3000/api/v1
Production: https://api.carbonxchange.com/v1
```

## Authentication

All API requests require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "fullName": "John Doe",
  "walletAddress": "0x..."
}
```

**Response:**
```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "fullName": "John Doe",
    "walletAddress": "0x..."
  }
}
```

#### POST /auth/login
Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** Same as register endpoint

### Carbon Credits

#### GET /credits
List available carbon credits.

**Query Parameters:**
- `page` (optional): Page number for pagination
- `limit` (optional): Items per page
- `type` (optional): Filter by credit type
- `status` (optional): Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "credits": [
      {
        "id": "credit_id",
        "type": "renewable_energy",
        "amount": 100,
        "price": "25.50",
        "status": "available",
        "verificationStatus": "verified",
        "createdAt": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "pages": 10
  }
}
```

#### POST /credits
Create a new carbon credit listing.

**Request Body:**
```json
{
  "type": "renewable_energy",
  "amount": 100,
  "price": "25.50",
  "description": "Solar power project credits",
  "verificationDocuments": ["doc1_url", "doc2_url"]
}
```

### Trading

#### POST /trades
Create a new trade order.

**Request Body:**
```json
{
  "creditId": "credit_id",
  "amount": 50,
  "price": "25.50",
  "type": "buy"
}
```

#### GET /trades/user
Get user's trade history.

**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page
- `status` (optional): Filter by status

### Market Data

#### GET /market/statistics
Get market statistics and analytics.

**Response:**
```json
{
  "success": true,
  "data": {
    "totalVolume": "1000000",
    "24hVolume": "50000",
    "averagePrice": "25.75",
    "priceChange24h": "2.5"
  }
}
```

#### GET /market/forecast
Get AI-powered market forecasts.

**Query Parameters:**
- `timeframe`: "24h" | "7d" | "30d"
- `type`: "price" | "volume" | "demand"

### Wallet

#### GET /wallet/balance
Get user's wallet balance.

**Response:**
```json
{
  "success": true,
  "data": {
    "tokenBalance": "1000.00",
    "creditBalance": "500",
    "pendingTrades": 2
  }
}
```

## Error Handling

All endpoints return error responses in the following format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {} // Optional additional error details
  }
}
```

Common Error Codes:
- `AUTH_REQUIRED`: Authentication required
- `INVALID_INPUT`: Invalid input parameters
- `NOT_FOUND`: Resource not found
- `INSUFFICIENT_FUNDS`: Insufficient funds for transaction
- `VALIDATION_ERROR`: Data validation error

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## Websocket API

Connect to real-time updates using WebSocket:

```
wss://api.carbonxchange.com/ws
```

Available Events:
- `market.update`: Real-time market data updates
- `trade.new`: New trade notifications
- `price.change`: Price change alerts

## SDK Integration

For easy integration, use our official SDK:

```bash
npm install @carbonxchange/sdk
```

Example usage:
```javascript
const CarbonXchange = require('@carbonxchange/sdk');
const client = new CarbonXchange({
  apiKey: 'your_api_key',
  environment: 'production'
});
```
