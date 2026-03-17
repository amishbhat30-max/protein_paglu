import requests
import os

PINCODE = os.environ.get("PINCODE")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

PRODUCTS = {
    "Pack of 8": "amul-high-protein-blueberry-shake-200-ml-or-pack-of-8",
    "Pack of 30": "amul-high-protein-blueberry-shake-200-ml-or-pack-of-30"
}


def check_stock(alias):
    url = "https://shop.amul.com/api/1/entity/ms.products"

    params = {
        "q": f'{{"alias":"{alias}"}}',
        "limit": 1
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "referer": "https://shop.amul.com/",
        "origin": "https://shop.amul.com"
    }

    session = requests.Session()

    try:
        # 🔥 STEP 1: Warmup request (important)
        session.get("https://shop.amul.com/", headers=headers, timeout=10)

        # 🔥 STEP 2: Actual API call
        res = session.get(
            url,
            params=params,
            headers=headers,
            cookies={"pincode": PINCODE},
            timeout=10
        )

        print("Status:", res.status_code)

        if res.status_code != 200 or not res.text.strip():
            print("Empty or bad response")
            return False

        # 🔥 SAFE JSON PARSE
        try:
            data = res.json()
        except Exception:
            print("Blocked response:", res.text[:200])
            return False

        product = data["data"][0]

        available = product.get("available", 0)
        quantity = product.get("inventory_quantity", 0)

        print(f"{alias} → available: {available}, qty: {quantity}")

        return available > 0 or quantity > 0

    except Exception as e:
        print("Error:", e)
        return False


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})


def main():
    alerts = []

    for name, alias in PRODUCTS.items():
        if check_stock(alias):
            alerts.append(f"✅ {name} IN STOCK\nhttps://shop.amul.com/en/product/{alias}")

    if alerts:
        send_telegram("🚀 Amul Protein Shake Available!\n\n" + "\n\n".join(alerts))
    else:
        print("All out of stock.")


if __name__ == "__main__":
    main()
