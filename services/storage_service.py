import json
import os
from config import Config

class StorageService:
    @staticmethod
    def load_settings():
        if not os.path.exists(Config.SETTINGS_FILE):
            return {"baseCurrency": "EUR", "selectedCurrencies": ["CZK", "USD", "GBP"]}
        
        try:
            with open(Config.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return {"baseCurrency": "EUR", "selectedCurrencies": ["CZK", "USD", "GBP"]}
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return {"baseCurrency": "EUR", "selectedCurrencies": ["CZK", "USD", "GBP"]}

    @staticmethod
    def save_settings(settings):
        os.makedirs(os.path.dirname(Config.SETTINGS_FILE), exist_ok=True)
        with open(Config.SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    