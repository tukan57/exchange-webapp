import pytest
from services.logging_service import LoggingService

def test_setup_logging(mocker):
    # Mockujeme Config a os.makedirs, aby se nepracovalo s reálným diskem
    mocker.patch('services.logging_service.Config.LOG_FILE', 'logs/app.log')
    mock_makedirs = mocker.patch('os.makedirs')
    mock_basic_config = mocker.patch('logging.basicConfig')
    
    LoggingService.setup_logging()
    
    # Ověření řádků 8-10: Vytvoření složky a nastavení loggingu
    mock_makedirs.assert_called_with('logs', exist_ok=True)
    mock_basic_config.assert_called_once()

@pytest.mark.parametrize("level, expected_method", [
    ("info", "info"),
    ("warning", "warning"),
    ("error", "error"),
    ("debug", "debug"),
    ("unknown", "debug"), # Tento řádek pokryje větev 'else' (řádek 28)
])
def test_log_event_branches(mocker, level, expected_method):
    # Mockujeme metody v modulu logging
    mock_log = mocker.patch(f'logging.{expected_method}')
    
    message = "Test zpráva"
    LoggingService.log_event(level, message)
    
    # Ověříme, že byla zavolána správná funkce
    mock_log.assert_called_once_with(message)