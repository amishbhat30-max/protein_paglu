from playwright.sync_api import sync_playwright
import requests
import os

PINCODE = os.environ.get("PINCODE")
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

PRODUCTS = {
    "Pack of 8": "https://shop.amul.com/en/product/amul-high-protein-blueberry-shake-200-ml-or-pack-of-8",
    "Pack of 30": "https://shop.amul.com/en/product/amul-high-protein-blueberry-shake-200-ml-or-pack-of-30"
}


def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


def set_pincode(page):
    try:
        page.goto("https://shop.amul.com", timeout=60000)

        # small wait instead of networkidle
        page.wait_for_timeout(3000)

        # try clicking before typing (handles modal)
        try:
            page.click('input', timeout=3000)
        except:
            pass

        page.fill('input', PINCODE)
        page.keyboard.press("Enter")

        page.wait_for_timeout(3000)
        print("Pincode set")

    except Exception as e:
        print("Pincode setup failed:", e)


def check_stock(context, name, url):
    page = context.new_page()  # fresh page each time

    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(4000)

        content = page.content().lower()

        if "sold out" in content or "notify me" in content:
            print(f"{name}: OUT OF STOCK")
            return False

        if "add to cart" in content:
            print(f"{name}: IN STOCK")
            return True

        print(f"{name}: UNKNOWN")
        return False

    except Exception as e:
        print(f"{name}: ERROR → {e}")
        return False

    finally:
        page.close()


def main():
    alerts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()

        # set pincode once
        page = context.new_page()
        set_pincode(page)
        page.close()

        for name, url in PRODUCTS.items():
            if check_stock(context, name, url):
                alerts.append(f"✅ {name} IN STOCK\n{url}")

        browser.close()

    if alerts:
        send_telegram("🚀 Amul Stock Available!\n\n" + "\n\n".join(alerts))
    else:
        print("All out of stock.")


if __name__ == "__main__":
    main()
