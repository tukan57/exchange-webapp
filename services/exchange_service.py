import requests
import json

class ExchangeService:
    def __init__(self, api_key, base_url="https://api.exchangerate.host/"):
        self.api_key = api_key
        self.base_url = base_url

    def get_latest_rates(self, base_currency, symbols):
        params = {
            'access_key': self.api_key,
            'base': base_currency,
            'symbols': ",".join(symbols)
        }
        try:
            response = requests.get(f"{self.base_url}latest", params=params)
            data = response.json()
            if not data.get("success"):
                raise Exception(data.get("error", {}).get("info", "Neznámá chyba API"))
            return data["rates"]
        except Exception as e:
            # Zde by se volal logging_service
            raise e