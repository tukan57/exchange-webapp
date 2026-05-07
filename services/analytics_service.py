class AnalyticsService:
    @staticmethod
    def get_strongest_currency(rates):
        # Nejsilnější = nejvyšší nominální hodnota (dle zadání)
        return max(rates.items(), key=lambda x: x[1])

    @staticmethod
    def get_weakest_currency(rates):
        return min(rates.items(), key=lambda x: x[1])

    @staticmethod
    def calculate_average(time_series_data, currency_code):
        # Výpočet aritmetického průměru za období
        values = [date_data[currency_code] 
                  for date_data in time_series_data.values() 
                  if currency_code in date_data]
        return sum(values) / len(values) if values else 0