from datetime import datetime
import json
import os
import re
from bs4 import BeautifulSoup
import requests

URL = "https://mawaqit.net/de/m/albir-schwalbach"
HTML_FILE = "mawaqit_page.html"
JSON_FILE = "prayer-schwal.json"


def download_and_save_html():
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

    with open(HTML_FILE, "w", encoding="utf-8") as f:
      f.write(response.text)
    print(f"HTML erfolgreich als '{HTML_FILE}' gespeichert.")
    return response.text
  except requests.exceptions.RequestException as e:
    print(f"Fehler beim Herunterladen der Seite: {e}")
    return None


def extract_prayer_times(html_content):
  if not html_content:
    return None

  soup = BeautifulSoup(html_content, "html.parser")
  prayer_names = ["Fajr", "Shuruk", "Dhuhr", "Asr", "Maghrib", "Isha"]
  times_dict = {}

  # Mawaqit bettet die Daten in JavaScript-Objekte innerhalb von <script>-Tags ein.
  # Wir durchsuchen daher alle Skripte und den gesamten Text nach Uhrzeiten.
  combined_text = ""
  for script in soup.find_all("script"):
    if script.string:
      combined_text += script.string + "\n"
  combined_text += soup.get_text()

  # Suche nach allen Uhrzeiten im Format HH:MM
  all_times = re.findall(r"\b([0-2]\d:[0-5]\d)\b", combined_text)

  # Duplikate entfernen, aber die Reihenfolge beibehalten
  unique_times = []
  for t in all_times:
    if t not in unique_times:
      # Filterung von unrealistischen Zeiten (optional, falls z.B. Uhrzeiten wie 00:00 oder ähnliches auftauchen)
      unique_times.append(t)

  # Die ersten 6 gefundenen, relevanten Zeiten zuordnen
  # Mawaqit listet im Nuxt-State oft zuerst die Zeiten für den Monat auf. 
  # Wir greifen hier auf die ersten 6 eindeutigen Zeiten zu.
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
  html_data = download_and_save_html()
  if html_data:
    parsed_data = extract_prayer_times(html_data)
    save_to_json(parsed_data)
