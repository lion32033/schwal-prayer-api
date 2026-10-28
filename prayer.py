from datetime import datetime
import json
import re
from bs4 import BeautifulSoup
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

    # Speichert die Website als Textdatei
    with open(TXT_FILE, "w", encoding="utf-8") as f:
      f.write(response.text)
    print(f"Website erfolgreich als '{TXT_FILE}' gespeichert.")
    return response.text
  except requests.exceptions.RequestException as e:
    print(f"Fehler beim Herunterladen der Seite: {e}")
    return None


def extract_prayer_times(html_content):
  if not html_content:
    return None

  soup = BeautifulSoup(html_content, "html.parser")
  times_dict = {
      "Fajr": "N/A",
      "Shuruk": "N/A",
      "Dhuhr": "N/A",
      "Asr": "N/A",
      "Maghrib": "N/A",
      "Isha": "N/A",
  }

  # Suche nach allen Elementen mit der Klasse "name" (Gebetsnamen)
  name_elements = soup.find_all(class_="name")

  for name_elem in name_elements:
    name_text = name_elem.get_text(strip=True).capitalize()
    parent = name_elem.find_parent()

    if parent:
      # Suche im selben Container nach der Klasse "time"
      time_elem = parent.find(class_="time")
      if time_elem:
        time_text = time_elem.get_text(strip=True)
        if time_text and re.match(r"^[0-2]\d:[0-5]\d$", time_text):
          if name_text in ["Sabah", "Fajr", "Imsak"]:
            if (
                times_dict["Fajr"] == "N/A" and name_text != "Imsak"
            ):  # Bevorzuge Fajr/Sabah vor Imsak falls nötig
              times_dict["Fajr"] = time_text
            elif times_dict["Fajr"] == "N/A":
              times_dict["Fajr"] = time_text
          elif name_text == "Shuruk":
            times_dict["Shuruk"] = time_text
          elif name_text in ["Dohr", "Dhuhr"]:
            times_dict["Dhuhr"] = time_text
          elif name_text in ["Assr", "Asr"]:
            times_dict["Asr"] = time_text
          elif name_text == "Maghrib":
            times_dict["Maghrib"] = time_text
          elif name_text in ["Ishaa", "Isha"]:
            times_dict["Isha"] = time_text

  # Fallback, falls die Klassenstruktur dynamisch abweichen sollte
  if all(v == "N/A" for v in times_dict.values()):
    lines = [line.strip() for line in soup.get_text().splitlines() if line.strip()]
    for i, line in enumerate(lines):
      l_upper = line.upper()
      if i + 1 < len(lines):
        next_line = lines[i + 1]
        if re.match(r"^[0-2]\d:[0-5]\d$", next_line):
          if l_upper in ["SABAH", "FAJR"]:
            times_dict["Fajr"] = next_line
          elif "SHURUK" in l_upper:
            times_dict["Shuruk"] = next_line
          elif l_upper in ["DOHR", "DHUHR"]:
            times_dict["Dhuhr"] = next_line
          elif l_upper in ["ASSR", "ASR"]:
            times_dict["Asr"] = next_line
          elif "MAGHRIB" in l_upper:
            times_dict["Maghrib"] = next_line
          elif l_upper in ["ISHAA", "ISHA"]:
            times_dict["Isha"] = next_line

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
