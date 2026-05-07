import json
import requests
import os
from config import Config

def capture_api_data():
    # Složka pro vzorky (podle tvého zadání tests/samples)
    folder = 'tests/samples'
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, 'sample_rates.json')

    # Endpoint pro reálná data
    url = f"{Config.BASE_URL}live"
    
    params = {
        'access_key': Config.API_KEY,
        'source': 'EUR',  # Nastavení základní měny na EUR
        # Parametr 'currencies' vynechán -> stáhne to úplně všechny měny
        'format': 1
    }

    try:
        print(f"Stahuji všechna EUR data z {url}...")
        response = requests.get(url, params=params)
        response.raise_for_status() 
        
        data = response.json()
        
        if data.get("success"):
            # Uložíme kompletní JSON odpověď
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            num_rates = len(data.get('quotes', {}))
            print(f"Úspěch! Staženo {num_rates} měnových párů vůči EUR.")
            print(f"Data uložena do: {file_path}")
            
            # Ukázka prvních 3 klíčů (budou vypadat jako EURCZK, EURUSD atd.)
            sample_keys = list(data['quotes'].keys())[:3]
            print(f"Vzorové klíče v JSONu: {sample_keys}")
        else:
            # Pokud by Free plán náhodou source=EUR zablokoval, vypíše to info z API
            error_info = data.get("error", {}).get("info", "Neznámá chyba API")
            print(f"API vrátilo chybu: {error_info}")

    except Exception as e:
        print(f"Chyba při komunikaci s API: {e}")

if __name__ == "__main__":
    capture_api_data()