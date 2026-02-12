# rakuten_scraper.py
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

def run_rakuten_scraper(keyword):
    setup_webdriver()

    search_url = f"https://search.rakuten.co.jp/search/mall/{keyword}/"
    driver.get(search_url)

    logs = []
    time.sleep(1)  # ページ安定のための初期待機

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.title-link--3Yuev"))
        )
    except:
        logs.append("⚠ 商品リンクが見つかりませんでした")
        return "", []

    for _ in range(10):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.5)

    time.sleep(3)  # スクロール後の安定待機

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    items = soup.select("a.title-link--3Yuev")
    results, seen = [], set()

    for item in items:
        try:
            title = item.get("title", "").strip() or item.get_text(strip=True)
            url = item.get("href")
            if not title or not url or url in seen:
                continue
            seen.add(url)
            parent = item.find_parent("div", class_="searchresultitem") or item.parent
            img = parent.select_one("img")
            img_url = img.get("src") if img else "N/A"
            review_elem = parent.select_one("span.legend")
            review = review_elem.text.replace("(", "").replace("件)", "") if review_elem else "N/A"
            score_elem = parent.select_one("span.score")
            rating = score_elem.text.strip() if score_elem else "N/A"

            # ランキングチェック（ページ内に同一商品URLがあれば「有」）
            driver.get(url)
            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "rnkInShopRankBox")))
            detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
            rank_box_links = detail_soup.select("#rnkInShopRankBox a[href]")
            is_ranked = "無"
            for link in rank_box_links:
                if url.split("?")[0] in link.get("href", ""):
                    is_ranked = "有"
                    break

            results.append([title, review, url, img_url, rating, is_ranked])

            if len(results) >= 20:
                break
        except Exception as e:
            print(f"[SKIP] {e}")
            continue

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"Rakuten_{keyword}_{timestamp}.csv"
    filepath = os.path.join("rival_outputs", filename)
    os.makedirs("rival_outputs", exist_ok=True)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['商品名', '評価数', '商品URL', '画像URL', '評価値', 'ランキング'])
        writer.writerows(results)

    return filepath, results
