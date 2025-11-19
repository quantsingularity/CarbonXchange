# Getting Started with CarbonXchange

This guide will help you set up and start developing with the CarbonXchange platform.

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v14 or higher)
- npm (v6 or higher)
- Git
- PostgreSQL (v13 or higher)
- MetaMask or similar Web3 wallet
- Python 3.8+ (for AI/ML components)

## Development Environment Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/abrar2030/CarbonExchange.git
   cd CarbonExchange
   ```

2. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Update the environment variables with your local settings
   ```bash
   cp .env.example .env
   ```

3. **Install Dependencies**
   ```bash
   # Backend dependencies
   cd backend
   npm install

   # Frontend dependencies
   cd ../frontend
   npm install

   # AI/ML dependencies
   cd ../ml
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # Create database
   psql -U postgres
   CREATE DATABASE carbonxchange;
   ```

5. **Smart Contract Deployment**
   ```bash
   cd ../blockchain
   npm install
   npx hardhat compile
   npx hardhat deploy --network localhost
   ```

## Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   npm run dev
   ```

2. **Start the Frontend Application**
   ```bash
   cd frontend
   npm start
   ```

3. **Run AI/ML Services**
   ```bash
   cd ml
   python app.py
   ```

## Development Workflow

1. Create a new branch for your feature
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

3. Push your changes and create a pull request
   ```bash
   git push origin feature/your-feature-name
   ```

## Testing

- Run backend tests: `cd backend && npm test`
- Run frontend tests: `cd frontend && npm test`
- Run smart contract tests: `cd blockchain && npx hardhat test`

## Common Issues and Solutions

1. **Smart Contract Deployment Failures**
   - Ensure you have sufficient test ETH in your wallet
   - Check network configuration in `hardhat.config.js`

2. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`

3. **Frontend Build Errors**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

## Additional Resources

- [Project Documentation](./documentation.md)
- [API Reference](./api-reference.md)
- [Smart Contract Documentation](./smart-contracts.md)
- [Contributing Guidelines](./contributing.md)

## Need Help?

- Check our [Troubleshooting Guide](./troubleshooting.md)
- Open an issue on GitHub
- Contact the development team
