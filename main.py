import time, requests
import config
import os
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

# ================= TELEGRAM =================
def tg_send(msg):
    requests.post(
        f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": config.CHAT_ID, "text": msg}
    )

def tg_ask_close():
    requests.post(
        f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": config.CHAT_ID,
            "text": "❓ Sahifani yopaymi?",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "✅ HA", "callback_data": "close_yes"}],
                    [{"text": "❌ YO‘Q", "callback_data": "close_no"}]
                ]
            }
        }
    )

def wait_user_decision(timeout=120):
    start = time.time()
    r = requests.get(
        f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getUpdates"
    ).json()
    if r.get("result"):
        offset = r["result"][-1]["update_id"] + 1
    else:
        offset = None

    while time.time() - start < timeout:
        r = requests.get(
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getUpdates",
            params={"offset": offset, "timeout": 10}
        ).json()

        for upd in r.get("result", []):
            offset = upd["update_id"] + 1
            if "callback_query" in upd:
                callback = upd["callback_query"]
                requests.post(
                    f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
                    data={"callback_query_id": callback["id"]}
                )
                return callback["data"]
        time.sleep(1)
    return None

# ================= BOT JAVOBINI OLISH =================
def wait_user_decision(timeout=120):
    offset = None
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getUpdates",
            params={"offset": offset, "timeout": 5}
        ).json()
        for upd in r.get("result", []):
            offset = upd["update_id"] + 1
            if "callback_query" in upd:
                return upd["callback_query"]["data"]
        time.sleep(2)
    return None

# ================= CAPTCHA =================
def captcha_detected(driver):
    src = driver.page_source.lower()
    return any(x in src for x in ["captcha", "recaptcha", "hcaptcha", "cloudflare"])

# ======== JSON INIT ========
LOG_FILE = "log.json"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
def write_log(data):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": data
    }

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)

    logs.append(log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


# ================= DRIVER =================
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

driver.get(config.URL)

# ================= JS CLICK =================
def js_click(el):
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", el
    )
    time.sleep(0.4)
    driver.execute_script("arguments[0].click();", el)

# ================= FROM =================
from_header = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//span[text()='Qayerdan']/..")
    )
)
js_click(from_header)

station_from = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, f"//li[contains(text(),\"{config.FROM_STATION}\")]")
    )
)
js_click(station_from)

# ================= TO =================
to_header = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//span[text()='Qayerga']/..")
    )
)
js_click(to_header)

station_to = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, f"//li[contains(text(),\"{config.TO_STATION}\")]")
    )
)
js_click(station_to)

# ================= SANA =================
calendar_btn = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.choose-date"))
)
js_click(calendar_btn)

TARGET_MONTH = config.MONTH_NAME.strip().lower()

while True:
    month_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ngb-datepicker .ngb-dp-month-name")
        )
    )

    visible_months = [m.text.strip().lower() for m in month_elements]
    print("📅 Ko‘rinayotgan oylar:", visible_months)

    # Agar kerakli oy ko‘rinib turgan bo‘lsa — chiqamiz
    if any(TARGET_MONTH in m for m in visible_months):
        break

    # Aks holda oldingi oyni bosamiz
    prev_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[aria-label='Previous month']")
        )
    )
    js_click(prev_btn)
    time.sleep(0.7)

# ======== KUN TANLASH ========
day_el = wait.until(
    EC.presence_of_element_located(
        (
            By.XPATH,
            f"//ngb-datepicker//div[@role='gridcell']/div[text()='{config.DAY}']"
        )
    )
)
js_click(day_el)


# ================= SEARCH =================
search_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-search")))
js_click(search_btn)
print("🚆 Poyezdlar qidirilyapti...")

try:
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.direction__item.info")))
except:
    print("⚠️ Dastlab poyezd topilmadi")

print("🚆 Monitoring boshlandi...")

INTERVAL = 5  # sekund (agar daqiqa bo‘lsa *60 qil)
first_run = True
old_wagon_state = set()

while True:

    trains = driver.find_elements(By.CSS_SELECTOR, "li.direction__item.info")

    current_wagon_state = set()
    all_trains_text = ["🚆 POYEZDlar RO‘YXATI\n"]

    if not trains:
        print("❌ Poyezd yo‘q")

    for i, train in enumerate(trains, 1):
        try:
            dep = train.find_element(
                By.XPATH, ".//div[contains(text(),'Ketish')]/following-sibling::div"
            ).text.strip()

            arr = train.find_element(
                By.XPATH, ".//div[contains(text(),'Yetib')]/following-sibling::div"
            ).text.strip()

            num = train.find_element(
                By.CSS_SELECTOR, ".info__value span.normal-big"
            ).text.strip()

            route = train.find_element(
                By.CSS_SELECTOR, ".train__route"
            ).text.replace("\n", " ").strip()
        except:
            continue

        block = [
            "━━━━━━━━━━━━━━━",
            f"🚆 #{i} | {num}",
            f"🕒 {dep} → {arr}",
            f"📍 {route}",
            ""
        ]

        wagons = train.find_elements(By.CSS_SELECTOR, ".info__item[title]")

        if not wagons:
            continue  # MUHIM: vagon yo‘q bo‘lsa umuman hisobga olinmaydi

        for w in wagons:
            try:
                wagon = w.get_attribute("title").strip()

                seats = w.find_element(
                    By.XPATH, "following-sibling::div[contains(@class,'normal-small')]"
                ).text.strip()

                price = w.find_element(
                    By.XPATH, "following-sibling::div//span[contains(@class,'bold-small')]"
                ).text.strip()

                block.append(f"🚪 {wagon} | 💺 {seats} | 💰 {price} so‘m")

                # 🔑 VAGON + NARX holatini saqlaymiz
                state_key = f"{num}|{wagon}|{price}"
                current_wagon_state.add(state_key)

            except:
                continue

        all_trains_text.append("\n".join(block))

    current_snapshot = "\n\n".join(all_trains_text)

    # ================= TELEGRAM =================
    if first_run:
        tg_send(current_snapshot)
        write_log(current_snapshot)
        old_wagon_state = current_wagon_state.copy()
        first_run = False
        print("📤 Birinchi xabar yuborildi")

    else:
        if not current_wagon_state:
            print("🔕 Vagon (narx) yo‘q — xabar yuborilmadi")

        elif current_wagon_state != old_wagon_state:
            tg_send(current_snapshot)
            write_log(current_snapshot)
            old_wagon_state = current_wagon_state.copy()
            print("📤 Vagon / narx o‘zgarishi topildi")

            tg_ask_close()
            if wait_user_decision() == "close_yes":
                tg_send("🛑 Monitoring to‘xtatildi.")
                driver.quit()
                break
        else:
            print("ℹ️ Vagonlar va narxlar o‘zgarmadi")

    # ======== REFRESH O‘RNIGA SANA BOSISH ========
    try:
        date_el = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "li.close-dates__item.selected")
        ))
        driver.execute_script("arguments[0].click();", date_el)
        print("📅 Sana bosildi, sahifa yangilandi")
        time.sleep(3)
    except:
        print("⚠️ Sana bosilmadi")

    time.sleep(INTERVAL)
