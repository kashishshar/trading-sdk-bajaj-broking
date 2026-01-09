from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory data storage
instruments_db = [
    {"symbol": "RELIANCE", "exchange": "NSE", "instrumentType": "EQUITY", "lastTradedPrice": 2450.50},
    {"symbol": "TCS", "exchange": "NSE", "instrumentType": "EQUITY", "lastTradedPrice": 3680.25},
    {"symbol": "INFY", "exchange": "NSE", "instrumentType": "EQUITY", "lastTradedPrice": 1542.75},
    {"symbol": "HDFCBANK", "exchange": "NSE", "instrumentType": "EQUITY", "lastTradedPrice": 1625.30},
    {"symbol": "ICICIBANK", "exchange": "NSE", "instrumentType": "EQUITY", "lastTradedPrice": 1089.60}
]

orders_db = {}
trades_db = []
portfolio_db = {}

# Mock authentication (hardcoded user)
MOCK_USER_ID = "user123"


# 1. INSTRUMENT APIs
@app.route('/api/v1/instruments', methods=['GET'])
def get_instruments():
    """Fetch list of tradable instruments"""
    return jsonify({
        "status": "success",
        "data": instruments_db
    }), 200


# 2. ORDER MANAGEMENT APIs
@app.route('/api/v1/orders', methods=['POST'])
def place_order():
    """Place a new order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"status": "error", "message": "Request body is required"}), 400
        
        order_type = data.get('orderType')
        order_style = data.get('orderStyle')
        symbol = data.get('symbol')
        quantity = data.get('quantity')
        price = data.get('price')
        
        # Validations
        if order_type not in ['BUY', 'SELL']:
            return jsonify({"status": "error", "message": "orderType must be BUY or SELL"}), 400
        
        if order_style not in ['MARKET', 'LIMIT']:
            return jsonify({"status": "error", "message": "orderStyle must be MARKET or LIMIT"}), 400
        
        if not symbol:
            return jsonify({"status": "error", "message": "symbol is required"}), 400
        
        if not quantity or quantity <= 0:
            return jsonify({"status": "error", "message": "quantity must be greater than 0"}), 400
        
        if order_style == 'LIMIT' and not price:
            return jsonify({"status": "error", "message": "price is required for LIMIT orders"}), 400
        
        # Check if symbol exists
        instrument = next((i for i in instruments_db if i['symbol'] == symbol), None)
        if not instrument:
            return jsonify({"status": "error", "message": f"Invalid symbol: {symbol}"}), 400
        
        # For SELL orders, check if user has sufficient holdings
        if order_type == 'SELL':
            holding = portfolio_db.get(symbol, {})
            if holding.get('quantity', 0) < quantity:
                return jsonify({"status": "error", "message": "Insufficient holdings to sell"}), 400
        
        # Create order
        order_id = str(uuid.uuid4())
        order = {
            "orderId": order_id,
            "userId": MOCK_USER_ID,
            "symbol": symbol,
            "orderType": order_type,
            "orderStyle": order_style,
            "quantity": quantity,
            "price": price if order_style == 'LIMIT' else instrument['lastTradedPrice'],
            "status": "PLACED",
            "timestamp": datetime.now().isoformat()
        }
        
        orders_db[order_id] = order
        
        # Simulate immediate execution for MARKET orders
        if order_style == 'MARKET':
            execute_order(order_id)
        
        return jsonify({
            "status": "success",
            "data": order
        }), 201
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/v1/orders/<order_id>', methods=['GET'])
def get_order_status(order_id):
    """Fetch order status"""
    order = orders_db.get(order_id)
    
    if not order:
        return jsonify({"status": "error", "message": "Order not found"}), 404
    
    return jsonify({
        "status": "success",
        "data": order
    }), 200


# 3. TRADE APIs
@app.route('/api/v1/trades', methods=['GET'])
def get_trades():
    """Fetch list of executed trades"""
    user_trades = [t for t in trades_db if t['userId'] == MOCK_USER_ID]
    
    return jsonify({
        "status": "success",
        "data": user_trades
    }), 200


# 4. PORTFOLIO APIs
@app.route('/api/v1/portfolio', methods=['GET'])
def get_portfolio():
    """Fetch current portfolio holdings"""
    portfolio_list = []
    
    for symbol, holding in portfolio_db.items():
        instrument = next((i for i in instruments_db if i['symbol'] == symbol), None)
        current_price = instrument['lastTradedPrice'] if instrument else 0
        
        portfolio_list.append({
            "symbol": symbol,
            "quantity": holding['quantity'],
            "averagePrice": holding['averagePrice'],
            "currentValue": holding['quantity'] * current_price
        })
    
    return jsonify({
        "status": "success",
        "data": portfolio_list
    }), 200


# Helper function to execute orders
def execute_order(order_id):
    """Simulate order execution"""
    order = orders_db.get(order_id)
    if not order:
        return
    
    # Update order status
    order['status'] = 'EXECUTED'
    
    # Create trade record
    trade = {
        "tradeId": str(uuid.uuid4()),
        "orderId": order_id,
        "userId": order['userId'],
        "symbol": order['symbol'],
        "orderType": order['orderType'],
        "quantity": order['quantity'],
        "price": order['price'],
        "timestamp": datetime.now().isoformat()
    }
    trades_db.append(trade)
    
    # Update portfolio
    symbol = order['symbol']
    if symbol not in portfolio_db:
        portfolio_db[symbol] = {"quantity": 0, "averagePrice": 0, "totalCost": 0}
    
    holding = portfolio_db[symbol]
    
    if order['orderType'] == 'BUY':
        # Add to holdings
        new_total_cost = holding['totalCost'] + (order['quantity'] * order['price'])
        new_quantity = holding['quantity'] + order['quantity']
        holding['quantity'] = new_quantity
        holding['totalCost'] = new_total_cost
        holding['averagePrice'] = new_total_cost / new_quantity
    else:  # SELL
        # Reduce holdings
        holding['quantity'] -= order['quantity']
        if holding['quantity'] == 0:
            del portfolio_db[symbol]
        else:
            holding['totalCost'] = holding['quantity'] * holding['averagePrice']


# Error handler
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)