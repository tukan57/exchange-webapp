class StorageService:
    FILE_PATH = "data/settings.json"

    def save_settings(self, settings_dict):
        with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=4)

    def load_settings(self):
        try:
            with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"baseCurrency": "EUR", "selectedCurrencies": ["CZK", "USD"]}