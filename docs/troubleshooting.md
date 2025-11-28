# Troubleshooting Guide

This guide helps developers and users resolve common issues encountered while working with the CarbonXchange platform.

## Table of Contents

1. [Development Environment Issues](#development-environment-issues)
2. [Smart Contract Issues](#smart-contract-issues)
3. [Frontend Issues](#frontend-issues)
4. [Backend Issues](#backend-issues)
5. [Database Issues](#database-issues)
6. [Blockchain Integration Issues](#blockchain-integration-issues)
7. [Performance Issues](#performance-issues)

## Development Environment Issues

### Node.js and npm Issues

#### Error: Node version not compatible

**Problem**: `Error: The engine "node" is incompatible with this module`
**Solution**:

1. Install nvm (Node Version Manager)
2. Run:
    ```bash
    nvm install 14
    nvm use 14
    ```

#### Error: Package installation fails

**Problem**: `npm ERR! code ELIFECYCLE`
**Solution**:

1. Clear npm cache:
    ```bash
    npm cache clean --force
    ```
2. Delete node_modules:
    ```bash
    rm -rf node_modules package-lock.json
    npm install
    ```

### Git Issues

#### Error: Cannot pull latest changes

**Problem**: Local changes conflict with remote changes
**Solution**:

1. Stash local changes:
    ```bash
    git stash
    git pull origin main
    git stash pop
    ```

## Smart Contract Issues

### Compilation Errors

#### Error: Solidity version mismatch

**Problem**: `Error: Source file requires different compiler version`
**Solution**:

1. Update solidity version in hardhat.config.js
2. Install correct solidity version:
    ```bash
    npm install --save-dev @nomiclabs/hardhat-waffle@^version
    ```

### Deployment Issues

#### Error: Insufficient funds

**Problem**: `Error: insufficient funds for gas`
**Solution**:

1. Check wallet balance
2. Get testnet tokens from faucet
3. Adjust gas price in deployment script

### Contract Interaction Issues

#### Error: Transaction reverted

**Problem**: `Error: Transaction has been reverted by the EVM`
**Solution**:

1. Check contract state
2. Verify input parameters
3. Check transaction gas limit
4. Review error message in contract events

## Frontend Issues

### Build Errors

#### Error: TypeScript compilation fails

**Problem**: `TS2307: Cannot find module or its corresponding type declarations`
**Solution**:

1. Install missing type definitions:
    ```bash
    npm install --save-dev @types/missing-module
    ```
2. Check tsconfig.json configuration

### Runtime Errors

#### Error: Web3 not detected

**Problem**: `Error: No Web3 instance injected`
**Solution**:

1. Install MetaMask
2. Connect to correct network
3. Add fallback Web3 provider:
    ```javascript
    if (typeof window.ethereum === 'undefined') {
        web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:8545'));
    }
    ```

## Backend Issues

### API Errors

#### Error: Database connection failed

**Problem**: `Error: Could not connect to database`
**Solution**:

1. Check database credentials
2. Verify database service is running
3. Check network connectivity
4. Review connection string format

### Authentication Issues

#### Error: JWT verification fails

**Problem**: `Error: Invalid token`
**Solution**:

1. Check token expiration
2. Verify secret key configuration
3. Ensure correct token format
4. Review token generation process

## Database Issues

### Connection Issues

#### Error: PostgreSQL connection refused

**Problem**: `Error: ECONNREFUSED 127.0.0.1:5432`
**Solution**:

1. Start PostgreSQL service:
    ```bash
    sudo service postgresql start
    ```
2. Check PostgreSQL configuration
3. Verify port availability

### Migration Issues

#### Error: Migration failed

**Problem**: `Error: Migration failed with error`
**Solution**:

1. Roll back failed migration:
    ```bash
    npx sequelize-cli db:migrate:undo
    ```
2. Fix migration file
3. Re-run migration

## Blockchain Integration Issues

### Network Issues

#### Error: Wrong network

**Problem**: `Error: Connected to wrong network`
**Solution**:

1. Switch to correct network in MetaMask
2. Update network configuration
3. Check network availability

### Transaction Issues

#### Error: Gas estimation failed

**Problem**: `Error: Cannot estimate gas`
**Solution**:

1. Check contract method parameters
2. Verify sufficient funds
3. Adjust gas limit
4. Review contract state

## Performance Issues

### Slow Loading Times

#### Problem: Frontend loads slowly

**Solution**:

1. Implement code splitting
2. Optimize bundle size
3. Use lazy loading
4. Implement caching

### High Gas Costs

#### Problem: Transactions too expensive

**Solution**:

1. Optimize contract code
2. Batch transactions
3. Use gas price oracle
4. Implement Layer 2 solutions

## Common Error Codes

### HTTP Status Codes

- `400`: Bad Request - Check input parameters
- `401`: Unauthorized - Check authentication
- `403`: Forbidden - Check permissions
- `404`: Not Found - Check resource exists
- `500`: Server Error - Check server logs

### Smart Contract Error Codes

- `INSUFFICIENT_BALANCE`
- `INVALID_SIGNATURE`
- `UNAUTHORIZED_ACCESS`
- `INVALID_STATE`

## Debugging Tools

### Frontend Debugging

- Chrome DevTools
- React Developer Tools
- Redux DevTools
- Web3 Inspector

### Backend Debugging

- Postman
- Morgan logging
- Debug npm package
- PM2 logs

### Smart Contract Debugging

- Hardhat console
- Etherscan
- Tenderly
- Remix debugger

## Logging

### Enable Debug Logs

```bash
# Frontend
localStorage.debug = '*'

# Backend
DEBUG=app:* npm start

# Smart Contracts
npx hardhat console --verbose
```
