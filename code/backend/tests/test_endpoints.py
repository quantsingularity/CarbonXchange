import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_forecast_endpoint(client):
    response = client.post('/api/forecast', json={
        'historical_price': 45.6,
        'trading_volume': 10000,
        'season': 3
    })
    assert response.status_code == 200
    assert 'forecast' in response.json