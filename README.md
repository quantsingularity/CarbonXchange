# CarbonXchange

[![CI/CD Status](https://img.shields.io/github/actions/workflow/status/abrar2030/CarbonXchange/ci-cd.yml?branch=main&label=CI/CD&logo=github)](https://github.com/abrar2030/CarbonXchange/actions)
[![Test Coverage](https://img.shields.io/codecov/c/github/abrar2030/CarbonXchange/main?label=Coverage)](https://codecov.io/gh/abrar2030/CarbonXchange)
[![Smart Contract Audit](https://img.shields.io/badge/audit-passing-brightgreen)](https://github.com/abrar2030/CarbonXchange)
[![License](https://img.shields.io/github/license/abrar2030/CarbonXchange)](https://github.com/abrar2030/CarbonXchange/blob/main/LICENSE)

## 🌿 Blockchain-Based Carbon Credit Trading Platform

CarbonXchange is an innovative platform that leverages blockchain technology and artificial intelligence to revolutionize carbon credit trading, making it more transparent, efficient, and accessible for businesses and individuals.

<div align="center">
  <img src="resources/carbonxchange_dashboard.png" alt="CarbonXchange Dashboard" width="80%">
</div>

> **Note**: This project is under active development. Features and functionalities are continuously being enhanced to improve carbon credit trading capabilities and user experience.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Contributing](#contributing)
- [License](#license)

## Overview

CarbonXchange is a decentralized platform that transforms how carbon credits are verified, traded, and retired. By combining blockchain's immutability with AI-powered verification, the platform ensures transparency and trust in the carbon offset market while making it accessible to businesses of all sizes and environmentally conscious individuals.

## Key Features

### Blockchain-Based Carbon Credit Tokenization
- **Transparent Verification**: Immutable record of carbon credit origin and lifecycle
- **Fractional Ownership**: Ability to purchase partial carbon credits
- **Smart Contract Automation**: Automated issuance, trading, and retirement
- **Provenance Tracking**: Complete history of each carbon credit from creation to retirement

### AI-Powered Verification System
- **Project Validation**: Automated assessment of carbon offset projects
- **Satellite Imagery Analysis**: Remote monitoring of reforestation and conservation projects
- **Data Verification**: Cross-referencing multiple data sources for accuracy
- **Fraud Detection**: Identifying suspicious patterns and double-counting

### Carbon Credit Marketplace
- **Peer-to-Peer Trading**: Direct transactions between buyers and sellers
- **Auction Mechanism**: Competitive bidding for carbon credits
- **Price Discovery**: Transparent market-based pricing
- **Portfolio Management**: Tools for managing carbon credit investments

### Impact Tracking & Reporting
- **Real-Time Metrics**: Live tracking of carbon offset impact
- **Customizable Reports**: Generate reports for sustainability goals and compliance
- **ESG Integration**: Connect carbon credits to broader ESG initiatives
- **API Access**: Integrate carbon data into corporate sustainability systems

## Technology Stack

### Blockchain & Smart Contracts
- **Blockchain**: Ethereum, Polygon
- **Smart Contract Language**: Solidity
- **Development Framework**: Hardhat, Truffle
- **Token Standard**: ERC-1155 (for carbon credit tokens)
- **Oracles**: Chainlink for external data

### Backend
- **Language**: Node.js, TypeScript
- **Framework**: Express, NestJS
- **Database**: PostgreSQL, MongoDB
- **API Documentation**: Swagger
- **Authentication**: JWT, OAuth2

### Frontend
- **Framework**: React with TypeScript
- **State Management**: Redux Toolkit
- **Styling**: Tailwind CSS, Styled Components
- **Web3 Integration**: ethers.js, web3.js
- **Data Visualization**: D3.js, Recharts

### AI & Machine Learning
- **Languages**: Python, TensorFlow
- **Computer Vision**: For satellite imagery analysis
- **Natural Language Processing**: For document verification
- **Data Processing**: Pandas, NumPy
- **Model Deployment**: TensorFlow Serving

### DevOps
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Infrastructure as Code**: Terraform

## Architecture

The CarbonXchange platform follows a microservices architecture with these key components:

```
CarbonXchange/
├── Blockchain Layer
│   ├── Carbon Credit Token Contracts
│   ├── Marketplace Contracts
│   ├── Verification Registry
│   └── Governance Contracts
├── AI Verification Layer
│   ├── Project Validation Service
│   ├── Satellite Imagery Analysis
│   ├── Document Processing
│   └── Fraud Detection System
├── Marketplace Layer
│   ├── Order Matching Engine
│   ├── Auction System
│   ├── Price Discovery Mechanism
│   └── Portfolio Management
├── Analytics Layer
│   ├── Impact Calculation
│   ├── Reporting Engine
│   ├── Data Visualization
│   └── ESG Integration
└── API Gateway
    ├── Authentication & Authorization
    ├── Rate Limiting
    ├── Request Routing
    └── External Integrations
```

## Installation and Setup

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- Docker and Docker Compose
- Ethereum wallet (MetaMask recommended)

### Quick Start with Setup Script
```bash
# Clone the repository
git clone https://github.com/abrar2030/CarbonXchange.git
cd CarbonXchange

# Run the setup script
./setup_carbonxchange_env.sh

# Start the application
./run_carbonxchange.sh
```

### Manual Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/abrar2030/CarbonXchange.git
cd CarbonXchange
```

2. Install dependencies:
```bash
# Backend dependencies
cd code/backend
npm install

# Frontend dependencies
cd ../web-frontend
npm install

# AI service dependencies
cd ../ai-service
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development environment:
```bash
docker-compose up -d
```

5. Deploy smart contracts to local blockchain:
```bash
cd code/blockchain
npx hardhat run scripts/deploy.js --network localhost
```

## Usage

### User Registration and Onboarding

1. Create an account on the platform
   - Sign up with email or social login
   - Complete profile information
   - Accept terms and conditions

2. Complete KYC verification
   - Upload identification documents
   - Verify email and phone number
   - Wait for approval (typically within 24 hours)

3. Connect your Ethereum wallet
   - Install MetaMask or compatible wallet
   - Connect wallet to the platform
   - Ensure sufficient funds for gas fees

### For Carbon Credit Suppliers

1. Register your carbon offset project
   - Provide project details and documentation
   - Upload verification certificates
   - Specify project location and impact metrics

2. Submit required documentation
   - Project methodology and standards compliance
   - Baseline calculations and monitoring reports
   - Third-party verification documents

3. Wait for AI verification
   - Automated document analysis
   - Satellite imagery verification (if applicable)
   - Cross-reference with external databases

4. Once approved, your carbon credits will be tokenized and available for sale
   - Set pricing strategy
   - Choose between direct sale or auction
   - Monitor sales and analytics

### For Carbon Credit Buyers

1. Browse available carbon credits
   - Filter by project type, location, and certification
   - View detailed project information and impact metrics
   - Compare prices and quality

2. Purchase credits directly or place bids
   - Buy now at listed price
   - Place bids in auctions
   - Set up recurring purchases

3. View your portfolio and impact metrics
   - Track owned carbon credits
   - Monitor environmental impact
   - Generate certificates for compliance

### Analytics and Reporting

1. Access the dashboard for market insights
   - Price trends and market volume
   - Supply and demand analytics
   - Project performance metrics

2. Generate reports for compliance and sustainability goals
   - Customizable report templates
   - Export in multiple formats (PDF, CSV, Excel)
   - Automated scheduled reporting

3. Track your environmental impact
   - Carbon footprint reduction metrics
   - Contribution to UN Sustainable Development Goals
   - Comparative analysis with industry benchmarks

## Testing

The project includes comprehensive testing to ensure reliability and security:

### Smart Contract Testing
- Unit tests for contract functions
- Integration tests for contract interactions
- Security audits with tools like Slither and MythX
- Gas optimization analysis

### AI Model Testing
- Model validation with test datasets
- Performance metrics evaluation
- Bias and fairness testing
- Edge case handling

### Backend Testing
- API endpoint tests
- Database integration tests
- Authentication and authorization tests
- Performance and load testing

### Frontend Testing
- Component tests with React Testing Library
- End-to-end tests with Cypress
- User experience testing
- Cross-browser compatibility

To run tests:
```bash
# Smart contract tests
cd code/blockchain
npx hardhat test

# AI model tests
cd code/ai-service
pytest

# Backend tests
cd code/backend
npm test

# Frontend tests
cd web-frontend
npm test

# Run all tests
./run_all_tests.sh
```

## CI/CD Pipeline

CarbonXchange uses GitHub Actions for continuous integration and deployment:

### Continuous Integration
- Automated testing on each pull request and push to main
- Code quality checks with ESLint, Prettier, and Pylint
- Test coverage reporting
- Security scanning for vulnerabilities
- Smart contract verification

### Continuous Deployment
- Automated deployment to staging environment on merge to main
- Manual promotion to production after approval
- Smart contract verification on Etherscan
- Infrastructure updates via Terraform
- Database migration management

Current CI/CD Status:
- Build: ![Build Status](https://img.shields.io/github/actions/workflow/status/abrar2030/CarbonXchange/ci-cd.yml?branch=main&label=build)
- Test Coverage: ![Coverage](https://img.shields.io/codecov/c/github/abrar2030/CarbonXchange/main?label=coverage)
- Smart Contract Audit: ![Audit Status](https://img.shields.io/badge/audit-passing-brightgreen)

## Contributing

We welcome contributions to improve CarbonXchange! Here's how you can contribute:

1. **Fork the repository**
   - Create your own copy of the project to work on

2. **Create a feature branch**
   - `git checkout -b feature/amazing-feature`
   - Use descriptive branch names that reflect the changes

3. **Make your changes**
   - Follow the coding standards and guidelines
   - Write clean, maintainable, and tested code
   - Update documentation as needed

4. **Commit your changes**
   - `git commit -m 'Add some amazing feature'`
   - Use clear and descriptive commit messages
   - Reference issue numbers when applicable

5. **Push to branch**
   - `git push origin feature/amazing-feature`

6. **Open Pull Request**
   - Provide a clear description of the changes
   - Link to any relevant issues
   - Respond to review comments and make necessary adjustments

### Development Guidelines
- Follow Solidity best practices for smart contracts
- Use ESLint and Prettier for JavaScript/React code
- Follow PEP 8 style guide for Python code
- Write unit tests for new features
- Update documentation for any changes
- Ensure all tests pass before submitting a pull request
- Keep pull requests focused on a single feature or fix

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
