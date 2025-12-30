# Contributing to CarbonXchange

Thank you for your interest in contributing to CarbonXchange!

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Updating Documentation](#updating-documentation)

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/abrar2030/CarbonXchange.git`
3. Add upstream remote: `git remote add upstream https://github.com/abrar2030/CarbonXchange.git`
4. Set up development environment: `./scripts/dev_env/cx_setup_env.sh`

## Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Keep your branch up to date
git fetch upstream
git rebase upstream/main

# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

## Code Style

### Python (Backend)

- Follow PEP 8 style guide
- Use Black formatter: `black code/backend/`
- Run linter: `flake8 code/backend/`
- Type hints for function signatures
- Docstrings for all public functions

```python
def create_order(
    user_id: int,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal] = None
) -> Order:
    """
    Create a new trading order.

    Args:
        user_id: ID of the user creating the order
        order_type: Type of order (market, limit, stop_limit)
        quantity: Order quantity in tCO2e
        price: Order price (required for limit orders)

    Returns:
        Created Order object

    Raises:
        ValueError: If parameters are invalid
    """
    # Implementation
```

### JavaScript/TypeScript (Frontend)

- Use ESLint configuration
- Prettier for formatting
- TypeScript for type safety
- React functional components with hooks

### Solidity (Smart Contracts)

- Follow Solidity style guide
- Use solhint: `npx solhint 'contracts/**/*.sol'`
- Comprehensive NatSpec comments
- OpenZeppelin contracts for standards

## Testing

### Run All Tests

```bash
./scripts/testing/cx_test_runner.sh --all --coverage
```

### Backend Tests

```bash
cd code/backend
pytest tests/ -v --cov=src
```

### Frontend Tests

```bash
cd web-frontend
npm test
```

### Smart Contract Tests

```bash
cd code/blockchain
npx truffle test
```

### Writing Tests

- Write tests for all new features
- Maintain or improve test coverage (target: >80%)
- Include unit tests, integration tests, and edge cases

Example test:

```python
def test_create_order(client, auth_headers):
    """Test order creation endpoint."""
    response = client.post(
        '/api/trading/orders',
        json={
            'order_type': 'limit',
            'side': 'buy',
            'quantity': 100,
            'price': 25.00,
            'credit_type': 'renewable_energy'
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json
    assert data['order']['status'] == 'open'
    assert data['order']['quantity'] == 100
```

## Pull Request Process

1. **Create PR** with clear title and description
2. **Link related issues** using "Fixes #issue_number"
3. **Ensure CI passes** (all tests, linting)
4. **Request review** from maintainers
5. **Address feedback** and update PR
6. **Squash commits** if requested
7. **Maintainer merges** after approval

### PR Title Format

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Examples:

- `feat: add stop-limit order support`
- `fix: correct portfolio P&L calculation`
- `docs: update API reference for trading endpoints`

## Updating Documentation

When adding or modifying features, update relevant documentation:

1. **API Reference** (`docs/API.md`) - For new endpoints
2. **Feature Matrix** (`docs/FEATURE_MATRIX.md`) - For new features
3. **Configuration** (`docs/CONFIGURATION.md`) - For new config options
4. **Examples** (`docs/examples/`) - Add usage examples
5. **Architecture** (`docs/ARCHITECTURE.md`) - For architectural changes

### Documentation Standards

- Clear, concise language
- Code examples that work
- Tables for structured information
- Links to related documentation
- Keep TOC updated

## Code Review Checklist

Before submitting PR, verify:

- [ ] Code follows project style guide
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No hardcoded secrets or credentials
- [ ] Error handling implemented
- [ ] Logging added for important operations
- [ ] Performance considered
- [ ] Security implications reviewed
- [ ] Backward compatibility maintained (if applicable)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
