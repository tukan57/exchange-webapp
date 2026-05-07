import logging
from config import Config

class LoggingService:
    @staticmethod
    def setup_logging():
        logging.basicConfig(
            filename=Config.LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s'
        )

    @staticmethod
    def log_error(message):
        logging.error(message)