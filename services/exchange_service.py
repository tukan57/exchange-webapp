import json
import requests
import os
import time
from config import Config
from services.logging_service import LoggingService

class ExchangeService:
    # --- Server-side Cache ---
    _cache = {}
    _last_fetch_time = {}
    CACHE_COOLDOWN = 60  # Cooldown v sekundách (1 minuta)

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
        now = time.time()
        
        # Kontrola cooldownu pro konkrétní base_currency
        last_fetch = self._last_fetch_time.get(base_currency, 0)
        if now - last_fetch < self.CACHE_COOLDOWN and base_currency in self._cache:
            LoggingService.log_event("info", f"Vracím data pro {base_currency} z cache (cooldown).")
            return self._process_data(self._cache[base_currency], base_currency, selected_currencies)

        if Config.USE_MOCK_DATA:
            LoggingService.log_event("info", "Načítání aktuálních MOCK dat.")
            data = self._load_mock_file('sample_rates.json')
        else:
            url = f"{Config.BASE_URL}live"
            params = {'access_key': Config.API_KEY, 'source': base_currency, 'format': 1}
            try:
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                # Uložíme do cache pouze pokud je odpověď úspěšná
                if data and data.get('success'):
                    LoggingService.log_event("info", f"Vyčtení nejnovějších dat pro {base_currency}.")
                    self._cache[base_currency] = data
                    self._last_fetch_time[base_currency] = now
            except Exception as e:
                LoggingService.log_event("error", f"Selhání API (latest): {str(e)}")
                return None

        return self._process_data(data, base_currency, selected_currencies)

    def get_historical_rates(self, date, base_currency='EUR', selected_currencies=None):
        """Načte historické kurzy pro konkrétní datum (YYYY-MM-DD)"""
        if Config.USE_MOCK_DATA:
            LoggingService.log_event("info", f"Načítání MOCK historických dat pro {date}.")
            data = self._load_mock_file('sample_rates.json')
        else:
            url = f"{Config.BASE_URL}historical"
            params = {
                'access_key': Config.API_KEY,
                'date': date,
                'source': base_currency,
                'format': 1
            }
            try:
                response = requests.get(url, params=params, timeout=10)
                LoggingService.log_event("info", f"Vyčtení historických dat pro {date}, {base_currency}.")
                data = response.json()
            except Exception as e:
                LoggingService.log_event("error", f"Selhání API (historical): {str(e)}")
                return None

        return self._process_data(data, base_currency, selected_currencies)

    def _load_mock_file(self, filename):
        """Pomocná metoda pro načtení JSON souboru"""
        try:
            path = os.path.join('tests', 'samples', filename)
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            LoggingService.log_event("error", f"Chyba při načítání souboru {filename}: {e}")
            return {}

    def _process_data(self, data, base_currency, selected_currencies):
        if not data: return None
        raw_quotes = data.get('quotes', {})
        processed_rates = {}
        for key, value in raw_quotes.items():
            # API vrací klíče jako USDEUR, CZKEUR atd.
            clean_key = key[len(base_currency):] if key.startswith(base_currency) else key
            if not clean_key: clean_key = base_currency
            if not selected_currencies or clean_key in selected_currencies:
                processed_rates[clean_key] = value
        return {
            "base": base_currency, 
            "rates": processed_rates, 
            "timestamp": data.get('timestamp'),
            "date": data.get('date') # Přidáno pro historické záznamy
        }