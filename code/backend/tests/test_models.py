import pytest
from flask_sqlalchemy import SQLAlchemy
from app import app # Assuming your Flask app instance is here
from models import db, User # Assuming your db instance and User model are here

# Configure the app for testing
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["TESTING"] = True

@pytest.fixture
def client():
    with app.app_context():
        db.create_all()
        yield app.test_client() # create a test client
        db.drop_all()

@pytest.fixture
def init_database():
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

def test_user_model_creation(init_database):
    """Test User model creation and attribute assignment."""
    wallet_addr = "0x1234567890abcdef1234567890abcdef12345678"
    user = User(wallet_address=wallet_addr, credit_balance=150.75)
    db.session.add(user)
    db.session.commit()

    retrieved_user = User.query.filter_by(wallet_address=wallet_addr).first()
    assert retrieved_user is not None
    assert retrieved_user.wallet_address == wallet_addr
    assert float(retrieved_user.credit_balance) == 150.75
    assert retrieved_user.id is not None

def test_user_model_unique_wallet_address(init_database):
    """Test that wallet_address must be unique."""
    wallet_addr = "0xabc123def456abc123def456abc123def456abc1"
    user1 = User(wallet_address=wallet_addr, credit_balance=100)
    db.session.add(user1)
    db.session.commit()

    user2 = User(wallet_address=wallet_addr, credit_balance=200)
    db.session.add(user2)
    with pytest.raises(Exception) as excinfo: # SQLAlchemy raises IntegrityError, caught as general Exception
        db.session.commit()
    assert "UNIQUE constraint failed" in str(excinfo.value).lower() or "duplicate key value violates unique constraint" in str(excinfo.value).lower()
    db.session.rollback() # Rollback the failed transaction

def test_user_model_credit_balance_type(init_database):
    """Test the data type of credit_balance."""
    user = User(wallet_address="0xdef", credit_balance=123.45)
    db.session.add(user)
    db.session.commit()
    retrieved_user = User.query.first()
    assert isinstance(retrieved_user.credit_balance, type(db.Numeric(18,2).type.python_type(1.0))) # Check against python type for Numeric

# Add more tests for any custom methods or specific validations in the User model

