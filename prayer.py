from datetime import datetime
import json
import re
import requests
from bs4 import BeautifulSoup

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

  soup = BeautifulSoup(response.text, "html.parser")
  prayer_names = ["Fajr", "Shuruk", "Dhuhr", "Asr", "Maghrib", "Isha"]
  times_dict = {}

  # Methode 1: Suche über die Textinhalte der Elemente nach Gebetsnamen und Uhrzeiten im direkten Umfeld
  for name in prayer_names:
    found_time = "N/A"
    # Suche nach Elementen, die den Gebetsnamen enthalten
    for element in soup.find_all(string=re.compile(name, re.IGNORECASE)):
      parent = element.find_parent()
      if parent:
        # Suche im Parent-Element oder dessen Nachbarn nach einer gültigen Uhrzeit (HH:MM)
        match = re.search(r"\b([0-2]\d:[0-5]\d)\b", parent.get_text())
        if match:
          found_time = match.group(1)
          break
    times_dict[name] = found_time

  # Methode 2 (Fallback): Falls über Namen nichts gefunden wurde, extrahiere alle Uhrzeiten der Reihe nach
  if all(v == "N/A" for v in times_dict.values()):
    all_times = re.findall(r"\b([0-2]\d:[0-5]\d)\b", response.text)
    unique_times = []
    for t in all_times:
      if t not in unique_times:
        unique_times.append(t)

    for idx, name in enumerate(prayer_names):
      if idx < len(unique_times):
        times_dict[name] = unique_times[idx]

  prayer_data = {
      "mosque": "Al-Birr Schwalbach",
      "source_url": URL,
      "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "date_gregorian": datetime.now().strftime("%Y-%m-%d"),
      "times": times_dict,
  }

  return prayer_data


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
