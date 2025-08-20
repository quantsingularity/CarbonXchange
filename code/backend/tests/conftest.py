"""
Test configuration and fixtures for CarbonXchange Backend
Provides comprehensive test setup for financial industry-grade testing
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from src import create_app
from src.models import db
from src.models.user import User, UserProfile, UserKYC, UserStatus, KYCStatus, RiskLevel
from src.models.carbon_credit import CarbonProject, CarbonCredit, ProjectType, ProjectStatus, CreditStatus
from src.models.trading import Portfolio, PortfolioHolding, Order, Trade, OrderType, OrderSide, TradeStatus
from src.models.transaction import Transaction, TransactionStatus, TransactionType

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'AUDIT_LOG_ENABLED': True,
        'REDIS_URL': 'redis://localhost:6379/1'  # Test Redis DB
    })
    
    with app.app_context():
        db.create_all()
        yield app
        
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        # Start transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use transaction
        db.session.configure(bind=connection)
        
        yield db.session
        
        # Rollback transaction
        transaction.rollback()
        connection.close()
        db.session.remove()

@pytest.fixture
def sample_user(db_session):
    """Create sample user for testing"""
    user = User(
        email='test@example.com',
        password='TestPassword123!',
        status=UserStatus.ACTIVE,
        risk_level=RiskLevel.MEDIUM
    )
    user.email_verified_at = datetime.utcnow()
    
    db_session.add(user)
    db_session.commit()
    
    return user

@pytest.fixture
def sample_user_profile(db_session, sample_user):
    """Create sample user profile"""
    profile = UserProfile(
        user_id=sample_user.id,
        first_name='John',
        last_name='Doe',
        phone_number='+1234567890',
        country='USA',
        timezone='UTC',
        currency='USD'
    )
    
    db_session.add(profile)
    db_session.commit()
    
    return profile

@pytest.fixture
def sample_kyc(db_session, sample_user):
    """Create sample KYC record"""
    kyc = UserKYC(
        user_id=sample_user.id,
        status=KYCStatus.APPROVED,
        verification_level=2,
        document_type='passport',
        document_number='A12345678',
        document_country='USA',
        approved_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=365)
    )
    
    db_session.add(kyc)
    db_session.commit()
    
    return kyc

@pytest.fixture
def sample_project(db_session):
    """Create sample carbon project"""
    project = CarbonProject(
        name='Test Forestry Project',
        description='A test forestry carbon project',
        project_type=ProjectType.FORESTRY,
        status=ProjectStatus.ACTIVE,
        country='USA',
        state_province='California',
        total_credits=Decimal('100000'),
        available_credits=Decimal('50000'),
        price_per_credit=Decimal('45.00'),
        vintage_year=2023,
        verification_standard='VCS',
        registry_id='VCS-12345'
    )
    
    db_session.add(project)
    db_session.commit()
    
    return project

@pytest.fixture
def sample_carbon_credit(db_session, sample_project):
    """Create sample carbon credit"""
    credit = CarbonCredit(
        project_id=sample_project.id,
        serial_number='VCS-12345-001',
        quantity=Decimal('1000'),
        vintage_year=2023,
        credit_type='VCS',
        status=CreditStatus.AVAILABLE,
        price=Decimal('45.00'),
        currency='USD'
    )
    
    db_session.add(credit)
    db_session.commit()
    
    return credit

@pytest.fixture
def sample_portfolio(db_session, sample_user):
    """Create sample portfolio"""
    portfolio = Portfolio(
        user_id=sample_user.id,
        name='Test Portfolio',
        description='A test portfolio',
        base_currency='USD',
        total_value=Decimal('10000'),
        total_cost=Decimal('9500'),
        is_active=True
    )
    
    db_session.add(portfolio)
    db_session.commit()
    
    return portfolio

@pytest.fixture
def sample_holding(db_session, sample_portfolio, sample_project):
    """Create sample portfolio holding"""
    holding = PortfolioHolding(
        portfolio_id=sample_portfolio.id,
        project_id=sample_project.id,
        credit_type='VCS',
        vintage_year=2023,
        quantity=Decimal('100'),
        average_cost=Decimal('45.00'),
        current_price=Decimal('47.00'),
        total_cost=Decimal('4500'),
        current_value=Decimal('4700'),
        currency='USD'
    )
    
    db_session.add(holding)
    db_session.commit()
    
    return holding

@pytest.fixture
def sample_order(db_session, sample_user, sample_project):
    """Create sample order"""
    order = Order(
        user_id=sample_user.id,
        project_id=sample_project.id,
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=Decimal('50'),
        price=Decimal('45.00'),
        credit_type='VCS',
        vintage_year=2023,
        currency='USD'
    )
    
    db_session.add(order)
    db_session.commit()
    
    return order

@pytest.fixture
def sample_trade(db_session, sample_user, sample_project):
    """Create sample trade"""
    # Create buy and sell orders
    buy_order = Order(
        user_id=sample_user.id,
        project_id=sample_project.id,
        order_type=OrderType.MARKET,
        side=OrderSide.BUY,
        quantity=Decimal('25'),
        price=Decimal('45.00'),
        credit_type='VCS',
        vintage_year=2023,
        currency='USD'
    )
    
    sell_order = Order(
        user_id=sample_user.id,
        project_id=sample_project.id,
        order_type=OrderType.MARKET,
        side=OrderSide.SELL,
        quantity=Decimal('25'),
        price=Decimal('45.00'),
        credit_type='VCS',
        vintage_year=2023,
        currency='USD'
    )
    
    db_session.add_all([buy_order, sell_order])
    db_session.commit()
    
    trade = Trade(
        buy_order_id=buy_order.id,
        sell_order_id=sell_order.id,
        project_id=sample_project.id,
        quantity=Decimal('25'),
        price=Decimal('45.00'),
        total_value=Decimal('1125.00'),
        credit_type='VCS',
        vintage_year=2023,
        currency='USD',
        status=TradeStatus.SETTLED,
        executed_at=datetime.utcnow()
    )
    
    db_session.add(trade)
    db_session.commit()
    
    return trade

@pytest.fixture
def sample_transaction(db_session, sample_user):
    """Create sample transaction"""
    transaction = Transaction(
        user_id=sample_user.id,
        transaction_type=TransactionType.DEPOSIT,
        amount=Decimal('1000.00'),
        currency='USD',
        status=TransactionStatus.COMPLETED,
        description='Test deposit'
    )
    
    db_session.add(transaction)
    db_session.commit()
    
    return transaction

@pytest.fixture
def authenticated_headers(sample_user):
    """Create authentication headers for API testing"""
    # In a real implementation, this would create a JWT token
    return {
        'Authorization': f'Bearer test-token-{sample_user.id}',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def mock_pricing_service():
    """Mock pricing service for testing"""
    with patch('src.services.pricing_service.PricingService') as mock:
        mock_instance = Mock()
        mock_instance.get_current_price.return_value = {
            'price': Decimal('45.00'),
            'pricing_method': 'market_based',
            'timestamp': datetime.utcnow().isoformat()
        }
        mock_instance.calculate_fair_value.return_value = {
            'fair_value': Decimal('46.50'),
            'confidence_score': 0.85
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_risk_service():
    """Mock risk service for testing"""
    with patch('src.services.risk_service.RiskService') as mock:
        mock_instance = Mock()
        mock_instance.check_order_risk.return_value = {
            'approved': True,
            'risk_checks': [],
            'risk_score': 25.0
        }
        mock_instance.get_user_risk_metrics.return_value = {
            'risk_level': 'medium',
            'risk_score': 45.0,
            'var_95': 1250.0
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_compliance_service():
    """Mock compliance service for testing"""
    with patch('src.services.compliance_service.ComplianceService') as mock:
        mock_instance = Mock()
        mock_instance.check_order_compliance.return_value = {
            'approved': True,
            'compliance_checks': [],
            'requires_manual_review': False
        }
        mock_instance.get_user_compliance_status.return_value = {
            'overall_status': 'compliant',
            'compliance_score': 85.0
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_portfolio_service():
    """Mock portfolio service for testing"""
    with patch('src.services.portfolio_service.PortfolioService') as mock:
        mock_instance = Mock()
        mock_instance.get_portfolio_summary.return_value = {
            'portfolio_id': 1,
            'total_value': 10000.0,
            'total_pnl': 500.0,
            'holdings_count': 3
        }
        mock_instance.calculate_portfolio_performance.return_value = {
            'total_return': 5.26,
            'sharpe_ratio': 1.25,
            'max_drawdown': 0.08
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_trading_service():
    """Mock trading service for testing"""
    with patch('src.services.trading_service.TradingService') as mock:
        mock_instance = Mock()
        mock_instance.create_order.return_value = {
            'order_id': 1,
            'status': 'pending',
            'message': 'Order created successfully'
        }
        mock_instance.execute_trade.return_value = {
            'trade_id': 1,
            'status': 'executed',
            'execution_price': 45.00
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_audit_service():
    """Mock audit service for testing"""
    with patch('src.services.audit_service.AuditService') as mock:
        mock_instance = Mock()
        mock_instance.log_event.return_value = Mock(id=1)
        mock_instance.get_user_audit_trail.return_value = []
        mock.return_value = mock_instance
        yield mock_instance

# Test data factories
class UserFactory:
    """Factory for creating test users"""
    
    @staticmethod
    def create_user(db_session, **kwargs):
        """Create a test user with default values"""
        defaults = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'status': UserStatus.ACTIVE,
            'risk_level': RiskLevel.MEDIUM
        }
        defaults.update(kwargs)
        
        user = User(**defaults)
        user.email_verified_at = datetime.utcnow()
        
        db_session.add(user)
        db_session.commit()
        
        return user

class ProjectFactory:
    """Factory for creating test projects"""
    
    @staticmethod
    def create_project(db_session, **kwargs):
        """Create a test project with default values"""
        defaults = {
            'name': 'Test Project',
            'description': 'A test carbon project',
            'project_type': ProjectType.FORESTRY,
            'status': ProjectStatus.ACTIVE,
            'country': 'USA',
            'total_credits': Decimal('100000'),
            'available_credits': Decimal('50000'),
            'price_per_credit': Decimal('45.00'),
            'vintage_year': 2023,
            'verification_standard': 'VCS'
        }
        defaults.update(kwargs)
        
        project = CarbonProject(**defaults)
        
        db_session.add(project)
        db_session.commit()
        
        return project

class OrderFactory:
    """Factory for creating test orders"""
    
    @staticmethod
    def create_order(db_session, user_id, project_id, **kwargs):
        """Create a test order with default values"""
        defaults = {
            'user_id': user_id,
            'project_id': project_id,
            'order_type': OrderType.MARKET,
            'side': OrderSide.BUY,
            'quantity': Decimal('50'),
            'price': Decimal('45.00'),
            'credit_type': 'VCS',
            'vintage_year': 2023,
            'currency': 'USD'
        }
        defaults.update(kwargs)
        
        order = Order(**defaults)
        
        db_session.add(order)
        db_session.commit()
        
        return order

# Test utilities
def assert_decimal_equal(actual, expected, places=2):
    """Assert that two decimal values are equal within specified decimal places"""
    assert abs(actual - expected) < Decimal(10) ** -places, f"Expected {expected}, got {actual}"

def assert_datetime_close(actual, expected, delta_seconds=60):
    """Assert that two datetime values are close within specified seconds"""
    delta = abs((actual - expected).total_seconds())
    assert delta <= delta_seconds, f"Datetime difference {delta}s exceeds {delta_seconds}s"

def create_test_data_set(db_session):
    """Create a comprehensive test data set"""
    # Create users
    users = []
    for i in range(3):
        user = UserFactory.create_user(
            db_session,
            email=f'user{i}@example.com',
            risk_level=RiskLevel.MEDIUM if i % 2 == 0 else RiskLevel.HIGH
        )
        users.append(user)
    
    # Create projects
    projects = []
    project_types = [ProjectType.FORESTRY, ProjectType.RENEWABLE_ENERGY, ProjectType.METHANE_CAPTURE]
    for i, project_type in enumerate(project_types):
        project = ProjectFactory.create_project(
            db_session,
            name=f'Test Project {i+1}',
            project_type=project_type,
            vintage_year=2022 + i
        )
        projects.append(project)
    
    # Create portfolios
    portfolios = []
    for user in users:
        portfolio = Portfolio(
            user_id=user.id,
            name=f'{user.email} Portfolio',
            base_currency='USD',
            is_active=True
        )
        db_session.add(portfolio)
        portfolios.append(portfolio)
    
    db_session.commit()
    
    return {
        'users': users,
        'projects': projects,
        'portfolios': portfolios
    }

# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
        
        def assert_under(self, max_seconds):
            assert self.elapsed < max_seconds, f"Operation took {self.elapsed}s, expected under {max_seconds}s"
    
    return Timer()

# Database testing utilities
@pytest.fixture
def db_query_counter():
    """Count database queries for performance testing"""
    from sqlalchemy import event
    
    class QueryCounter:
        def __init__(self):
            self.count = 0
            self.queries = []
        
        def reset(self):
            self.count = 0
            self.queries = []
        
        def increment(self, conn, cursor, statement, parameters, context, executemany):
            self.count += 1
            self.queries.append({
                'statement': statement,
                'parameters': parameters
            })
    
    counter = QueryCounter()
    
    # Register event listener
    event.listen(db.engine, 'before_cursor_execute', counter.increment)
    
    yield counter
    
    # Remove event listener
    event.remove(db.engine, 'before_cursor_execute', counter.increment)

