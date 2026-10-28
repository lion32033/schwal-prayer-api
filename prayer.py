from datetime import datetime
import json
import re
import requests

URL = "https://mawaqit.net/de/m/albir-schwalbach"
JSON_FILE = "prayer-schwal.json"


def fetch_prayer_times():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/122.0.0.0 Safari/537.36"
      )
  }

  print(f"Lade Gebetszeiten von: {URL}")
  try:
    response = requests.get(URL, headers=headers, timeout=15)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(f"Fehler beim Verbindungsaufbau: {e}")
    return None

  html = response.text

  # Suchen nach confData im Quelltext
  match = re.search(r"var\s+confData\s*=\s*(\{.*?\});", html, re.DOTALL)
  if not match:
    print(
        "Fehler: 'confData' konnte im Seitenquelltext nicht gefunden werden."
    )
    return None

  try:
    conf_data = json.loads(match.group(1))

    # Debug-Ausgabe für die Logs
    print("Verfügbare confData Schlüssel:", list(conf_data.keys()))

    prayer_names = ["Fajr", "Shuruk", "Dhuhr", "Asr", "Maghrib", "Isha"]
    times_dict = {}

    # 1. Prüfen, ob 'times' direkt als Liste/Array existiert
    times_data = conf_data.get("times", [])
    today_day_idx = datetime.now().day - 1

    if isinstance(times_data, list) and len(times_data) > 0:
      if today_day_idx < len(times_data):
        day_entry = times_data[today_day_idx]
        if isinstance(day_entry, list) and len(day_entry) >= len(prayer_names):
          for idx, name in enumerate(prayer_names):
            times_dict[name] = day_entry[idx]

    # 2. Falls times_dict leer ist, prüfen wir alternative Schlüssel in confData
    if not times_dict:
      for name in prayer_names:
        # Suche nach keys die den Gebetsnamen enthalten
        for k, v in conf_data.items():
          if name.lower() in k.lower() and isinstance(v, str):
            times_dict[name] = v

    # Fallback, falls absolut nichts gefunden wurde
    if not times_dict:
      for name in prayer_names:
        times_dict[name] = "N/A"

    prayer_data = {
        "mosque": conf_data.get("name", "Al-Birr Schwalbach"),
        "source_url": URL,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_gregorian": datetime.now().strftime("%Y-%m-%d"),
        "times": times_dict,
    }

    return prayer_data

  except Exception as e:
    print(f"Fehler beim Parsen des JSON aus confData: {e}")
    return None


def save_to_json(data):
  if not data:
    return
  with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
  print(f"Daten erfolgreich in '{JSON_FILE}' gespeichert.")


if __name__ == "__main__":
  data = fetch_prayer_times()
  if data:
    save_to_json(data)
