import json
import os
from config import Config

class StorageService:
    @staticmethod
    def load_settings():
        if not os.path.exists(Config.SETTINGS_FILE):
            return {"baseCurrency": "EUR", "selectedCurrencies": ["CZK", "USD", "GBP"]}
        with open(Config.SETTINGS_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_settings(settings):
        with open(Config.SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)