import requests
import json
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

ALERT_FILE = "alerted_ipos.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def load_alerted():
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "r") as f:
            return json.load(f)
    return []

def save_alerted(data):
    with open(ALERT_FILE, "w") as f:
        json.dump(data, f)

def parse_issue_size(text):
    """
    Converts '₹1,200 Cr' or '120 Cr' to float
    """
    text = text.replace("₹", "").replace("Cr", "").replace(",", "").strip()
    return float(text)

def check_chittorgarh():
    url = "https://www.chittorgarh.com/ipo/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")
    alerted = load_alerted()

    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            name = cols[0].get_text(strip=True)
            issue_size_text = cols[2].get_text(strip=True)
            status = cols[5].get_text(strip=True).lower()
            dates = cols[4].get_text(strip=True)

            try:
                issue_size = parse_issue_size(issue_size_text)
            except:
                continue

            if (
                status == "open"
                and issue_size >= 70
                and name not in alerted
            ):
                message = (
                    "📢 IPO OPEN (Chittorgarh)\n\n"
                    f"Name: {name}\n"
                    f"Issue Size: ₹{issue_size} Cr\n"
                    f"Dates: {dates}"
                )
                send_telegram(message)
                alerted.append(name)

    save_alerted(alerted)

check_chittorgarh()
