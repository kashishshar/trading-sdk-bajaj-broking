import requests
import json


class TradingSDK:
    """
    Wrapper SDK for Trading APIs
    Provides easy-to-use methods to interact with the trading platform
    """
    
    def __init__(self, base_url="http://localhost:5000"):
        """
        Initialize the SDK with base URL
        
        Args:
            base_url (str): Base URL of the trading API server
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def get_instruments(self):
        """
        Fetch list of tradable instruments
        
        Returns:
            dict: Response containing list of instruments
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/instruments")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def place_order(self, symbol, order_type, quantity, order_style="MARKET", price=None):
        """
        Place a new order
        
        Args:
            symbol (str): Trading symbol (e.g., "RELIANCE")
            order_type (str): "BUY" or "SELL"
            quantity (int): Number of shares (must be > 0)
            order_style (str): "MARKET" or "LIMIT" (default: "MARKET")
            price (float): Price for LIMIT orders (required for LIMIT orders)
        
        Returns:
            dict: Response containing order details
        """
        payload = {
            "symbol": symbol,
            "orderType": order_type,
            "quantity": quantity,
            "orderStyle": order_style
        }
        
        if order_style == "LIMIT":
            if price is None:
                return {"status": "error", "message": "Price is required for LIMIT orders"}
            payload["price"] = price
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/orders",
                data=json.dumps(payload)
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def get_order_status(self, order_id):
        """
        Fetch order status
        
        Args:
            order_id (str): Unique order identifier
        
        Returns:
            dict: Response containing order status
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/orders/{order_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def get_trades(self):
        """
        Fetch list of executed trades
        
        Returns:
            dict: Response containing list of trades
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/trades")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def get_portfolio(self):
        """
        Fetch current portfolio holdings
        
        Returns:
            dict: Response containing portfolio holdings
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/portfolio")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}


# Example usage
if __name__ == "__main__":
    # Initialize SDK
    sdk = TradingSDK()
    
    # 1. Get instruments
    print("=== Fetching Instruments ===")
    instruments = sdk.get_instruments()
    print(json.dumps(instruments, indent=2))
    
    # 2. Place a BUY order
    print("\n=== Placing BUY Order ===")
    buy_order = sdk.place_order(
        symbol="RELIANCE",
        order_type="BUY",
        quantity=10,
        order_style="MARKET"
    )
    print(json.dumps(buy_order, indent=2))
    
    if buy_order['status'] == 'success':
        order_id = buy_order['data']['orderId']
        
        # 3. Check order status
        print("\n=== Checking Order Status ===")
        order_status = sdk.get_order_status(order_id)
        print(json.dumps(order_status, indent=2))
    
    # 4. Get trades
    print("\n=== Fetching Trades ===")
    trades = sdk.get_trades()
    print(json.dumps(trades, indent=2))
    
    # 5. Get portfolio
    print("\n=== Fetching Portfolio ===")
    portfolio = sdk.get_portfolio()
    print(json.dumps(portfolio, indent=2))