import requests
import json
import os

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

def check_ipos():
    url = "https://www.nseindia.com/api/ipo-current-issue"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    ipos = response.json()

    alerted = load_alerted()

    for ipo in ipos:
        try:
            name = ipo["companyName"]
            issue_size = float(ipo["issueSize"].replace(",", ""))
            status = ipo["status"].lower()

            if status == "open" and issue_size >= 77 and name not in alerted:
                message = (
                    "📢 BIG IPO OPEN\n\n"
                    f"Name: {name}\n"
                    f"Issue Size: ₹{issue_size} Cr\n"
                    f"Dates: {ipo['issueStartDate']} → {ipo['issueEndDate']}"
                )
                send_telegram(message)
                alerted.append(name)
        except:
            continue

    save_alerted(alerted)

check_ipos()
