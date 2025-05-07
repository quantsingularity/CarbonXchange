import pytest
import json
from app import app # Assuming your Flask app instance is here
from models import db, User # Assuming your db instance and User model are here

# Configure the app for testing
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" # Use in-memory SQLite for tests
app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False # Disable CSRF for testing forms if any

@pytest.fixture
def client():
    with app.app_context():
        db.create_all() # Create tables based on models
        yield app.test_client()
        db.session.remove()
        db.drop_all() # Drop tables after tests

# --- Test /api/forecast --- #
def test_forecast_endpoint_success(client):
    """Test the forecast endpoint with valid data."""
    response = client.post("/api/forecast", json={
        "historical_price": 45.6,
        "trading_volume": 10000,
        "season": 3
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "forecast" in data
    assert isinstance(data["forecast"], float) # Assuming forecast is a float

def test_forecast_endpoint_missing_fields(client):
    """Test the forecast endpoint with missing fields."""
    response = client.post("/api/forecast", json={
        "historical_price": 45.6,
        # trading_volume is missing
        "season": 3
    })
    # The current app.py doesn't validate input for forecast, so it might still pass or error differently.
    # Assuming the dummy model or actual model handles missing features gracefully or pandas raises an error.
    # For a robust API, this should ideally return a 400 Bad Request.
    # Given the current app.py, it will likely raise an error during feature processing by pandas.
    # This test might need adjustment based on how the actual model/feature engineering handles this.
    assert response.status_code == 500 # Or 400 if input validation is added

def test_forecast_endpoint_invalid_data_type(client):
    """Test the forecast endpoint with invalid data types."""
    response = client.post("/api/forecast", json={
        "historical_price": "not-a-float",
        "trading_volume": 10000,
        "season": 3
    })
    # Similar to missing fields, current app.py might not have explicit validation.
    # Pandas/model might raise an error.
    assert response.status_code == 500 # Or 400 if input validation is added

# --- Test /api/listings --- #
def test_get_listings_endpoint(client):
    """Test the get_listings endpoint."""
    response = client.get("/api/listings")
    assert response.status_code == 200
    listings = response.get_json()
    assert isinstance(listings, list)
    assert len(listings) > 0 # Based on mock data
    for item in listings:
        assert "id" in item
        assert "seller" in item
        assert "amount" in item
        assert "pricePerToken" in item
        assert "project" in item

# --- Test /api/credit-distribution --- #
def test_get_credit_distribution_endpoint(client):
    """Test the get_credit_distribution endpoint."""
    response = client.get("/api/credit-distribution")
    assert response.status_code == 200
    distribution = response.get_json()
    assert isinstance(distribution, list)
    assert len(distribution) > 0 # Based on mock data
    for item in distribution:
        assert "name" in item
        assert "value" in item

# --- Test /api/user/<wallet_address> --- #
def test_get_user_endpoint_existing_user(client):
    """Test get_user endpoint for an existing (mocked) user."""
    # Note: The current app.py returns mock data and doesn't use the User model for this endpoint.
    # This test reflects the current mock implementation.
    wallet_addr = "0xTestWallet123"
    response = client.get(f"/api/user/{wallet_addr}")
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data["wallet_address"] == wallet_addr
    assert "credit_balance" in user_data
    assert isinstance(user_data["credit_balance"], (int, float))

# If the /api/user endpoint were to interact with the database:
# def test_get_user_endpoint_db_interaction(client):
#     """ Test get_user endpoint assuming it fetches from DB. """
#     wallet_addr = "0xDbUserWallet789"
#     # Add a user to the mock DB first
#     with app.app_context():
#         test_user = User(wallet_address=wallet_addr, credit_balance=500.25)
#         db.session.add(test_user)
#         db.session.commit()

#     response = client.get(f"/api/user/{wallet_addr}")
#     assert response.status_code == 200
#     user_data = response.get_json()
#     assert user_data["wallet_address"] == wallet_addr
#     assert float(user_data["credit_balance"]) == 500.25

#     # Test for a non-existent user
#     response_non_existent = client.get("/api/user/0xNonExistentWallet")
#     assert response_non_existent.status_code == 404 # Assuming it would return 404

# Placeholder for test_integration.py if actual integration scenarios are needed beyond endpoint tests.
# For now, endpoint tests cover basic integration with the Flask app context.

