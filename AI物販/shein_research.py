import csv
import time
import subprocess
import os
import re
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from bs4 import BeautifulSoup

log_callback = None
driver = None

def set_log_callback(callback):
    global log_callback
    log_callback = callback

def log(msg):
    if log_callback:
        log_callback(msg)
    else:
        print(msg)

# Edgeプロセス強制終了
def kill_edge_processes():
    try:
        subprocess.run("taskkill /F /IM msedge.exe /T", check=False, stdout=subprocess.DEVNULL)
        subprocess.run("taskkill /F /IM msedgedriver.exe /T", check=False, stdout=subprocess.DEVNULL)
        log("🪟 Edge 関連プロセスをすべて強制終了しました")
    except Exception as e:
        log(f"[警告] Edge 強制終了に失敗: {e}")

# WebDriver起動（ログイン済みプロファイル使用）
def setup_webdriver():
    global driver
    EDGEDRIVER = r"C:\\Users\\SOICHIRO SAHARA\\Documents\\BizBright\\04 Script\\Amazon\\AI物販\\resources\\msedgedriver.exe"
    EDGEUSERDATA = r"C:\\Users\\SOICHIRO SAHARA\\AppData\\Local\\Microsoft\\Edge\\User Data"
    PROFILE = "Default"

    options = EdgeOptions()
    options.add_argument(f"--user-data-dir={EDGEUSERDATA}")
    options.add_argument(f"--profile-directory={PROFILE}")
    options.add_argument("--start-maximized")

    # ✅ User-Agent 明示
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
    )

    service = EdgeService(executable_path=EDGEDRIVER)
    driver = webdriver.Edge(service=service, options=options)


# 商品リサーチメイン（CSV or 手入力選択）
def run_shein_scraper():
    def on_manual():
        root.destroy()
        get_search_keyword(run_shein_scraper_from_keyword)

    def on_csv():
        root.destroy()
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            run_shein_scraper_from_csv(path)

    root = tk.Tk()
    root.title("SHEINリサーチモード選択")
    tk.Label(root, text="リサーチ方法を選んでください：").pack(padx=20, pady=10)
    tk.Button(root, text="キーワードを手入力して検索", width=40, command=on_manual).pack(pady=5)
    tk.Button(root, text="CSVファイルから一括検索", width=40, command=on_csv).pack(pady=5)
    root.mainloop()

# 手入力用
def get_search_keyword(on_submit_callback):
    def submit():
        value = entry.get().strip()
        root.destroy()
        if value:
            on_submit_callback(value)

    root = tk.Tk()
    root.title("キーワード入力")
    tk.Label(root, text="検索キーワードを入力してください（例：筆箱）：").pack(padx=20, pady=10)
    entry = tk.Entry(root, width=40)
    entry.pack(padx=20)
    entry.focus()
    tk.Button(root, text="検索開始", command=submit).pack(pady=10)
    root.mainloop()

# キーワード単体処理
def run_shein_scraper_from_keyword(keyword):
    kill_edge_processes()
    setup_webdriver()
    log(f"🔍 キーワード「{keyword}」で検索中...")
    results = get_search_results(keyword)
    filename = time.strftime(f"SHEIN_{keyword}_%Y%m%d_%H%M%S.csv")
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['商品名', '販売数', '商品URL', '画像URL'])
        writer.writerows(results)
    log(f"✅ 完了：{filename} に保存しました")
    driver.quit()

# 複数キーワードCSV処理
def run_shein_scraper_from_csv(path):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # ヘッダスキップ
            keywords = [row[0].strip() for row in reader if row]
    except Exception as e:
        log(f"❌ CSV読み込みエラー: {e}")
        return

    kill_edge_processes()
    setup_webdriver()

    for i, keyword in enumerate(keywords, 1):
        try:
            log(f"[{i}/{len(keywords)}] 🔍 キーワード「{keyword}」で検索中...")
            results = get_search_results(keyword)
            filename = time.strftime(f"SHEIN_{keyword}_%Y%m%d_%H%M%S.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(['商品名', '販売数', '商品URL', '画像URL'])
                writer.writerows(results)
            log(f"✅ 完了：{filename} に保存しました")
            time.sleep(3)
        except Exception as e:
            log(f"❌ キーワード「{keyword}」の処理中にエラー: {e}")

    driver.quit()

# 実際の商品情報スクレイピング処理
def get_search_results(keyword):
    search_url = f"https://jp.shein.com/pdsearch/{keyword}/"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='S-product-card__img-container']"))
        )
    except:
        log("⚠ 商品カードが表示されませんでした")
        return []

    for _ in range(10):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_data = []
    seen = set()

    cards = soup.select("a[class*='S-product-card__img-container']")
    sales_candidates = []
    for card in cards:
        try:
            parent_div = card.find_parent("div")
            if parent_div:
                sold_tag = parent_div.find_next(string=lambda t: t and 'sold' in t)
                sales_text = sold_tag.strip() if sold_tag else "N/A"
            else:
                sales_text = "N/A"
        except:
            sales_text = "N/A"
        sales_candidates.append(sales_text)

    for card in cards:
        try:
            href = card.get("href")
            product_url = urljoin("https://jp.shein.com", href)
            title = card.get("aria-label") or card.get("data-title") or "N/A"

            if product_url in seen:
                continue
            seen.add(product_url)

            try:
                img = card.select_one("img")
                image_url = img.get("src") or img.get("data-src")
            except:
                image_url = "N/A"

            try:
                sales_raw = sales_candidates[len(product_data)].strip() if len(sales_candidates) > len(product_data) else "N/A"
                match = re.search(r"([\d\.]+)([kK]?)\s*\+?\s*sold", sales_raw)
                if match:
                    num = float(match.group(1))
                    sales_text = int(num * 1000) if match.group(2).lower() == 'k' else int(num)
                else:
                    sales_text = "N/A"
            except:
                sales_text = "N/A"

            product_data.append([title, sales_text, product_url, image_url])

            if len(product_data) >= 50:
                break
        except Exception as e:
            log(f"[SKIP] 商品情報取得エラー: {e}")
            continue

    return product_data
