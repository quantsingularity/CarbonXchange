# Feature Matrix

Complete overview of all CarbonXchange platform features, their implementation status, and module locations.

## Table of Contents

- [Core Features](#core-features)
- [Authentication & User Management](#authentication--user-management)
- [Trading Features](#trading-features)
- [Blockchain Features](#blockchain-features)
- [Compliance Features](#compliance-features)
- [Analytics Features](#analytics-features)
- [Advanced Features](#advanced-features)

## Core Features

| Feature            |             Short description | Module / File                     | CLI flag / API                  | Example (path)                                | Notes                                   |
| ------------------ | ----------------------------: | --------------------------------- | ------------------------------- | --------------------------------------------- | --------------------------------------- |
| User Registration  |      Create new user accounts | `code/backend/src/routes/auth.py` | `POST /api/auth/register`       | [Example 1](examples/01-user-registration.md) | Supports individual and corporate users |
| User Login         |   Authenticate users with JWT | `code/backend/src/routes/auth.py` | `POST /api/auth/login`          | [Example 1](examples/01-user-registration.md) | Returns access and refresh tokens       |
| Token Refresh      | Refresh expired access tokens | `code/backend/src/routes/auth.py` | `POST /api/auth/refresh`        | [Example 1](examples/01-user-registration.md) | Automatic token renewal                 |
| Password Reset     |     Reset forgotten passwords | `code/backend/src/routes/auth.py` | `POST /api/auth/reset-password` | -                                             | Email-based reset                       |
| Profile Management |          Update user profiles | `code/backend/src/routes/user.py` | `PUT /api/users/profile`        | -                                             | Full profile CRUD                       |
| Health Check       |      System health monitoring | `code/backend/src/main.py`        | `GET /api/health`               | -                                             | No auth required                        |

## Authentication & User Management

| Feature               |        Short description | Module / File                                     | CLI flag / API                           | Example (path)                                | Notes                    |
| --------------------- | -----------------------: | ------------------------------------------------- | ---------------------------------------- | --------------------------------------------- | ------------------------ |
| JWT Authentication    |  Secure token-based auth | `code/backend/src/security.py`                    | Headers: `Authorization: Bearer <token>` | All examples                                  | 15min access, 7d refresh |
| Two-Factor Auth (MFA) |           TOTP-based 2FA | `code/backend/src/routes/auth.py`                 | `POST /api/auth/mfa/enable`              | [Example 1](examples/01-user-registration.md) | QR code generation       |
| MFA Verification      |         Verify MFA codes | `code/backend/src/routes/auth.py`                 | `POST /api/auth/mfa/verify`              | [Example 1](examples/01-user-registration.md) | 6-digit TOTP codes       |
| KYC Submission        | Submit verification docs | `code/backend/src/routes/user.py`                 | `POST /api/users/kyc/submit`             | [Example 1](examples/01-user-registration.md) | PDF/image upload         |
| KYC Verification      |   Admin approval process | `code/backend/src/services/kyc_service.py`        | `PUT /api/admin/users/{id}/verify`       | -                                             | Admin only               |
| AML Screening         |     Automated AML checks | `code/backend/src/services/compliance_service.py` | Automatic                                | -                                             | Risk scoring             |
| Role-Based Access     |    Permission management | `code/backend/src/security.py`                    | Decorators: `@admin_required`            | -                                             | Multiple roles supported |
| Session Management    |  Secure session handling | `code/backend/src/config.py`                      | Automatic                                | -                                             | HTTP-only secure cookies |

## Trading Features

| Feature               |        Short description | Module / File                                    | CLI flag / API                               | Example (path)                               | Notes                      |
| --------------------- | -----------------------: | ------------------------------------------------ | -------------------------------------------- | -------------------------------------------- | -------------------------- |
| Market Orders         |      Immediate execution | `code/backend/src/services/trading_service.py`   | `POST /api/trading/orders` (type=market)     | [Example 2](examples/02-basic-trading.md)    | Best available price       |
| Limit Orders          |    Price-specific orders | `code/backend/src/services/trading_service.py`   | `POST /api/trading/orders` (type=limit)      | [Example 2](examples/02-basic-trading.md)    | Execute at price or better |
| Stop-Limit Orders     |       Conditional orders | `code/backend/src/services/trading_service.py`   | `POST /api/trading/orders` (type=stop_limit) | [Example 3](examples/03-advanced-trading.md) | Trigger-based execution    |
| Order Matching Engine | Automatic order matching | `code/backend/src/services/trading_service.py`   | Automatic                                    | -                                            | Price-time priority        |
| Order Cancellation    |       Cancel open orders | `code/backend/src/routes/trading.py`             | `DELETE /api/trading/orders/{id}`            | [Example 2](examples/02-basic-trading.md)    | Only for open orders       |
| Trade History         |        Historical trades | `code/backend/src/routes/trading.py`             | `GET /api/trading/trades`                    | [Example 2](examples/02-basic-trading.md)    | Paginated results          |
| Order Book            |     Real-time order book | `code/backend/src/routes/market.py`              | `GET /api/market/orderbook`                  | -                                            | Bid/ask levels             |
| Portfolio Tracking    |      Real-time portfolio | `code/backend/src/services/portfolio_service.py` | `GET /api/users/portfolio`                   | [Example 2](examples/02-basic-trading.md)    | P&L calculation            |
| Risk Management       |    Pre-trade risk checks | `code/backend/src/services/risk_service.py`      | Automatic                                    | -                                            | Position limits, margin    |
| Time-In-Force         |   Order duration control | `code/backend/src/models/trading.py`             | Order param: `time_in_force`                 | [Example 3](examples/03-advanced-trading.md) | GTC, GTD, IOC, FOK         |

## Blockchain Features

| Feature              |          Short description | Module / File                                             | CLI flag / API      | Example (path) | Notes                     |
| -------------------- | -------------------------: | --------------------------------------------------------- | ------------------- | -------------- | ------------------------- |
| ERC-20 Token         | Carbon credit tokenization | `code/blockchain/contracts/CarbonCreditToken.sol`         | Smart contract      | -              | Standard ERC-20           |
| Advanced Token       |    Enhanced token features | `code/blockchain/contracts/AdvancedCarbonCreditToken.sol` | Smart contract      | -              | Pausable, burnable, roles |
| Token Minting        |          Issue new credits | `code/blockchain/contracts/AdvancedCarbonCreditToken.sol` | `mint()` function   | -              | Requires MINTER_ROLE      |
| Token Burning        |             Retire credits | `code/blockchain/contracts/AdvancedCarbonCreditToken.sol` | `burn()` function   | -              | Permanent retirement      |
| Marketplace Contract |       On-chain marketplace | `code/blockchain/contracts/Marketplace.sol`               | Smart contract      | -              | Buy/sell/list             |
| Advanced Marketplace |       Enhanced marketplace | `code/blockchain/contracts/AdvancedMarketplace.sol`       | Smart contract      | -              | Auctions, escrow          |
| Web3 Integration     |    Blockchain connectivity | `code/backend/src/services/blockchain_service.py`         | Automatic           | -              | Polygon/Ethereum          |
| Transaction Tracking |      On-chain verification | `code/backend/src/services/blockchain_service.py`         | Automatic           | -              | Immutable audit trail     |
| Multi-Sig Governance |             DAO governance | `code/blockchain/contracts/AdvancedCarbonCreditToken.sol` | AccessControl roles | -              | Decentralized control     |
| Gas Optimization     |     Efficient transactions | All contracts                                             | Automatic           | -              | Batching, optimized code  |

## Compliance Features

| Feature                 |         Short description | Module / File                                     | CLI flag / API                             | Example (path)                                | Notes                    |
| ----------------------- | ------------------------: | ------------------------------------------------- | ------------------------------------------ | --------------------------------------------- | ------------------------ |
| KYC Verification        |     Identity verification | `code/backend/src/services/kyc_service.py`        | `POST /api/users/kyc/submit`               | [Example 1](examples/01-user-registration.md) | Document verification    |
| AML Screening           |     Anti-money laundering | `code/backend/src/services/compliance_service.py` | Automatic                                  | -                                             | Risk-based screening     |
| Compliance Reports      |        Regulatory reports | `code/backend/src/routes/compliance.py`           | `GET /api/compliance/reports/holdings`     | -                                             | PDF/CSV export           |
| Audit Logging           | Comprehensive audit trail | `code/backend/src/services/audit_service.py`      | Automatic                                  | -                                             | All user actions logged  |
| Transaction Reports     |     Trade history reports | `code/backend/src/routes/compliance.py`           | `GET /api/compliance/reports/transactions` | -                                             | For audits               |
| Retirement Certificates |   Credit retirement proof | `code/backend/src/routes/compliance.py`           | `GET /api/compliance/certificates/{id}`    | -                                             | PDF certificates         |
| Data Retention          | Automated data management | `code/backend/src/config.py`                      | `DATA_RETENTION_DAYS`                      | -                                             | 7-year default           |
| GDPR Compliance         |              Data privacy | Multiple                                          | Various                                    | -                                             | Right to erasure, export |
| Regulatory Reporting    |       Automated reporting | `code/backend/src/services/compliance_service.py` | Scheduled jobs                             | -                                             | Configurable frequency   |

## Analytics Features

| Feature              |    Short description | Module / File                                                | CLI flag / API             | Example (path)                            | Notes                   |
| -------------------- | -------------------: | ------------------------------------------------------------ | -------------------------- | ----------------------------------------- | ----------------------- |
| Market Data          |    Real-time pricing | `code/backend/src/services/market_data_service.py`           | `GET /api/market/data`     | -                                         | Updated every 60s       |
| Price History        |    Historical charts | `code/backend/src/routes/market.py`                          | `GET /api/market/history`  | -                                         | Multiple timeframes     |
| Portfolio Analytics  |  Performance metrics | `code/backend/src/services/portfolio_service.py`             | `GET /api/users/portfolio` | [Example 2](examples/02-basic-trading.md) | P&L, ROI, allocation    |
| Risk Analytics       |        Risk exposure | `code/backend/src/services/risk_service.py`                  | Automatic                  | -                                         | VaR, concentration risk |
| Volume Metrics       |       Trading volume | `code/backend/src/services/market_data_service.py`           | `GET /api/market/data`     | -                                         | 24h volume              |
| Price Discovery      |       Market pricing | `code/backend/src/services/pricing_service.py`               | Automatic                  | -                                         | VWAP, TWAP              |
| AI Price Forecasting | ML-based predictions | `code/ai_models/training_scripts/train_forecasting_model.py` | Scheduled jobs             | -                                         | TensorFlow models       |
| Dashboard Metrics    |  Platform statistics | `code/backend/src/routes/admin.py`                           | `GET /api/admin/stats`     | -                                         | Admin only              |

## Advanced Features

| Feature               |      Short description | Module / File                                       | CLI flag / API            | Example (path) | Notes                  |
| --------------------- | ---------------------: | --------------------------------------------------- | ------------------------- | -------------- | ---------------------- |
| Rate Limiting         |         API throttling | `code/backend/src/main.py`                          | Automatic (Flask-Limiter) | -              | Redis-backed           |
| Caching               |       Response caching | `code/backend/src/config.py`                        | Redis cache               | -              | Improves performance   |
| Background Tasks      |   Async job processing | Celery integration                                  | Automatic                 | -              | Email, notifications   |
| Email Notifications   |           Email alerts | `code/backend/src/services/notification_service.py` | Automatic                 | -              | SendGrid/SMTP          |
| SMS Notifications     |             SMS alerts | `code/backend/src/services/notification_service.py` | Automatic                 | -              | Twilio                 |
| API Documentation     |    Auto-generated docs | `code/backend/src/main.py`                          | Swagger/OpenAPI           | -              | Interactive docs       |
| Database Migrations   |      Schema versioning | Flask-Migrate                                       | `flask db migrate`        | -              | Alembic-based          |
| Docker Support        |       Containerization | `code/backend/Dockerfile`                           | `docker-compose up`       | -              | Production-ready       |
| Kubernetes Deployment |          Orchestration | `infrastructure/kubernetes/`                        | `kubectl apply`           | -              | Scalable deployment    |
| CI/CD Pipeline        |   Automated deployment | `.github/workflows/cicd.yml`                        | GitHub Actions            | -              | Test, build, deploy    |
| Prometheus Metrics    |             Monitoring | `code/backend/src/config.py`                        | `/metrics` endpoint       | -              | Application metrics    |
| Error Tracking        |     Sentry integration | `code/backend/src/main.py`                          | Automatic                 | -              | Real-time error alerts |
| Internationalization  | Multi-language support | Flask-Babel                                         | Planned                   | -              | Future enhancement     |

## Module Mapping

### Backend Services

| Service              | Primary Responsibility           | Key Files                                           |
| -------------------- | -------------------------------- | --------------------------------------------------- |
| Auth Service         | Authentication and authorization | `code/backend/src/services/auth_service.py`         |
| Trading Service      | Order management and execution   | `code/backend/src/services/trading_service.py`      |
| Portfolio Service    | Portfolio tracking and analytics | `code/backend/src/services/portfolio_service.py`    |
| Compliance Service   | KYC, AML, regulatory compliance  | `code/backend/src/services/compliance_service.py`   |
| Risk Service         | Risk management and checks       | `code/backend/src/services/risk_service.py`         |
| Blockchain Service   | Web3 integration                 | `code/backend/src/services/blockchain_service.py`   |
| Market Data Service  | Real-time market data            | `code/backend/src/services/market_data_service.py`  |
| Audit Service        | Audit logging                    | `code/backend/src/services/audit_service.py`        |
| Notification Service | Email and SMS                    | `code/backend/src/services/notification_service.py` |

### Smart Contracts

| Contract                  | Purpose                            | Network             |
| ------------------------- | ---------------------------------- | ------------------- |
| CarbonCreditToken         | Basic ERC-20 token                 | All networks        |
| AdvancedCarbonCreditToken | Enhanced token with governance     | Production networks |
| Marketplace               | Basic trading marketplace          | All networks        |
| AdvancedMarketplace       | Enhanced marketplace with auctions | Production networks |

### Frontend Components

| Component         | Location                              | Description             |
| ----------------- | ------------------------------------- | ----------------------- |
| Dashboard         | `web-frontend/src/pages/Dashboard.js` | Main user dashboard     |
| Trading Interface | `web-frontend/src/pages/Trading.js`   | Order placement UI      |
| Portfolio View    | `web-frontend/src/pages/Portfolio.js` | Portfolio management    |
| Market Data       | `web-frontend/src/pages/Market.js`    | Live market data charts |

## Next Steps

- Review [API Reference](API.md) for endpoint details
- Check [Examples](examples/) for feature usage
- See [Architecture](ARCHITECTURE.md) for system design
- Read [Contributing](CONTRIBUTING.md) to add new features
