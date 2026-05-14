import pytest
from services.analytics_service import AnalyticsService

@pytest.fixture
def sample_rates():
    return {"USD": 1.1, "CZK": 25.0, "GBP": 0.8}

def test_get_strongest_currency(sample_rates):
    res = AnalyticsService.get_strongest_currency(sample_rates)
    assert res[0] == "CZK"
    assert res[1] == 25.0

def test_get_weakest_currency(sample_rates):
    res = AnalyticsService.get_weakest_currency(sample_rates)
    assert res[0] == "GBP"
    assert res[1] == 0.8

def test_calculate_average_success():
    time_data = {
        "2023-01-01": {"USD": 1.0, "CZK": 24.0},
        "2023-01-02": {"USD": 1.2, "CZK": 26.0}
    }
    avg_usd = AnalyticsService.calculate_average(time_data, "USD")
    assert avg_usd == 1.1

def test_calculate_average_empty_or_missing():
    assert AnalyticsService.calculate_average({}, "USD") == 0
    assert AnalyticsService.calculate_average({"2023": {"EUR": 1}}, "USD") == 0

def test_get_min_max_logic(sample_rates):
    res = AnalyticsService.get_min_max(sample_rates)
    assert res["strongest"][0] == "CZK"
    assert res["weakest"][0] == "GBP"

def test_get_min_max_empty():
    assert AnalyticsService.get_min_max({}) is None