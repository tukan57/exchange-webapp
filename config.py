import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
    API_KEY = '0b5a463e6508f9571de58d930aca1041'
    BASE_URL = 'https://api.exchangerate.host/'
    SETTINGS_FILE = 'data/settings.json'
    LOG_FILE = 'data/app.log'
    USERNAME = 'admin'
    PASSWORD = 'pswd123'
    USE_MOCK_DATA = False