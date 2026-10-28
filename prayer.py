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

    # Speichert die Website als reine Textdatei
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

  lines = [line.strip() for line in text_content.splitlines() if line.strip()]

  # 1. Suche zeilenbasiert nach dem Gebetsnamen und der direkt folgenden Uhrzeit
  for i, line in enumerate(lines):
    l_upper = line.upper()

    # Prüfen, ob die nächste Zeile eine gültige Uhrzeit (HH:MM) ist
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

  # 2. Fallback: Falls Werte fehlen, in derselben Zeile suchen (z.B. "Shuruk 07:02")
  for line in lines:
    for name, keys in [
        ("Fajr", ["Sabah", "Fajr"]),
        ("Shuruk", ["Shuruk"]),
        ("Dhuhr", ["Dohr", "Dhuhr"]),
        ("Asr", ["Assr", "Asr"]),
        ("Maghrib", ["Maghrib"]),
        ("Isha", ["Ishaa", "Isha"]),
    ]:
      if times_dict[name] == "N/A":
        for k in keys:
          match = re.search(rf"\b{k}\b\D+([0-2]\d:[0-5]\d)", line, re.IGNORECASE)
          if match:
            times_dict[name] = match.group(1)

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
