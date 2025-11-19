# Contributing to CarbonXchange

Thank you for your interest in contributing to CarbonXchange! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Process](#development-process)
4. [Pull Request Process](#pull-request-process)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Community](#community)

## Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm (v6 or higher)
- Git
- PostgreSQL (v13 or higher)
- Python 3.8+ (for AI/ML components)

### Setup Steps
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/CarbonXchange.git
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/original/CarbonXchange.git
   ```
4. Install dependencies:
   ```bash
   # Frontend
   cd frontend
   npm install

   # Backend
   cd ../backend
   npm install

   # Smart Contracts
   cd ../blockchain
   npm install
   ```

## Development Process

### 1. Branching Strategy
- `main` - production-ready code
- `develop` - main development branch
- `feature/*` - new features
- `bugfix/*` - bug fixes
- `hotfix/*` - urgent production fixes

### 2. Branch Naming Convention
```
feature/descriptive-feature-name
bugfix/issue-description
hotfix/critical-fix-description
```

### 3. Commit Messages
Follow the conventional commits specification:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Example:
```
feat(trading): implement limit order functionality

- Add limit order smart contract
- Implement order matching engine
- Add API endpoints for limit orders

Closes #123
```

## Pull Request Process

1. **Update Documentation**
   - Update README.md if necessary
   - Add/update API documentation
   - Update architecture diagrams if needed

2. **Testing Requirements**
   - Add/update unit tests
   - Add/update integration tests
   - Ensure all tests pass
   - Maintain or improve code coverage

3. **Code Review Process**
   - At least two approvals required
   - All comments must be resolved
   - CI/CD checks must pass

4. **Merge Requirements**
   - Squash commits into meaningful units
   - Ensure branch is up to date with develop
   - No merge conflicts

## Coding Standards

### JavaScript/TypeScript
- Use ESLint with provided configuration
- Follow Airbnb Style Guide
- Use TypeScript for type safety
- Maximum line length: 100 characters

### Solidity
- Follow Solidity Style Guide
- Use latest stable Solidity version
- Implement natspec documentation
- Use OpenZeppelin contracts when possible

### Python
- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters (black formatter)
- Use pylint for linting

### General Guidelines
- Write self-documenting code
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic

## Testing Guidelines

### Unit Tests
- Test each function independently
- Use mocking for external dependencies
- Aim for 100% code coverage
- Test edge cases and error conditions

### Integration Tests
- Test component interactions
- Test API endpoints
- Test smart contract interactions
- Test database operations

### Smart Contract Tests
- Test all contract functions
- Test access control
- Test error conditions
- Use gas optimization tests

## Documentation

### Code Documentation
- Use JSDoc for JavaScript/TypeScript
- Use NatSpec for Solidity
- Use docstrings for Python
- Document complex algorithms

### API Documentation
- Use OpenAPI/Swagger
- Document all endpoints
- Include request/response examples
- Document error responses

### Architecture Documentation
- Keep diagrams up to date
- Document system interactions
- Document deployment process
- Document configuration options

## Community

### Communication Channels
- GitHub Discussions
- Discord Server
- Development Blog
- Monthly Community Calls

### Getting Help
- Check existing issues
- Ask in Discord
- Join community calls
- Read documentation

### Recognition
- Contributors list in README
- Monthly contributor highlights
- Community awards
- Speaking opportunities

## Additional Resources

### Learning Resources
- Ethereum Development Documentation
- React.js Documentation
- Node.js Best Practices
- Smart Contract Security Best Practices

### Useful Tools
- Hardhat for smart contract development
- Remix IDE for quick testing
- MetaMask for wallet integration
- Etherscan for contract verification

### Security
- Report security issues privately
- Follow responsible disclosure
- Use security tools provided
- Regular security reviews
