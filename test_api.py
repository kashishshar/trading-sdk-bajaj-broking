import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_instruments(client):
    """Test fetching instruments"""
    response = client.get('/api/v1/instruments')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) > 0


def test_place_market_order(client):
    """Test placing a market order"""
    payload = {
        "symbol": "RELIANCE",
        "orderType": "BUY",
        "quantity": 10,
        "orderStyle": "MARKET"
    }
    response = client.post('/api/v1/orders', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['data']['status'] == 'EXECUTED'


def test_place_limit_order(client):
    """Test placing a limit order"""
    payload = {
        "symbol": "TCS",
        "orderType": "BUY",
        "quantity": 5,
        "orderStyle": "LIMIT",
        "price": 3680.00
    }
    response = client.post('/api/v1/orders', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['data']['status'] == 'PLACED'


def test_invalid_order_quantity(client):
    """Test order with invalid quantity"""
    payload = {
        "symbol": "RELIANCE",
        "orderType": "BUY",
        "quantity": 0,
        "orderStyle": "MARKET"
    }
    response = client.post('/api/v1/orders', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'


def test_get_order_status(client):
    """Test fetching order status"""
    # First place an order
    payload = {
        "symbol": "INFY",
        "orderType": "BUY",
        "quantity": 20,
        "orderStyle": "MARKET"
    }
    response = client.post('/api/v1/orders', json=payload)
    order_id = response.get_json()['data']['orderId']
    
    # Then fetch its status
    response = client.get(f'/api/v1/orders/{order_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'


def test_get_trades(client):
    """Test fetching trades"""
    response = client.get('/api/v1/trades')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'


def test_get_portfolio(client):
    """Test fetching portfolio"""
    response = client.get('/api/v1/portfolio')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'