import pytest
from services.analytics_service import AnalyticsService

@pytest.fixture
def sample_rates():
    """Základní sada testovacích dat pro aktuální kurzy."""
    return {
        "USD": 1.1,
        "CZK": 25.0,
        "GBP": 0.8,
        "EUR": 1.0
    }

@pytest.fixture
def sample_time_series():
    """Data pro testování výpočtu průměru za období (historická data)."""
    return {
        "2025-01-01": {"USD": 1.0, "CZK": 24.0},
        "2025-01-02": {"USD": 1.2, "CZK": 26.0},
        "2025-01-03": {"USD": 1.1, "CZK": 25.0}
    }

def test_get_strongest_currency_success(sample_rates):
    """Testuje nalezení nejvyšší nominální hodnoty (nejsilnější měna dle zadání)."""
    res = AnalyticsService.get_strongest_currency(sample_rates)
    assert res[0] == "CZK"
    assert res[1] == 25.0

def test_get_weakest_currency_success(sample_rates):
    """Testuje nalezení nejnižší nominální hodnoty (nejslabší měna)."""
    res = AnalyticsService.get_weakest_currency(sample_rates)
    assert res[0] == "GBP"
    assert res[1] == 0.8

def test_get_currency_bounds_empty():
    """Ověřuje, že metody vrátí None, pokud je vstup prázdný (pokrytí větví)."""
    assert AnalyticsService.get_strongest_currency({}) is None
    assert AnalyticsService.get_weakest_currency({}) is None



def test_calculate_average_success(sample_time_series):
    """Testuje standardní výpočet aritmetického průměru."""
    # (1.0 + 1.2 + 1.1) / 3 = 1.1
    avg_usd = AnalyticsService.calculate_average(sample_time_series, "USD")
    assert avg_usd == pytest.approx(1.1)

def test_calculate_average_missing_data_in_days():
    """
    Testuje požadavek DSP: 'Chybějící data ignorovat'.
    Pokrývá podmínku 'if currency_code in date_data'.
    """
    incomplete_data = {
        "2025-01-01": {"USD": 1.0},
        "2025-01-02": {"EUR": 0.9},  # USD chybí úplně
        "2025-01-03": {"USD": 2.0}
    }
    avg_usd = AnalyticsService.calculate_average(incomplete_data, "USD")
    assert avg_usd == 1.5

def test_calculate_average_empty_input():
    """Testuje větev 'else 0' při prázdném vstupu."""
    assert AnalyticsService.calculate_average({}, "USD") == 0

def test_calculate_average_currency_not_present():
    """Testuje situaci, kdy měna v datech vůbec neexistuje."""
    data = {"2025-01-01": {"EUR": 1.0}}
    assert AnalyticsService.calculate_average(data, "USD") == 0


def test_get_min_max_logic(sample_rates):
    """Testuje metodu vracející slovník s nejsilnější a nejslabší měnou."""
    res = AnalyticsService.get_min_max(sample_rates)
    assert res["strongest"][0] == "CZK"
    assert res["weakest"][0] == "GBP"

def test_get_min_max_empty():
    """Pokrývá 'if not rates' guard clause v metodě get_min_max."""
    assert AnalyticsService.get_min_max({}) is None

def test_get_min_max_single_value():
    """Testuje chování, pokud je v seznamu pouze jedna měna."""
    res = AnalyticsService.get_min_max({"CZK": 25.0})
    assert res["strongest"][0] == "CZK"
    assert res["weakest"][0] == "CZK"