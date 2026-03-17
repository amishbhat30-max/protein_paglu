import requests
from bs4 import BeautifulSoup
import os
import json

PRODUCTS = {
    "Pack of 30": "https://shop.amul.com/en/product/amul-high-protein-blueberry-shake-200-ml-or-pack-of-30",
    "Pack of 8": "https://shop.amul.com/en/product/amul-high-protein-blueberry-shake-200-ml-or-pack-of-8"
}

PINCODE = os.environ.get("PINCODE")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

STATE_FILE = "state.json"


def get_headers():
    return {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-IN,en;q=0.9",
    }


def get_cookies():
    # This is the key for location-specific stock
    return {
        "pincode": PINCODE
    }


def check_stock(url):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-IN,en;q=0.9",
    }

    try:
        # Step 1: Load homepage to establish session
        session.get("https://shop.amul.com/", headers=headers, timeout=10)

        # Step 2: Set pincode cookie (more realistic)
        session.cookies.set("pincode", PINCODE)

        # Step 3: Fetch product page
        res = session.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        text = soup.get_text().lower()

        # DEBUG (important)
        print("Checking:", url)
        print("Snippet:", text[:500])

        if "sold out" in text or "notify me" in text:
            return False

        # Extra safety: ensure Add to Cart exists
        if "add to cart" in text:
            return True

        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    state = load_state()
    new_state = {}

    alerts = []

    for name, url in PRODUCTS.items():
        in_stock = check_stock(url)
        new_state[name] = in_stock

        prev = state.get(name, False)

        # Alert only when it becomes available
        if in_stock and not prev:
            alerts.append(f"✅ {name} is IN STOCK\n{url}")

    if alerts:
        message = "🚀 Amul Blueberry Protein Shake Available!\n\n" + "\n\n".join(alerts)
        send_telegram(message)
        print("Alert sent!")
    else:
        print("No change.")

    save_state(new_state)


if __name__ == "__main__":
    main()
