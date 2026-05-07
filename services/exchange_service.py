import json
import requests
from config import Config

class ExchangeService:
    def get_latest_rates(self, base_currency='EUR', selected_currencies=None):
        """
        Rozcestník mezi reálnými a testovacími daty.
        """
        if Config.USE_MOCK_DATA:
            print("INFO: Používám MOCK data ze souboru.")
            return self._get_mock_data(base_currency, selected_currencies)
        else:
            print("INFO: Volám reálné API.")
            return self._get_real_data(base_currency, selected_currencies)

    def _get_mock_data(self, base_currency, selected_currencies):
        """Načte data z tvého sample_rates.json"""
        file_path = 'tests/samples/sample_rates.json'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._process_data(data, base_currency, selected_currencies)
        except Exception as e:
            print(f"Chyba při načítání souboru: {e}")
            return None

    def _get_real_data(self, base_currency, selected_currencies):
        """Získá data z internetu"""
        url = f"{Config.BASE_URL}live"
        params = {
            'access_key': Config.API_KEY,
            'source': base_currency,
            'format': 1
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                print(f"API Error: {data.get('error')}")
                return None
            return self._process_data(data, base_currency, selected_currencies)
        except Exception as e:
            print(f"Chyba při volání API: {e}")
            return None

    def _process_data(self, data, base_currency, selected_currencies):
        """Společná logika pro očištění klíčů (EURCZK -> CZK)"""
        raw_quotes = data.get('quotes', {})
        processed_rates = {}

        for key, value in raw_quotes.items():
            # Odstranění prefixu (např. 'EUR')
            clean_key = key[len(base_currency):] if key.startswith(base_currency) else key
            
            if not clean_key:
                clean_key = base_currency

            if selected_currencies:
                if clean_key in selected_currencies:
                    processed_rates[clean_key] = value
            else:
                processed_rates[clean_key] = value

        return {
            "base": base_currency,
            "rates": processed_rates,
            "timestamp": data.get('timestamp')
        }