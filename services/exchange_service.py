import json
import requests
from config import Config
from services.storage_service import StorageService

class ExchangeService:
    def get_latest_rates(self, base_currency='EUR', selected_currencies=None):
        if Config.USE_MOCK_DATA:
            StorageService.log_event("info", "Načítání aktuálních MOCK dat.")
            return self._get_mock_data(base_currency, selected_currencies)
        
        url = f"{Config.BASE_URL}live"
        params = {'access_key': Config.API_KEY, 'source': base_currency, 'format': 1}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            StorageService.log_event("info", f"Úspěšné volání API (latest) pro {base_currency}")
            return self._process_data(data, base_currency, selected_currencies)
        except Exception as e:
            StorageService.log_event("error", f"Selhání API (latest): {str(e)}")
            return None

    def get_historical_rates(self, date, base_currency='EUR', selected_currencies=None):
        if Config.USE_MOCK_DATA:
            StorageService.log_event("info", f"Načítání historických MOCK dat pro datum {date}.")
            return self._get_mock_data(base_currency, selected_currencies)

        url = f"{Config.BASE_URL}{date}"
        params = {'access_key': Config.API_KEY, 'source': base_currency, 'format': 1}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            StorageService.log_event("info", f"Úspěšné volání API (history) pro datum {date}")
            return self._process_data(data, base_currency, selected_currencies)
        except Exception as e:
            StorageService.log_event("error", f"Selhání API (history) pro {date}: {str(e)}")
            return None

    def _process_data(self, data, base_currency, selected_currencies):
        raw_quotes = data.get('quotes', {})
        processed_rates = {}
        for key, value in raw_quotes.items():
            clean_key = key[len(base_currency):] if key.startswith(base_currency) else key
            if not clean_key: clean_key = base_currency
            if not selected_currencies or clean_key in selected_currencies:
                processed_rates[clean_key] = value
        return {"base": base_currency, "rates": processed_rates, "timestamp": data.get('timestamp')}

    def _get_mock_data(self, base_currency, selected_currencies):
        try:
            with open('tests/samples/sample_rates.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._process_data(data, base_currency, selected_currencies)
        except Exception as e:
            StorageService.log_event("error", f"Chyba při načítání MOCK souboru: {e}")
            return None