"""
Test configuration and fixtures for CarbonXchange Backend
"""

import os
import tempfile
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest
from src.main import create_app
from src.models import db
from src.models.carbon_credit import (
    CarbonCredit,
    CarbonProject,
    CreditStatus,
    ProjectStatus,
    ProjectType,
)
from src.models.trading import (
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Portfolio,
    Trade,
)
from src.models.user import KYCStatus, RiskLevel, User, UserKYC, UserProfile, UserStatus


def assert_decimal_equal(a: Decimal, b: Decimal, places: int = 4) -> None:
    """Assert two Decimal values are equal within precision."""
    assert (
        abs(a - b) < Decimal(10) ** -places
    ), f"{a} != {b} (within {places} decimal places)"


@pytest.fixture(scope="session")
def app() -> Any:
    """Create application for testing"""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app("testing")
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY": "test-secret-key-32-chars-minimum!",
            "JWT_SECRET_KEY": "test-jwt-secret-key-32-chars-min!!",
            "WTF_CSRF_ENABLED": False,
            "AUDIT_LOG_ENABLED": True,
        }
    )
    with app.app_context():
        db.create_all()
        yield app
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app: Any) -> Any:
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app: Any) -> Any:
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app: Any) -> Any:
    """Create database session for testing"""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def sample_user(db_session: Any) -> Any:
    """Create sample user for testing"""
    email = f"test_{os.urandom(4).hex()}@example.com"
    user = User(
        email=email,
        password="TestPassword123!",
        first_name="Test",
        last_name="User",
        status=UserStatus.ACTIVE,
        risk_level=RiskLevel.MEDIUM,
    )
    user.email_verified_at = datetime.now(timezone.utc)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_user_profile(db_session: Any, sample_user: Any) -> Any:
    """Create sample user profile"""
    profile = UserProfile(
        user_id=sample_user.id,
        country="USA",
        timezone="UTC",
    )
    db_session.add(profile)
    db_session.commit()
    return profile


@pytest.fixture
def sample_kyc(db_session: Any, sample_user: Any) -> Any:
    """Create sample KYC record"""
    kyc = UserKYC(
        user_id=sample_user.id,
        status=KYCStatus.APPROVED,
        identity_verified=True,
        address_verified=True,
        email_verified=True,
        approved_at=datetime.now(timezone.utc),
    )
    db_session.add(kyc)
    db_session.commit()
    return kyc


@pytest.fixture
def sample_project(db_session: Any) -> Any:
    """Create a sample carbon project"""
    project = CarbonProject(
        name="Test Reforestation Project",
        project_type=ProjectType.REFORESTATION,
        status=ProjectStatus.ACTIVE,
        country="BR",
        description="A test reforestation project",
        total_credits=Decimal("10000"),
        available_credits_count=Decimal("8000"),
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def sample_credit(db_session: Any, sample_project: Any) -> Any:
    """Create a sample carbon credit"""
    credit = CarbonCredit(
        project_id=sample_project.id,
        serial_number=f"CC-TEST-{os.urandom(4).hex().upper()}",
        vintage_year=2023,
        quantity=Decimal("100"),
        status=CreditStatus.AVAILABLE,
        price_per_unit=Decimal("25.00"),
    )
    db_session.add(credit)
    db_session.commit()
    db_session.refresh(credit)
    return credit


@pytest.fixture
def sample_portfolio(db_session: Any, sample_user: Any) -> Any:
    """Create a sample portfolio"""
    from src.models.trading import PortfolioType

    portfolio = Portfolio(
        user_id=sample_user.id,
        name="Test Portfolio",
        portfolio_type=PortfolioType.PERSONAL,
    )
    db_session.add(portfolio)
    db_session.commit()
    db_session.refresh(portfolio)
    return portfolio


@pytest.fixture
def sample_order(db_session: Any, sample_user: Any, sample_project: Any) -> Any:
    """Create a sample open limit buy order for testing"""
    import uuid as uuid_mod

    order = Order(
        order_id=f"ORD-TEST-{uuid_mod.uuid4().hex[:8].upper()}",
        user_id=sample_user.id,
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        status=OrderStatus.OPEN,
        quantity=Decimal("100"),
        remaining_quantity=Decimal("100"),
        filled_quantity=Decimal("0"),
        price=Decimal("45.00"),
        credit_type="VCS",
        vintage_year=2023,
        project_id=sample_project.id,
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_trade(db_session: Any, sample_user: Any, sample_project: Any) -> Any:
    """Create a sample settled trade for testing"""
    import uuid as uuid_mod

    from src.models.trading import TradeStatus

    buy_order = Order(
        order_id=f"ORD-BUY-{uuid_mod.uuid4().hex[:8].upper()}",
        user_id=sample_user.id,
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        status=OrderStatus.FILLED,
        quantity=Decimal("100"),
        remaining_quantity=Decimal("0"),
        filled_quantity=Decimal("100"),
        price=Decimal("45.00"),
        credit_type="VCS",
        vintage_year=2023,
        project_id=sample_project.id,
    )
    sell_order = Order(
        order_id=f"ORD-SELL-{uuid_mod.uuid4().hex[:8].upper()}",
        user_id=sample_user.id,
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL,
        status=OrderStatus.FILLED,
        quantity=Decimal("100"),
        remaining_quantity=Decimal("0"),
        filled_quantity=Decimal("100"),
        price=Decimal("45.00"),
        credit_type="VCS",
        vintage_year=2023,
        project_id=sample_project.id,
    )
    db_session.add(buy_order)
    db_session.add(sell_order)
    db_session.flush()

    trade = Trade(
        buy_order_id=buy_order.id,
        sell_order_id=sell_order.id,
        quantity=Decimal("100"),
        price=Decimal("45.00"),
        vintage_year=2023,
        project_id=sample_project.id,
        status=TradeStatus.SETTLED,
        credit_type="VCS",
    )
    db_session.add(trade)
    db_session.commit()
    db_session.refresh(trade)
    return trade


@pytest.fixture
def mock_audit_service() -> Any:
    """Create a mock audit service"""
    mock = MagicMock()
    mock.log_event.return_value = True
    mock.log_trading_event.return_value = True
    mock.log_authentication.return_value = True
    mock.log_data_access.return_value = True
    mock.log_compliance_event.return_value = True
    return mock


@pytest.fixture
def mock_risk_service() -> Any:
    """Create a mock risk service"""
    mock = MagicMock()
    mock.check_order_risk.return_value = {
        "approved": True,
        "reason": None,
        "risk_checks": [],
        "risk_score": 0.1,
    }
    mock.get_user_risk_profile.return_value = {
        "risk_level": "medium",
        "risk_score": 0.3,
    }
    return mock


@pytest.fixture
def mock_compliance_service() -> Any:
    """Create a mock compliance service"""
    mock = MagicMock()
    mock.check_order_compliance.return_value = {
        "approved": True,
        "reason": None,
        "compliance_checks": [],
    }
    mock.check_user_compliance.return_value = {
        "compliant": True,
        "issues": [],
    }
    return mock


@pytest.fixture
def mock_pricing_service() -> Any:
    """Create a mock pricing service"""
    mock = MagicMock()
    mock.get_current_price.return_value = {
        "price": Decimal("46.75"),
        "pricing_method": "market_based",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    mock.calculate_fair_value.return_value = Decimal("46.75")
    return mock


class PerformanceTimer:
    """Timer utility for performance tests"""

    def __init__(self) -> None:
        self._start: float = 0.0
        self._elapsed: float = 0.0

    def start(self) -> None:
        self._start = time.time()

    def stop(self) -> None:
        self._elapsed = time.time() - self._start

    def assert_under(self, seconds: float) -> None:
        assert (
            self._elapsed < seconds
        ), f"Operation took {self._elapsed:.3f}s, expected under {seconds}s"

    @property
    def elapsed(self) -> float:
        return self._elapsed


@pytest.fixture
def performance_timer() -> Any:
    """Create a performance timer fixture"""
    return PerformanceTimer()


def make_user(db_session: Any, app: Any, **overrides: Any) -> Any:
    """Helper to create a user with defaults"""
    defaults = {
        "email": f"user_{os.urandom(4).hex()}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "status": UserStatus.ACTIVE,
        "risk_level": RiskLevel.MEDIUM,
    }
    defaults.update(overrides)
    with app.app_context():
        user = User(**defaults)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
