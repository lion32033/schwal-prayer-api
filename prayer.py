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
    conf_text = match.group(1)
    conf_data = json.loads(conf_text)

    prayer_names = ["Fajr", "Shuruk", "Dhuhr", "Asr", "Maghrib", "Isha"]
    times_dict = {}

    # Extrahiere alle echten Uhrzeiten im Format HH:MM aus dem gesamten confData-Block
    all_times = re.findall(r'"(\d{2}:\d{2})"', conf_text)

    # Filtere Duplikate und ungültige Werte heraus, behalte aber die Reihenfolge
    seen = set()
    unique_times = []
    for t in all_times:
      if t not in seen:
        seen.add(t)
        unique_times.append(t)

    # Mawaqit listet die täglichen Gebetszeiten im Array auf.
    # Wir nehmen die ersten 6 passenden Zeiten für den aktuellen Tag.
    if len(unique_times) >= 6:
      # Manchmal stehen im confData zuerst die Azhan-Zeiten für heute
      for idx, name in enumerate(prayer_names):
        times_dict[name] = unique_times[idx]
    else:
      for name in prayer_names:
        times_dict[name] = "N/A"

    prayer_data = {
        "mosque": conf_data.get("name", "مسجد البر - Schwalbach"),
        "source_url": URL,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_gregorian": datetime.now().strftime("%Y-%m-%d"),
        "times": times_dict,
    }

    return prayer_data

  except Exception as e:
    print(f"Fehler beim Parsen: {e}")
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
