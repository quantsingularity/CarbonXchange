# CarbonXchange Backend - Production-Ready Carbon Credit Trading Platform

## Overview

CarbonXchange Backend is a production-ready, enterprise-grade API platform for carbon credit trading that meets financial industry standards. Built with Flask and designed for scalability, security, and regulatory compliance, this backend provides comprehensive functionality for carbon credit management, trading operations, user management with KYC compliance, and regulatory reporting.

## Key Features

### Enterprise Security

- JWT-based authentication with refresh token rotation
- Role-based access control (RBAC) with fine-grained permissions
- Multi-factor authentication support
- Comprehensive audit logging for financial compliance
- Rate limiting and DDoS protection
- Input validation and sanitization
- Encryption for sensitive data at rest and in transit

### User Management & KYC

- Complete user lifecycle management
- Know Your Customer (KYC) verification workflow
- Politically Exposed Person (PEP) and sanctions screening
- Document management for compliance
- Risk assessment and scoring
- Account status management and controls

### Carbon Credit Management

- Comprehensive carbon project tracking
- Credit issuance, verification, and certification
- Multiple carbon standards support (VCS, CDM, Gold Standard, etc.)
- Project lifecycle management from development to completion
- Certificate management and validation
- Blockchain integration for tokenization

### Trading Engine

- Order management system (market, limit, stop orders)
- Trade execution and settlement
- Portfolio management and tracking
- Real-time position monitoring
- Profit/loss calculations and reporting
- Risk management and position limits

### Market Data & Analytics

- Real-time market data processing
- Historical price data and OHLCV charts
- Technical indicators and analytics
- Market depth and liquidity metrics
- Price discovery and index calculations
- Volatility and risk metrics

### Compliance & Reporting

- Regulatory framework compliance (SOX, MiFID II, GDPR, etc.)
- Automated compliance monitoring
- Regulatory reporting and filing
- Audit trail maintenance
- Anti-Money Laundering (AML) checks
- Transaction monitoring and alerts

### Scalability & Performance

- Redis-based caching for high performance
- Database query optimization
- Connection pooling and resource management
- Background task processing with Celery
- Horizontal scaling support
- Performance monitoring and metrics

## Architecture

### System Architecture

The CarbonXchange Backend follows a layered architecture pattern designed for financial services:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │    CORS     │ │Rate Limiting│ │   Security  │          │
│  │  Handling   │ │   & DDoS    │ │   Headers   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 Authentication Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │     JWT     │ │    RBAC     │ │     MFA     │          │
│  │   Tokens    │ │Permissions  │ │   Support   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Trading   │ │   Carbon    │ │ Compliance  │          │
│  │   Engine    │ │   Credits   │ │ & Reporting │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ PostgreSQL  │ │    Redis    │ │ Blockchain  │          │
│  │  Database   │ │   Cache     │ │Integration  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

The system uses a comprehensive relational database schema with the following core entities:

- **Users & Authentication**: User accounts, profiles, KYC records
- **Carbon Credits**: Projects, credits, certificates, standards
- **Trading**: Orders, trades, portfolios, holdings
- **Transactions**: Financial transactions, audit logs
- **Market Data**: Real-time prices, historical data, analytics
- **Compliance**: Regulatory records, reports, monitoring

### Security Architecture

Security is implemented at multiple layers:

1. **Network Security**: HTTPS enforcement, security headers
2. **Authentication**: JWT tokens with secure key rotation
3. **Authorization**: Role-based access control with permissions
4. **Data Protection**: Encryption at rest and in transit
5. **Audit Logging**: Comprehensive activity tracking
6. **Input Validation**: Sanitization and validation of all inputs

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- Node.js 18+ (for frontend integration)

### Environment Setup

1. **Clone the repository:**

```bash
git clone <repository-url>
cd carbonxchange_backend
```

2. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Environment Configuration:**
   Create a `.env` file in the root directory:

```env
# Application Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/carbonxchange

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/3

# Blockchain Configuration
WEB3_PROVIDER_URL=https://polygon-mainnet.infura.io/v3/your-project-id
WEB3_PRIVATE_KEY=your-private-key-here
CARBON_TOKEN_CONTRACT_ADDRESS=0x...
MARKETPLACE_CONTRACT_ADDRESS=0x...

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# External Services
SENDGRID_API_KEY=your-sendgrid-api-key
```

5. **Database Setup:**

```bash
# Create database
createdb carbonxchange

# Run migrations
flask db upgrade
```

6. **Start the application:**

```bash
python src/main.py
```

The API will be available at `http://localhost:5000`

## API Documentation

### Authentication Endpoints

#### POST /api/auth/register

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "company_name": "Example Corp"
}
```

**Response:**

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "status": "pending",
    "role": "individual"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer"
}
```

#### POST /api/auth/login

Authenticate user and receive access tokens.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

#### POST /api/auth/refresh

Refresh access token using refresh token.

**Headers:**

```
Authorization: Bearer <refresh_token>
```

#### GET /api/auth/me

Get current user information.

**Headers:**

```
Authorization: Bearer <access_token>
```

### Carbon Credits Endpoints

#### GET /api/carbon-credits/

Get list of available carbon credits.

**Query Parameters:**

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `project_type`: Filter by project type
- `vintage_year`: Filter by vintage year
- `standard`: Filter by carbon standard

#### GET /api/carbon-credits/projects

Get list of carbon projects.

### Trading Endpoints

#### GET /api/trading/orders

Get user's trading orders.

#### POST /api/trading/orders

Create a new trading order.

**Request Body:**

```json
{
  "order_type": "limit",
  "side": "buy",
  "quantity": 100.0,
  "price": 25.5,
  "project_id": 1,
  "vintage_year": 2023
}
```

#### GET /api/trading/portfolio

Get user's portfolio information.

### Market Data Endpoints

#### GET /api/market/data

Get current market data.

#### GET /api/market/prices

Get historical price data.

**Query Parameters:**

- `symbol`: Market symbol
- `timeframe`: Time frame (1m, 5m, 1h, 1d, etc.)
- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)

### Health Check

#### GET /api/health

System health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-08-18T10:30:00Z",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "api": "healthy"
  }
}
```

## Configuration

### Environment Variables

| Variable            | Description                  | Default                    | Required |
| ------------------- | ---------------------------- | -------------------------- | -------- |
| `FLASK_ENV`         | Application environment      | `development`              | No       |
| `SECRET_KEY`        | Flask secret key             | Generated                  | Yes      |
| `JWT_SECRET_KEY`    | JWT signing key              | Generated                  | Yes      |
| `DATABASE_URL`      | PostgreSQL connection string | -                          | Yes      |
| `REDIS_URL`         | Redis connection string      | `redis://localhost:6379/0` | No       |
| `WEB3_PROVIDER_URL` | Blockchain provider URL      | -                          | Yes      |
| `MAIL_SERVER`       | SMTP server                  | `localhost`                | No       |
| `SENDGRID_API_KEY`  | SendGrid API key             | -                          | No       |

### Security Configuration

The application implements multiple security layers:

- **HTTPS Enforcement**: All production traffic must use HTTPS
- **Security Headers**: Comprehensive security headers applied to all responses
- **Rate Limiting**: Configurable rate limits per endpoint
- **Input Validation**: All inputs validated and sanitized
- **SQL Injection Protection**: Parameterized queries and ORM usage
- **XSS Protection**: Content Security Policy and output encoding

### Database Configuration

The system uses PostgreSQL with the following optimizations:

- **Connection Pooling**: Configured for high concurrency
- **Query Optimization**: Proper indexing and query planning
- **Backup Strategy**: Automated backups with point-in-time recovery
- **Monitoring**: Query performance monitoring and alerting
