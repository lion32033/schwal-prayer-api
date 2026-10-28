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

  times_dict = {
      "Fajr": "N/A",
      "Shuruk": "N/A",
      "Dhuhr": "N/A",
      "Asr": "N/A",
      "Maghrib": "N/A",
      "Isha": "N/A",
  }

  # 1. Extrahiere direkt das "times"-Array (Enthält: Fajr, Dhuhr, Asr, Maghrib, Isha)
  # Beispiel im Quelltext: "times":["05:18","12:14","14:47","17:19","18:48"]
  times_match = re.search(r'"times"\s*:\s*\[(.*?)\]', text_content)
  if times_match:
    raw_times = times_match.group(1)
    # Alle Zeiten im Format "HH:MM" herausfiltern
    extracted_times = re.findall(r'"([0-2]\d:[0-5]\d)"', raw_times)

    if len(extracted_times) >= 5:
      times_dict["Fajr"] = extracted_times[0]
      times_dict["Dhuhr"] = extracted_times[1]
      times_dict["Asr"] = extracted_times[2]
      times_dict["Maghrib"] = extracted_times[3]
      times_dict["Isha"] = extracted_times[4]

  # 2. Extrahiere direkt den "shuruq" (Sonnenaufgang)
  # Beispiel im Quelltext: "shuruq":"07:00"
  shuruq_match = re.search(r'"shuruq"\s*:\s*"([0-2]\d:[0-5]\d)"', text_content)
  if shuruq_match:
    times_dict["Shuruk"] = shuruq_match.group(1)

  # Moschee-Namen ermitteln
  name_match = re.search(r'"name"\s*:\s*"([^"]+)"', text_content)
  mosque_name = (
      name_match.group(1).encode().decode("unicode-escape")
      if name_match
      else "مسجد البر - Schwalbach"
  )

  prayer_data = {
      "mosque": mosque_name,
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
