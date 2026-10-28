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

    # Mawaqit speichert die Zeiten meistens in 'times' als Liste von Tagen.
    # Manchmal ist es eine Liste von Listen oder ein Objekt. Schauen wir nach dem heutigen Tag.
    times_data = conf_data.get("times", [])
    today_day_idx = datetime.now().day - 1  # 0-basierter Index für den Monatstag

    today_times = []
    if isinstance(times_data, list) and len(times_data) > 0:
      if today_day_idx < len(times_data):
        raw_today = times_data[today_day_idx]
        # Falls es eine Liste von Zeiten für den Tag ist:
        if isinstance(raw_today, list):
          today_times = raw_today
        elif isinstance(raw_today, dict):
          # Manchmal ist es ein Dictionary
          today_times = list(raw_today.values())

    # Fallraum, falls die Struktur anders verschachtelt ist:
    # Mawaqit Standard-Reihenfolge der Gebete: [Fajr, Shuruk (Sonnenaufgang), Dhuhr, Asr, Maghrib, Isha]
    prayer_names = ["Fajr", "Shuruk", "Dhuhr", "Asr", "Maghrib", "Isha"]
    times_dict = {}

    for idx, name in enumerate(prayer_names):
      if idx < len(today_times) and isinstance(today_times[idx], str):
        times_dict[name] = today_times[idx]
      else:
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
  if not data or not data.get("times"):
    print("Keine gültigen Zeiten gefunden. JSON wird nicht überschrieben.")
    return
  with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
  print(f"Daten erfolgreich in '{JSON_FILE}' gespeichert.")


if __name__ == "__main__":
  data = fetch_prayer_times()
  if data:
    save_to_json(data)
