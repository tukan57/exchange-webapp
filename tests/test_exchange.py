import pytest
import time
import json
from services.exchange_service import ExchangeService
from config import Config

@pytest.fixture
def service(mocker):
    mocker.patch.object(Config, 'USE_MOCK_DATA', True)
    # Resetujeme cache před každým testem
    ExchangeService._cache = {}
    ExchangeService._last_fetch_time = {}
    return ExchangeService()

def test_get_latest_rates_cache_hit(service, mocker):
    base = "EUR"
    mock_data = {"quotes": {"EURCZK": 25.0}, "success": True}
    ExchangeService._cache[base] = mock_data
    ExchangeService._last_fetch_time[base] = time.time()
    spy = mocker.spy(service, '_load_mock_file')
    result = service.get_latest_rates(base_currency=base)
    assert result["rates"]["CZK"] == 25.0
    assert spy.call_count == 0

def test_get_historical_rates_mock(service, mocker):
    mock_rates = {"quotes": {"EURUSD": 1.1}, "date": "2023-01-01"}
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_rates)))
    res = service.get_historical_rates("2023-01-01", "EUR")
    assert res["date"] == "2023-01-01"
    assert res["rates"]["USD"] == 1.1


def test_get_all_currencies_mock_file_error(service, mocker):
    mocker.patch.object(Config, 'USE_MOCK_DATA', True)
    mocker.patch("builtins.open", side_effect=Exception("Disk error"))
    res = service.get_all_currencies()
    assert res == {"CZK": "Czech Koruna", "EUR": "Euro", "USD": "US Dollar"}

def test_load_mock_file_exception(service, mocker):
    mocker.patch("os.path.join", side_effect=Exception("Path error"))
    res = service._load_mock_file("any.json")
    assert res == {}

def test_get_all_currencies_api_success(service, mocker, requests_mock):
    mocker.patch.object(Config, 'USE_MOCK_DATA', False)
    api_url = f"{Config.BASE_URL}list"
    requests_mock.get(api_url, json={"currencies": {"AED": "Dirham"}, "success": True})
    res = service.get_all_currencies()
    assert res["AED"] == "Dirham"

def test_get_latest_rates_api_success_and_cache(service, mocker, requests_mock):
    mocker.patch.object(Config, 'USE_MOCK_DATA', False)
    api_url = f"{Config.BASE_URL}live"
    mock_response = {"success": True, "quotes": {"EURUSD": 1.08}, "timestamp": 123456}
    requests_mock.get(api_url, json=mock_response)
    res = service.get_latest_rates("EUR")
    assert res["rates"]["USD"] == 1.08
    assert "EUR" in service._cache

def test_process_data_empty_key_matches_base(service):
    data = {"quotes": {"EUR": 1.0}, "timestamp": 111}
    res = service._process_data(data, "EUR", None)
    assert res["rates"]["EUR"] == 1.0

def test_process_data_with_selected_currencies(service):
    data = {"quotes": {"EURUSD": 1.1, "EURCZK": 25.0}}
    res = service._process_data(data, "EUR", ["USD"])
    assert "USD" in res["rates"]
    assert "CZK" not in res["rates"]

# Testy pro API failure (už jsi měl)
def test_get_latest_rates_api_error(service, mocker, requests_mock):
    mocker.patch.object(Config, 'USE_MOCK_DATA', False)
    api_url = f"{Config.BASE_URL}live"
    requests_mock.get(api_url, status_code=500)
    res = service.get_latest_rates("EUR")
    assert res is None