import json
import requests
import os
from config import Config
from services.logging_service import LoggingService

class ExchangeService:
    def get_all_currencies(self):
        """Načte seznam všech měn z list.json (mock) nebo z API"""
        if Config.USE_MOCK_DATA:
            try:
                path = os.path.join('tests', 'samples', 'list.json')
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    LoggingService.log_event("info", "Načten seznam měn z list.json.")
                    return data.get('currencies', {})
            except Exception as e:
                LoggingService.log_event("error", f"Chyba při čtení list.json: {e}")
                return {"CZK": "Czech Koruna", "EUR": "Euro", "USD": "US Dollar"}
        
        url = f"{Config.BASE_URL}list" 
        params = {'access_key': Config.API_KEY}
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return data.get('currencies', {})
        except Exception as e:
            LoggingService.log_event("error", f"API list failure: {e}")
            return {}

    def get_latest_rates(self, base_currency='EUR', selected_currencies=None):
        if Config.USE_MOCK_DATA:
            LoggingService.log_event("info", "Načítání aktuálních MOCK dat.")
            return self._get_mock_data(base_currency, selected_currencies)
        
        url = f"{Config.BASE_URL}live"
        params = {'access_key': Config.API_KEY, 'source': base_currency, 'format': 1}
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return self._process_data(data, base_currency, selected_currencies)
        except Exception as e:
            LoggingService.log_event("error", f"Selhání API (latest): {str(e)}")
            return None

    def get_historical_rates(self, date, base_currency='EUR', selected_currencies=None):
        if Config.USE_MOCK_DATA:
            return self._get_mock_data(base_currency, selected_currencies)
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
            path = os.path.join('tests', 'samples', 'sample_rates.json')
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._process_data(data, base_currency, selected_currencies)
        except Exception as e:
            LoggingService.log_event("error", f"Chyba při načítání MOCK souboru: {e}")
            return None