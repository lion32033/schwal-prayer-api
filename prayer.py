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

  # Mawaqit bettet alle Moschee-Daten in 'var confData = {...}' ein
  match = re.search(r"var\s+confData\s*=\s*(\{.*?\});", html, re.DOTALL)
  if not match:
    print(
        "Fehler: 'confData' konnte im Seitenquelltext nicht gefunden werden."
    )
    return None

  try:
    conf_data = json.loads(match.group(1))

    # confData['times'] enthält ein Array von Zeiten pro Tag für den gesamten Monat
    times_list = conf_data.get("times", [])
    today_day = datetime.now().day - 1  # 0-basierter Index für den Tag des Monats

    if today_day < len(times_list):
      today_times = times_list[today_day]  # z.B. ["05:15", "06:45", "12:15", ...]
    else:
      today_times = times_list[0]

    # Mawaqit speichert i.d.R. 6 Standardzeiten: [Fajr, Shuruk, Dhuhr, Asr, Maghrib, Isha]
    prayer_names = ["Fajr", "Shuruk", "Dhuhr", "Asr", "Maghrib", "Isha"]
    times_dict = {}

    for idx, name in enumerate(prayer_names):
      if idx < len(today_times):
        times_dict[name] = today_times[idx]

    prayer_data = {
        "mosque": conf_data.get("name", "Al-Birr Schwalbach"),
        "source_url": URL,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_gregorian": datetime.now().strftime("%Y-%m-%d"),
        "times": times_dict,
    }

    return prayer_data

  except Exception as e:
    print(f"Fehler beim Extrahieren der Zeiten aus confData: {e}")
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
  save_to_json(data)
