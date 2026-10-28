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

    # Speichert den Quelltext als Textdatei ab
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

  # Suche im Text nach dem JavaScript-Objekt 'var confData = {...};'
  match = re.search(r"var\s+confData\s*=\s*(\{.*?\});", text_content, re.DOTALL)
  if not match:
    print(
        "Fehler: 'confData' konnte im heruntergeladenen Text nicht gefunden"
        " werden."
    )
    return None

  try:
    conf_data = json.loads(match.group(1))

    # 'times' enthält standardmäßig [Fajr, Dhuhr, Asr, Maghrib, Isha]
    times_array = conf_data.get("times", [])
    shuruq_time = conf_data.get("shuruq", "N/A")

    # Zeiten sicher zuordnen
    fajr = times_array[0] if len(times_array) > 0 else "N/A"
    dhuhr = times_array[1] if len(times_array) > 1 else "N/A"
    asr = times_array[2] if len(times_array) > 2 else "N/A"
    maghrib = times_array[3] if len(times_array) > 3 else "N/A"
    isha = times_array[4] if len(times_array) > 4 else "N/A"

    times_dict = {
        "Fajr": fajr,
        "Shuruk": shuruq_time,
        "Dhuhr": dhuhr,
        "Asr": asr,
        "Maghrib": maghrib,
        "Isha": isha,
    }

    prayer_data = {
        "mosque": conf_data.get("name", "Al-Birr Schwalbach"),
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
