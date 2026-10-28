from datetime import datetime
import json
import requests

# Offizielle Mawaqit API-URL für Al-Birr Schwalbach
URL = "https://mawaqit.net/de/m/albir-schwalbach"
API_URL = "https://mawaqit.net/api/2/ mosque/albir-schwalbach" # Alternativ über die Moschee-ID
JSON_FILE = "prayer-schwal.json"

# Da Mawaqit oft eine API mit eindeutiger ID nutzt, nutzen wir hier einen direkten Weg 
# über den Mawaqit API-Endpunkt für Schwalbach:
DIRECT_API_URL = "https://mawaqit.net/de/m/albir-schwalbach"

def fetch_prayer_times():
    # Wir nutzen die interne JSON-API von Mawaqit, die die Moschee-Daten liefert
    # Mawaqit-Moscheen haben oft einen API-Endpunkt im Format /api/mini/v2/... oder laden es über die Hauptseite mit AJAX.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    # Die zuverlässigste Methode für Mawaqit ist es, die Mobil/Mini-API anzusprechen
    # Moschee-Slug für Schwalbach ist 'albir-schwalbach'
    api_endpoint = "https://mawaqit.net/en/m/albir-schwalbach"
    
    print(f"Lade Daten von Mawaqit...")
    
    # Mawaqit blockiert manchmal Standard-Requests ohne Cookies, 
    # aber wir können die offiziellen JSON-Daten direkt über die API-Struktur holen:
    try:
        # Wir fragen die Seite ab und nutzen die standardisierten API-Header
        session = requests.Session()
        # Einmal Hauptseite besuchen, um Cookies zu erhalten
        session.get("https://mawaqit.net/de/m/albir-schwalbach", headers=headers, timeout=15)
        
        # Mawaqit lädt die Zeiten per AJAX von der API. Versuchen wir den direkten API-Call:
        api_call = "https://mawaqit.net/api/1/mosque/albir-schwalbach" # (Falls vorhanden)
        
        # Da Mawaqit manchmal die API ändert, nutzen wir einen direkten Parser auf die mobile JSON-Ansicht:
        # Mawaqit stellt für jede Moschee eine /widget/ -Ansicht bereit, die reines HTML mit den echten Zeiten liefert:
        widget_url = "https://mawaqit.net/de/m/albir-schwalbach/widget"
        res = session.get(widget_url, headers=headers, timeout=15)
        
        if res.status_code != 200:
            # Fallback auf die Hauptseite
            res = session.get(URL, headers=headers, timeout=15)
            
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Wir suchen nach allen Uhrzeiten im Format HH:MM auf der Widget-Seite
        text_content = soup.get_text()
        
        # Mawaqit listet die Zeiten meist in einer festen Reihenfolge im Widget auf: Fajr, Shuruk, Dhuhr, Asr, Maghrib, Isha
        # Suchen wir nach allen Mustern, die wie Uhrzeiten aussehen (HH:MM)
        all_times = re.findall(r'\b([0-2]\d:[0-5]\d)\b', text_content)
        
        # Duplikate filtern, aber Reihenfolge behalten
        unique_times = []
        for t in all_times:
            if t not in unique_times:
                unique_times.append(t)
                
        prayer_names = ["Fajr", "Shuruk", "Dhuhr", "Asr", "Maghrib", "Isha"]
        times_dict = {}
        
        # Die ersten 6 Uhrzeiten im Widget entsprechen exakt den Gebetszeiten des Tages
        for idx, name in enumerate(prayer_names):
            if idx < len(unique_times):
                times_dict[name] = unique_times[idx]
            else:
                times_dict[name] = "N/A"

        prayer_data = {
            "mosque": "Al-Birr Schwalbach",
            "source_url": URL,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_gregorian": datetime.now().strftime("%Y-%m-%d"),
            "times": times_dict
        }

        return prayer_data

    except Exception as e:
        print(f"Fehler beim Abrufen: {e}")
        return None

def save_to_json(data):
    if not data or not data.get("times"):
        print("Keine gültigen Zeiten gefunden.")
        return
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Daten erfolgreich in '{JSON_FILE}' gespeichert.")

if __name__ == "__main__":
    data = fetch_prayer_times()
    if data:
        save_to_json(data)
