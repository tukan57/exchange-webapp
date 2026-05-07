import requests
from config import Config
from .logging_service import LoggingService

class ExchangeService:
    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL

    def get_latest_rates(self, base, symbols):
        params = {
            'access_key': self.api_key,
            'base': base,
            'symbols': ",".join(symbols)
        }
        try:
            response = requests.get(f"{self.base_url}latest", params=params)
            data = response.json()
            if not data.get("success"):
                LoggingService.log_error(f"API Error: {data.get('error')}")
                return None
            return data
        except Exception as e:
            LoggingService.log_error(f"Network Error: {str(e)}")
            return None