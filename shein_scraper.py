# shein_scraper.py
import csv
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# グローバルWebDriver
driver = None

def setup_webdriver():
    global driver
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 既存Chromeに接続
    driver = webdriver.Chrome(options=options)

def scrape_shein(keyword):
    setup_webdriver()

    search_url = f"https://jp.shein.com/pdsearch/{keyword}/"
    driver.get(search_url)

    logs = []

    time.sleep(1)  # ⭐ スクレイピング開始前に安定のため10秒待機

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.S-product-card__img-container"))
        )
    except:
        logs.append("⚠ 商品カードが表示されませんでした")
        return "", []

    # スクロールして読み込み
    for _ in range(10):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.5)

    time.sleep(3)  # ⭐ スクロール後に安定待ち追加

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_data = []
    seen = set()

    cards = soup.select("a.S-product-card__img-container")

    for card in cards:
        try:
            href = card.get("href")
            product_url = urljoin("https://jp.shein.com", href)
            title = card.get("aria-label") or card.get("data-title") or card.get("title") or card.text.strip() or "N/A"

            if product_url in seen:
                continue
            seen.add(product_url)

            try:
                img = card.select_one("img")
                image_url = img.get("src") or img.get("data-src")
            except:
                image_url = "N/A"

            try:
                # 親の中に"sold"の文字列がある要素を検索
                parent_html = card.find_parent("div")
                sold_element = parent_html.find_next(string=re.compile(r"sold")) if parent_html else None
                if sold_element:
                    match = re.search(r"([\d\.]+)([kK]?)\s*\+?\s*sold", sold_element)
                    if match:
                        num = float(match.group(1))
                        sales_text = int(num * 1000) if match.group(2).lower() == 'k' else int(num)
                    else:
                        sales_text = "N/A"
                else:
                    sales_text = "N/A"
            except:
                sales_text = "N/A"

            product_data.append([title, sales_text, product_url, image_url])

            if len(product_data) >= 20:
                break
        except Exception as e:
            print(f"[SKIP] 商品情報取得エラー: {e}")
            continue

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"SHEIN_{keyword}_{timestamp}.csv"
    filepath = os.path.join("rival_outputs", filename)
    os.makedirs("rival_outputs", exist_ok=True)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['商品名', '販売数', '商品URL', '画像URL'])
        writer.writerows(product_data)

    return filepath, product_data
