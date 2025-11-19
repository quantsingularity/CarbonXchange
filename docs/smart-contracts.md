# Smart Contract Documentation

This document provides detailed information about the smart contracts used in the CarbonXchange platform.

## Contract Architecture

The CarbonXchange platform uses a system of interconnected smart contracts:

1. `CarbonCredit.sol` - ERC-1155 token implementation for carbon credits
2. `CarbonMarketplace.sol` - Main marketplace contract for trading
3. `CarbonVerification.sol` - Handles verification of carbon credits
4. `CarbonGovernance.sol` - DAO governance contract

## Core Contracts

### CarbonCredit.sol

The main token contract implementing ERC-1155 for carbon credit tokens.

```solidity
interface ICarbonCredit {
    function mint(address to, uint256 id, uint256 amount, bytes calldata data) external;
    function burn(address from, uint256 id, uint256 amount) external;
    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes calldata data) external;
}
```

#### Key Functions

- `mint`: Creates new carbon credit tokens
- `burn`: Destroys carbon credit tokens
- `safeTransferFrom`: Transfers tokens between addresses

### CarbonMarketplace.sol

Handles all trading operations and market mechanics.

```solidity
interface ICarbonMarketplace {
    function createSellOrder(uint256 tokenId, uint256 amount, uint256 price) external;
    function createBuyOrder(uint256 tokenId, uint256 amount, uint256 price) external;
    function cancelOrder(uint256 orderId) external;
    function executeOrder(uint256 orderId) external;
}
```

#### Key Functions

- `createSellOrder`: List carbon credits for sale
- `createBuyOrder`: Place buy orders for credits
- `cancelOrder`: Cancel existing orders
- `executeOrder`: Execute trades between matching orders

## Contract Deployment

### Networks

- **Mainnet**: [Contract Addresses](#mainnet-addresses)
- **Testnet**: [Contract Addresses](#testnet-addresses)

### Mainnet Addresses

```
CarbonCredit: 0x...
CarbonMarketplace: 0x...
CarbonVerification: 0x...
CarbonGovernance: 0x...
```

### Testnet Addresses

```
CarbonCredit: 0x...
CarbonMarketplace: 0x...
CarbonVerification: 0x...
CarbonGovernance: 0x...
```

## Contract Interaction

### Using Web3.js

```javascript
const Web3 = require('web3');
const web3 = new Web3('YOUR_PROVIDER_URL');

const marketplace = new web3.eth.Contract(
  MARKETPLACE_ABI,
  MARKETPLACE_ADDRESS
);

// Create sell order
async function createSellOrder(tokenId, amount, price) {
  const tx = await marketplace.methods
    .createSellOrder(tokenId, amount, price)
    .send({ from: userAddress });
  return tx;
}
```

### Using Ethers.js

```javascript
const { ethers } = require('ethers');

const provider = new ethers.providers.JsonRpcProvider('YOUR_PROVIDER_URL');
const signer = provider.getSigner();

const marketplace = new ethers.Contract(
  MARKETPLACE_ADDRESS,
  MARKETPLACE_ABI,
  signer
);

// Create buy order
async function createBuyOrder(tokenId, amount, price) {
  const tx = await marketplace.createBuyOrder(tokenId, amount, price);
  await tx.wait();
  return tx;
}
```

## Security Considerations

### Access Control

- Contracts use OpenZeppelin's `Ownable` and `AccessControl` patterns
- Role-based access control for administrative functions
- Time-locked upgrades for critical changes

### Safety Measures

1. **Reentrancy Protection**
   - All contracts use OpenZeppelin's `ReentrancyGuard`
   - Check-Effects-Interactions pattern implemented

2. **Integer Overflow Protection**
   - SafeMath library used for all mathematical operations
   - Input validation on all public functions

3. **Emergency Controls**
   - Circuit breaker pattern implemented
   - Admin functions for emergency situations

## Events

### CarbonCredit Events

```solidity
event TokenMinted(address indexed to, uint256 indexed tokenId, uint256 amount);
event TokenBurned(address indexed from, uint256 indexed tokenId, uint256 amount);
```

### Marketplace Events

```solidity
event OrderCreated(uint256 indexed orderId, address indexed creator, uint256 amount);
event OrderExecuted(uint256 indexed orderId, address indexed buyer, address indexed seller);
event OrderCancelled(uint256 indexed orderId);
```

## Upgradeability

The contracts use the OpenZeppelin upgrades pattern:

1. **Proxy Pattern**
   - Transparent proxy pattern for upgradeability
   - Admin multisig for upgrade control

2. **Storage Layout**
   - Structured storage pattern
   - Storage gaps for future upgrades

## Gas Optimization

Implemented optimizations:
- Packed storage variables
- Batch operations where possible
- Efficient event emission
- Optimized loops and data structures

## Testing

### Test Coverage

```bash
# Run tests
npx hardhat test

# Generate coverage report
npx hardhat coverage
```

### Key Test Cases

1. Token Operations
   - Minting
   - Burning
   - Transfers

2. Market Operations
   - Order creation
   - Order execution
   - Price mechanics

3. Security
   - Access control
   - Edge cases
   - Attack vectors

## Audits

The smart contracts have been audited by:
1. [Audit Firm 1] - [Date]
2. [Audit Firm 2] - [Date]

[Link to audit reports]

## Development Guidelines

1. **Code Style**
   - Follow Solidity style guide
   - Use explicit visibility modifiers
   - Document all functions with NatSpec

2. **Testing Requirements**
   - 100% test coverage required
   - Integration tests for all features
   - Fuzz testing for critical functions

3. **Deployment Process**
   - Multi-sig requirement for upgrades
   - Timelock for critical changes
   - Testing on testnet first
