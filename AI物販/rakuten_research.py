import tkinter as tk
from tkinter import filedialog
import pandas as pd
import csv
import time
import os
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Edgeを強制終了する関数
def kill_edge():
    subprocess.run("taskkill /F /IM msedge.exe /T", check=False, stdout=subprocess.DEVNULL)
    subprocess.run("taskkill /F /IM msedgedriver.exe /T", check=False, stdout=subprocess.DEVNULL)

# ✅ Edgeブラウザ起動（プロファイルなし）
def start_browser():
    EDGEDRIVER = r"C:\\Users\\SOICHIRO SAHARA\\Documents\\BizBright\\04 Script\\Amazon\\AI物販\\resources\\msedgedriver.exe"
    options = EdgeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Edge(service=EdgeService(EDGEDRIVER), options=options)

# ✅ 商品ページからランキング情報を取得
def check_ranking_status(driver, product_url):
    try:
        driver.get(product_url)
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.ID, "rnkInShopRankBox"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ranking_links = soup.select("div#rnkInShopRankBox a[href*='item.rakuten.co.jp']")
        base_url = product_url.split("?", 1)[0]
        for a in ranking_links:
            if base_url in a.get("href", ""):
                return "有"
        return "無"
    except:
        return "N/A"

# ✅ メイン処理関数（上位30件取得し、CSV保存＋ランキング列追加）
def run_rakuten_scraper(keyword):
    kill_edge()
    browser = start_browser()
    browser.get(f"https://search.rakuten.co.jp/search/mall/{keyword}/")
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.title-link--3Yuev"))
    )
    for _ in range(10):
        browser.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.3)

    soup = BeautifulSoup(browser.page_source, 'html.parser')
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
            results.append([title, review, url, img_url, rating])
            if len(results) >= 30:
                break
        except Exception as e:
            print(f"[SKIP] {e}")
            continue

    filename = time.strftime(f"Rakuten_{keyword}_%Y%m%d_%H%M%S.csv")

    # ✅ ランキング列追加
    updated_rows = []
    for i, row in enumerate(results, 1):
        try:
            status = check_ranking_status(browser, row[2])
        except:
            status = "N/A"
        updated_rows.append(row + [status])
        print(f"[{i}/{len(results)}] ランキング: {status}")

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['商品名', '評価数', '商品URL', '画像URL', '評価値', 'ランキング'])
        writer.writerows(updated_rows)

    print(f"✅ 完了：{filename} に保存しました")
    browser.quit()

# ✅ CSVファイルからキーワードを取得して実行（A列2行目以降）
def run_from_csv(filepath):
    df = pd.read_csv(filepath, header=None)
    keywords = df.iloc[1:, 0].dropna().astype(str).tolist()
    for keyword in keywords:
        print(f"\n🔍 キーワード：{keyword}")
        run_rakuten_scraper(keyword)

# ✅ GUIメニュー（手入力かCSV選択）
def keyword_input_gui():
    def run_manual():
        root.destroy()
        keyword = simple_input_gui()
        if keyword:
            run_rakuten_scraper(keyword)

    def run_csv():
        root.destroy()
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filepath:
            run_from_csv(filepath)

    root = tk.Tk()
    root.title("楽天リサーチモード選択")
    tk.Label(root, text="リサーチ方法を選択してください", font=("メイリオ", 11)).pack(padx=20, pady=15)

    tk.Button(root, text="キーワードを手入力して検索", font=("メイリオ", 10), width=30, command=run_manual).pack(pady=5)
    tk.Button(root, text="CSVからキーワード読み込み", font=("メイリオ", 10), width=30, command=run_csv).pack(pady=5)

    root.mainloop()

# ✅ 手入力用の小ウィンドウ
def simple_input_gui():
    result = {"keyword": None}

    def submit():
        result["keyword"] = entry.get().strip()
        popup.destroy()

    popup = tk.Tk()
    popup.title("キーワード入力")
    tk.Label(popup, text="検索するキーワードを入力してください：", font=("メイリオ", 10)).pack(padx=20, pady=10)
    entry = tk.Entry(popup, width=40)
    entry.pack(padx=20)
    entry.focus()
    tk.Button(popup, text="検索開始", font=("メイリオ", 10), command=submit).pack(pady=10)
    popup.mainloop()

    return result["keyword"]

# ✅ PyQt5側から呼び出すためのエントリーポイント
def choose_keyword_and_run():
    keyword_input_gui()
