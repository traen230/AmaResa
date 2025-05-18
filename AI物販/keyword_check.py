# ================================================================
# keyword_check.py
#
# 概要:
# このスクリプトは、指定されたキーワードを Amazon で検索し、
# 評価数と販売数の条件（クライテリア）に基づいてライバル候補を判定し、
# CSV に出力するバッチ処理ロジックを提供します。
# また、SellerSprite API を使用してトラフィック順位・比率も取得します。
#
# 必須構成:
# - ChromeDriver のパス指定が必要
# - SellerSprite API のシークレットキーを環境変数で取得するか、直接埋め込み可能
# - 拡張機能 (SellerSprite拡張) のパスを指定
# ================================================================

import csv
import time
from datetime import datetime
from urllib.parse import quote
from tkinter import messagebox, filedialog, Tk, Toplevel, Label, Button, Entry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import os

REVIEW_THRESHOLD = 20
SALES_THRESHOLD = 70
SELLERSPRITE_SECRET_KEY = "a8e88da3d9e84c0eb7824cf32d9b1848"

# 🔧 ChromeDriver / Extension パス設定
def get_chromedriver_path():
    return r"C:\\Users\\SOICHIRO SAHARA\\Documents\\BizBright\\04 Script\\99 temp\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

def get_extension_path():
    return r"C:\\Users\\SOICHIRO SAHARA\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions\\lnbmbgocenenhhhdojdielgnmeflbnfb\\4.7.7_0"

def launch_driver():
    chrome_driver_path = get_chromedriver_path()
    extension_path = get_extension_path()

    print(f"[INFO] ChromeDriver パス: {chrome_driver_path}")
    print(f"[INFO] 拡張機能パス: {extension_path}")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--load-extension={extension_path}")

    if not os.path.exists(chrome_driver_path):
        raise FileNotFoundError(f"ChromeDriver が見つかりません: {chrome_driver_path}")

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def set_rival_criteria(review_threshold=20, sales_threshold=70):
    global REVIEW_THRESHOLD, SALES_THRESHOLD
    REVIEW_THRESHOLD = review_threshold
    SALES_THRESHOLD = sales_threshold

def get_keyword_rank_in_traffic(asin: str, keyword: str):
    url = "https://api.sellersprite.com/v1/traffic/keyword"
    headers = {
        "secret-key": SELLERSPRITE_SECRET_KEY,
        "Content-Type": "application/json;charset=UTF-8"
    }
    payload = {
        "marketplace": "JP",
        "asin": asin
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            items = data["data"].get("items", [])
            for i, item in enumerate(items):
                if item.get("keyword", "").strip() == keyword.strip():
                    rank = str(i + 1)
                    percentage = f"{(item.get('trafficPercentage') or 0) * 100:.2f}%"
                    return rank, percentage
        return "-", "-"
    except:
        return "-", "-"

def show_topmost_message(title, message):
    top = Tk()
    top.withdraw()
    msg = Toplevel()
    msg.title(title)
    msg.attributes("-topmost", True)
    Label(msg, text=message, padx=20, pady=10).pack()
    Button(msg, text="OK", command=lambda: (msg.destroy(), top.quit())).pack(pady=5)
    msg.grab_set()
    top.mainloop()

def ask_input_method():
    result = {"choice": None, "keyword": None}

    def select_file():
        result["choice"] = "file"
        win.destroy()

    def enter_keyword():
        def save_keyword():
            result["keyword"] = entry.get()
            result["choice"] = "manual"
            input_win.destroy()
            win.destroy()

        input_win = Toplevel(win)
        input_win.title("キーワード入力")
        Label(input_win, text="キーワードを入力してください:").pack(padx=10, pady=5)
        entry = Entry(input_win)
        entry.pack(padx=10, pady=5)
        Button(input_win, text="OK", command=save_keyword).pack(pady=10)

    win = Tk()
    win.title("入力方法選択")
    Label(win, text="入力方法を選択してください:").pack(padx=20, pady=10)
    Button(win, text="CSVファイルから読込", command=select_file).pack(padx=10, pady=5)
    Button(win, text="キーワードを手入力", command=enter_keyword).pack(padx=10, pady=5)
    win.mainloop()

    return result

def run_keyword_check(keyword, driver, show_dialog=True):
    try:
        url = f"https://www.amazon.co.jp/s?k={quote(keyword)}"
        driver.get(url)

        if show_dialog:
            show_topmost_message("キーワード確認", f"🔍 キーワード '{keyword}' に遷移しました。拡張機能の表示が完了したら『OK』を押してください。")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.select("div.s-result-item[data-asin]")

        sales_blocks = soup.find_all("div", class_="font-ext-13")
        sales_data = []
        for div in sales_blocks:
            if "直近30日販売数（親）" in div.get_text(strip=True):
                span = div.find("span", class_="exts-color-border-black")
                if span:
                    sales_data.append(span.get_text(strip=True))

        output = []
        rival_count = 0

        for i, item in enumerate(items):
            rank = i + 1
            title_el = item.select_one("h2 span")
            title = title_el.get_text(strip=True) if title_el else "N/A"

            link_el = item.find("a", href=True)
            product_url = "https://www.amazon.co.jp" + link_el["href"] if link_el else "N/A"

            asin = item.get("data-asin", "N/A")

            rating_el = item.select_one(".a-icon-alt")
            rating = rating_el.get_text(strip=True).replace("5つ星のうち", "") if rating_el else "N/A"

            review_el = item.select_one(".a-size-base.s-underline-text")
            review_count = review_el.get_text(strip=True).replace(",", "") if review_el else "N/A"

            img_el = item.select_one("img.s-image")
            image_url = img_el["src"] if img_el else "N/A"

            sales = sales_data[i] if i < len(sales_data) else "N/A"

            remark = ""
            traffic_rank = ""
            traffic_percentage = ""

            try:
                if review_count.isdigit() and sales.isdigit():
                    if int(review_count) <= REVIEW_THRESHOLD and int(sales) >= SALES_THRESHOLD:
                        remark = "ライバル候補"
                        traffic_rank, traffic_percentage = get_keyword_rank_in_traffic(asin, keyword)
                        rival_count += 1
            except:
                pass

            output.append([
                rank, asin, title, product_url, image_url, review_count, rating, sales, remark, traffic_rank, traffic_percentage
            ])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = keyword.replace("/", "_")
        csv_path = f"amazonキーワード分析_{safe_keyword}_{timestamp}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["順位", "ASIN", "商品名", "商品URL", "画像URL", "評価数", "評価値", "直近30日販売数（親）", "ライバル候補", "トラフィック順位", "トラフィック比率"])
            writer.writerows(output)

        print(f"✅ {keyword} のデータ取得完了 → {csv_path}")
        return csv_path, rival_count

    except Exception as e:
        print(f"[エラー] キーワード '{keyword}' の調査中に例外発生: {e}")
        return None, 0

def batch_run_from_csv(review_threshold=20, sales_threshold=70, mode="select"):
    set_rival_criteria(review_threshold, sales_threshold)

    if mode == "auto_file":
        root = Tk()
        root.withdraw()
        csv_file = filedialog.askopenfilename(
            title="CSVファイルを選択してください",
            filetypes=[("CSVファイル", "*.csv")]
        )
        if not csv_file:
            print("❌ ファイルが選択されませんでした。処理を終了します。")
            return
        df = pd.read_csv(csv_file, header=None)
        keywords = df.iloc[1:, 0].dropna().tolist()
    elif mode == "select":
        input_method = ask_input_method()
        if input_method["choice"] == "file":
            root = Tk()
            root.withdraw()
            csv_file = filedialog.askopenfilename(
                title="CSVファイルを選択してください",
                filetypes=[("CSVファイル", "*.csv")]
            )
            if not csv_file:
                print("❌ ファイルが選択されませんでした。処理を終了します。")
                return
            df = pd.read_csv(csv_file, header=None)
            keywords = df.iloc[1:, 0].dropna().tolist()
        elif input_method["choice"] == "manual":
            keyword = input_method["keyword"]
            keywords = [keyword]
        else:
            print("❌ 入力が選択されませんでした。処理を終了します。")
            return
    else:
        print(f"❌ 無効なモード '{mode}'")
        return

    if not keywords:
        print("❌ キーワードが見つかりません。処理を終了します。")
        return

    driver = launch_driver()

    results = []
    for keyword in keywords:
        result, _ = run_keyword_check(keyword, driver, show_dialog=True)
        if result:
            results.append(result)
        time.sleep(2)

    driver.quit()
    return results

if __name__ == "__main__":
    set_rival_criteria(review_threshold=20, sales_threshold=70)
    batch_run_from_csv(mode="select")