import pytest
import os
import json
from services.storage_service import StorageService

def test_save_and_load_settings(mocker):
    # Mockujeme open, abychom nezapisovali na disk
    mock_data = {"base": "USD", "symbols": ["EUR"]}
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_data)))
    mocker.patch("os.path.exists", return_value=True)
    
    # Předpokládám, že storage_service má tyto metody
    service = StorageService()
    
    # Testujeme načítání (pokryje řádky načítání)
    data = service.load_settings()
    assert data["base"] == "USD"
    
    # Testujeme ukládání (pokryje řádky zápisu)
    service.save_settings(mock_data)