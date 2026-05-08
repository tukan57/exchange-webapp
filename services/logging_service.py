import logging
import os
from config import Config

class LoggingService:
    @staticmethod
    def setup_logging():
        os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)
        
        logging.basicConfig(
            filename=Config.LOG_FILE,
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8'
        )

    @staticmethod
    def log_event(level, message):
        level = level.lower()
        if level == 'info':
            logging.info(message)
        elif level == 'warning':
            logging.warning(message)
        elif level == 'error':
            logging.error(message)
        else:
            logging.debug(message)