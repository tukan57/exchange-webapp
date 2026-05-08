import pytest
import os
import json
from services.exchange_service import ExchangeService
from config import Config

@pytest.fixture
def service(mocker):
    # Vynutíme mock data pro všechny testy v tomto souboru
    mocker.patch.object(Config, 'USE_MOCK_DATA', True)
    return ExchangeService()

def test_get_all_currencies_from_file(service, mocker):
    # Simulujeme obsah list.json
    mock_list = {"currencies": {"EUR": "Euro", "USD": "Dollar"}}
    
    # Patchujeme open, aby četlo naše data místo skutečného disku (pokud by tam soubor chyběl)
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_list)))
    
    result = service.get_all_currencies()
    assert "EUR" in result
    assert result["USD"] == "Dollar"

def test_get_latest_rates_processing(service, mocker):
    # Simulujeme obsah sample_rates.json
    mock_rates = {
        "quotes": {
            "EURCZK": 25.5,
            "EURUSD": 1.08
        },
        "timestamp": 1600000000
    }
    
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_rates)))
    # Musíme patchovat i os.path.exists, aby si service myslela, že soubor existuje
    mocker.patch("os.path.exists", return_value=True)
    
    result = service.get_latest_rates(base_currency="EUR", selected_currencies=["CZK"])
    
    assert result["base"] == "EUR"
    assert "CZK" in result["rates"]
    assert "USD" not in result["rates"] # Otestuje větev filtrování
    assert result["rates"]["CZK"] == 25.5

def test_mock_file_not_found(service, mocker):
    # Testuje větev 'except Exception as e' v _get_mock_data
    mocker.patch("builtins.open", side_effect=IOError("File not found"))
    
    result = service.get_latest_rates()
    assert result is None

def test_get_all_currencies_api_branch(service, requests_mock, mocker):
    # Přepneme na False, abychom vlezli do větve s API
    mocker.patch.object(Config, 'USE_MOCK_DATA', False)
    
    api_url = f"{Config.BASE_URL}list"
    requests_mock.get(api_url, json={"currencies": {"USD": "Dollar"}})
    
    res = service.get_all_currencies()
    assert res["USD"] == "Dollar"

def test_get_latest_rates_api_branch(service, requests_mock, mocker):
    # Přepneme na False
    mocker.patch.object(Config, 'USE_MOCK_DATA', False)
    
    api_url = f"{Config.BASE_URL}live"
    requests_mock.get(api_url, json={"quotes": {"EURUSD": 1.1}, "timestamp": 123})
    
    res = service.get_latest_rates("EUR", ["USD"])
    assert res["rates"]["USD"] == 1.1