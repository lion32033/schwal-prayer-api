from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
import requests

URL = "https://mawaqit.net/de/m/albir-schwalbach"
JSON_FILE = "prayer-schwal.json"

def fetch_prayer_times():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    print(f"Lade Gebetszeiten von: {URL}")
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Verbindungsaufbau: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    prayer_data = {
        "mosque": "Al-Birr Schwalbach",
        "source_url": URL,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_gregorian": datetime.now().strftime("%Y-%m-%d"),
        "times": {}
    }

    try:
        for element in soup.find_all(['div', 'li', 'span']):
            text = element.get_text(strip=True)
            for name in ["Fajr", "Fadjr", "Shuruk", "Dohr", "Dhuhr", "Assr", "Asr", "Maghrib", "Isha"]:
                if name.lower() in text.lower() and len(text) < 30:
                    parent = element.parent
                    if parent:
                        time_val = parent.get_text(strip=True).replace(text, "")
                        if time_val:
                            clean_time = time_val.strip().split()[0]
                            if len(clean_time) <= 5: # Validierung, ob es wie eine Uhrzeit aussieht
                                prayer_data["times"][name] = clean_time
    except Exception as e:
        print(f"Fehler beim Parsen der HTML-Struktur: {e}")

    return prayer_data

def save_to_json(data):
    if not data or not data["times"]:
        print("Keine Zeiten gefunden, JSON wird nicht überschrieben.")
        return
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Daten erfolgreich in '{JSON_FILE}' gespeichert.")

if __name__ == "__main__":
    data = fetch_prayer_times()
    save_to_json(data)
