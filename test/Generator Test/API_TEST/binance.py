# <file:DOCS>BINANCE_DOCS.md<file:DOCS/>
# <file:MANIFEST>MANIFEST.txt<file:MANIFEST/>

# <context:BINANCE_INTEGRATION>
# These are the requirements for this codefile.
# 1. Create a BinanceIntegration class that will handle the integration with the Binance API.
# 2. The class should have a method to fetch historical data for 1 second candles
# 3. IF 1 second is not possible then I just need a method for getting the current price
# of the pair mentioned in the manifest file.
# <context:BINANCE_INTEGRATION/>

# <prompt:CreateBinanceIntegration>
# Based on the BINANCE_INTEGRATION requirements, please implement this binance.py file.
# For context you will get the project description for you to design the best solution with a list of libraries
# also most importnantly you will get Binance API documentation from BINANCE_DOCS.md.
# {BINANCE_INTEGRATION}
# {MANIFEST}
# {BINANCE_DOCS}
# <prompt:CreateBinanceIntegration/>

# <context:BinanceIntegration>
# <CreateBinanceIntegration>
import requests

class BinanceIntegration:
    """
    Class that handles the integration with the Binance API for fetching cryptocurrency data.
    """
    
    def __init__(self):
        # The base URL of the Binance API
        self.base_url = "https://api.binance.com"
    
    def get_current_price(self, symbol:str = "BTCUSDT"):
        """
        Fetches the current price of a trading pair (default BTC/USDT).

        :param symbol: The symbol of the trading pair to fetch, default is BTC/USDT.
        :return: The current price as float or raises an exception if unable to fetch.
        """
        endpoint = "/api/v3/ticker/price"
        url = f"{self.base_url}{endpoint}?symbol={symbol}"
        response = requests.get(url)
        response.raise_for_status() # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        
        # Assuming a successful response, parse the JSON and return the price
        price_info = response.json()
        return float(price_info['price'])

# Example usage:
# binance_integration = BinanceIntegration()
# current_price = binance_integration.get_current_price()
# print(f"Current price of BTC/USDT is: {current_price}")
# <CreateBinanceIntegration/>
# <context:BinanceIntegration/>