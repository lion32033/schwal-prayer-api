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

    # Speichert den Quelltext als Textdatei
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

  # Suchen nach dem confData-Objekt im Text
  match = re.search(r"var\s+confData\s*=\s*(\{.*?\});", text_content, re.DOTALL)
  if not match:
    print(
        "Fehler: 'confData' konnte im heruntergeladenen Text nicht gefunden"
        " werden."
    )
    return None

  try:
    conf_text = match.group(1)
    # Da das JSON im Quelltext manchmal unvollständig abgeschnitten sein kann,
    # säubern wir es oder laden es direkt per eval/json.
    # Bei Mawaqit ist confData ein valides JSON-Objekt.
    conf_data = json.loads(conf_text)

    # Ermittle den heutigen Tag als String (z.B. "28")
    today_day_str = str(datetime.now().day)
    calendar = conf_data.get("calendar", [])

    times_dict = {}

    # Mawaqit speichert den Kalender oft als Liste von Dictionaries oder als Array.
    # Schauen wir nach dem heutigen Tag im Kalender:
    found_day_times = None
    if isinstance(calendar, list):
      for entry in calendar:
        # entry ist z.B. {"1": ["06:25", ...]}
        if isinstance(entry, dict) and today_day_str in entry:
          found_day_times = entry[today_day_str]
          break
    elif isinstance(calendar, dict):
      if today_day_str in calendar:
        found_day_times = calendar[today_day_str]

    # Wenn der Kalender-Eintrag für heute gefunden wurde:
    # Struktur im Kalender-Array: [Fajr, Iqama_Fajr, Shuruq, Dhuhr, Asr, Maghrib, Isha]
    if found_day_times and len(found_day_times) >= 7:
      times_dict = {
          "Fajr": found_day_times[0],
          "Shuruk": found_day_times[2],
          "Dhuhr": found_day_times[3],
          "Asr": found_day_times[4],
          "Maghrib": found_day_times[5],
          "Isha": found_day_times[6],
      }
    else:
      # Fallback auf die allgemeinen heutigen Zeiten im confData
      times_array = conf_data.get("times", [])
      shuruq_time = conf_data.get("shuruq", "N/A")

      times_dict = {
          "Fajr": times_array[0] if len(times_array) > 0 else "N/A",
          "Shuruk": shuruq_time,
          "Dhuhr": times_array[1] if len(times_array) > 1 else "N/A",
          "Asr": times_array[2] if len(times_array) > 2 else "N/A",
          "Maghrib": times_array[3] if len(times_array) > 3 else "N/A",
          "Isha": times_array[4] if len(times_array) > 4 else "N/A",
      }

    prayer_data = {
        "mosque": conf_data.get("name", "مسجد البر - Schwalbach"),
        "source_url": URL,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_gregorian": datetime.now().strftime("%Y-%m-%d"),
        "times": times_dict,
    }

    return prayer_data

  except Exception as e:
    print(f"Fehler beim Parsen der confData: {e}")
    return None


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
