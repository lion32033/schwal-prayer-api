from datetime import datetime
import json
import re
import requests

URL = "https://mawaqit.net/de/m/albir-schwalbach"
TXT_FILE = "mawaqit_page.txt"
JSON_FILE = "prayer-schwal.json"


def download_and_save_txt():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/122.0.0.0 Safari/537.36"
      )
  }
  print(f"Lade Seite herunter von: {URL}")
  try:
    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()

    # Speichert die Website als reine Textdatei im Projektordner
    with open(TXT_FILE, "w", encoding="utf-8") as f:
      f.write(response.text)
    print(f"Website erfolgreich als '{TXT_FILE}' gespeichert.")
    return response.text
  except requests.exceptions.RequestException as e:
    print(f"Fehler beim Herunterladen der Seite: {e}")
    return None


def extract_prayer_times(text_content):
  if not text_content:
    return None

  prayer_names = ["Fajr", "Shuruk", "Dhuhr", "Asr", "Maghrib", "Isha"]
  times_dict = {}

  # Extrahiert alle Uhrzeiten im Format HH:MM aus dem Text
  all_times = re.findall(r"\b([0-2]\d:[0-5]\d)\b", text_content)

  # Duplikate filtern, Reihenfolge beibehalten
  unique_times = []
  for t in all_times:
    if t not in unique_times:
      unique_times.append(t)

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
      "times": times_dict,
  }

  return prayer_data


def save_to_json(data):
  if not data or not data.get("times"):
    print("Keine gültigen Zeiten zum Speichern vorhanden.")
    return
  with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
  print(f"Daten erfolgreich in '{JSON_FILE}' gespeichert.")


if __name__ == "__main__":
  page_text = download_and_save_txt()
  if page_text:
    parsed_data = extract_prayer_times(page_text)
    save_to_json(parsed_data)
