# CarbonXchange Documentation

Welcome to the CarbonXchange platform documentation. This comprehensive guide will help you understand, install, configure, and use the blockchain-based carbon credit trading platform.

## Table of Contents

1. [Installation Guide](INSTALLATION.md) - Get started with CarbonXchange
2. [Usage Guide](USAGE.md) - Learn how to use the platform
3. [API Reference](API.md) - Complete API documentation
4. [CLI Reference](CLI.md) - Command-line tools and scripts
5. [Configuration](CONFIGURATION.md) - System configuration options
6. [Feature Matrix](FEATURE_MATRIX.md) - Complete feature overview
7. [Architecture](ARCHITECTURE.md) - System design and architecture
8. [Smart Contracts](SMART_CONTRACTS.md) - Blockchain contract documentation
9. [Examples](examples/) - Practical usage examples
10. [Contributing](CONTRIBUTING.md) - Contribution guidelines
11. [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## Quick Summary

CarbonXchange is a blockchain-based carbon credit trading platform that leverages Ethereum/Polygon smart contracts, AI-powered verification, and modern web technologies to create a transparent, efficient marketplace for carbon credits. The platform enables businesses and individuals to trade, verify, and retire carbon credits with complete auditability and regulatory compliance.

## Quick Start

Get up and running in 3 steps:

```bash
# 1. Clone and enter repository
git clone https://github.com/quantsingularity/CarbonXchange.git
cd CarbonXchange

# 2. Set up environment (automated)
./scripts/dev_env/cx_setup_env.sh

# 3. Start the platform
./scripts/orchestration/cx_run_dev.sh
```

Access the application at `http://localhost:3000` (web) and `http://localhost:5000/api/health` (API).

## Platform Components

- **Backend API** (Python/Flask) - RESTful API with JWT authentication, rate limiting, and comprehensive trading services
- **Web Frontend** (React/TypeScript) - Modern web interface for trading and portfolio management
- **Mobile Frontend** (React Native) - Mobile application for iOS/Android
- **Smart Contracts** (Solidity) - ERC-20 token contracts and marketplace logic on Ethereum/Polygon
- **AI Models** (Python/TensorFlow) - Price forecasting and verification models
- **Infrastructure** (Docker/Kubernetes/Terraform) - Production-ready deployment configuration

## Key Features

- ✅ Blockchain-based carbon credit tokenization (ERC-20)
- ✅ Advanced trading engine with multiple order types (market, limit, stop-limit)
- ✅ Portfolio management and analytics
- ✅ KYC/AML compliance automation
- ✅ Risk management and audit services
- ✅ Real-time market data and pricing
- ✅ Multi-factor authentication (MFA)
- ✅ Regulatory reporting tools
- ✅ AI-powered price forecasting
- ✅ Smart contract automation for issuance, trading, and retirement

## Technology Stack

| Component       | Technology                                         |
| --------------- | -------------------------------------------------- |
| Backend         | Python 3.8+, Flask 3.1, SQLAlchemy, Celery         |
| Frontend        | React 18+, TypeScript, Redux Toolkit, Tailwind CSS |
| Smart Contracts | Solidity ^0.8.0, OpenZeppelin, Truffle             |
| Blockchain      | Ethereum, Polygon                                  |
| Database        | PostgreSQL, Redis                                  |
| AI/ML           | Python, TensorFlow, NumPy, Pandas, scikit-learn    |
| Infrastructure  | Docker, Kubernetes, Terraform, Ansible             |
| CI/CD           | GitHub Actions                                     |
| Monitoring      | Prometheus, Grafana, Sentry                        |
