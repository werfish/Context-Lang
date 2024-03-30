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
from typing import Dict, Union


class BinanceIntegration:

    def __init__(self):
        # Binance API base URL
        self.base_url = "https://api.binance.com"
    
    def fetch_current_price(self, symbol: str) -> Union[Dict[str, Union[str, float]], str]:
        endpoint = f"{self.base_url}/api/v3/ticker/price"
        params = {'symbol': symbol}
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise HTTPError for bad requests (4xx or 5xx)
            data = response.json()
            # Ensuring proper data format
            if "price" in data and "symbol" in data:
                return {
                    "symbol": data["symbol"],
                    "price": float(data["price"])
                }
            else:
                return "Unexpected data format from Binance API."
        except requests.exceptions.HTTPError as http_err:
            # Log the error here
            # logger.error(f"HTTP error occurred: {http_err}")
            return f"HTTP error occurred: {http_err}"
        except Exception as err:
            # Log the error here
            # logger.error(f"An error occurred: {err}")
            return f"An error occurred: {err}"

# Example usage:
# binance_integration = BinanceIntegration()
# current_price = binance_integration.fetch_current_price("BTCUSDT")
# print(current_price)
# <CreateBinanceIntegration/>
# <context:BinanceIntegration/>