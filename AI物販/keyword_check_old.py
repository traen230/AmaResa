# keyword_check.py
# このスクリプトは、指定されたキーワードを Amazon で検索し、評価数と販売数の条件（クライテリア）に基づいてライバル候補を判定し、CSV に出力します。
# また、SellerSprite API を使用してトラフィック順位・比率を取得する分析機能も含まれます。
# PyQt5ダイアログを使って楽天リサーチと統一された操作UIを提供します。

import csv
import time
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json

from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QInputDialog, QFileDialog
)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

REVIEW_THRESHOLD = 20
SALES_THRESHOLD = 70
SELLERSPRITE_SECRET_KEY = "a8e88da3d9e84c0eb7824cf32d9b1848"

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

def ask_input_method_qt():
    app = QApplication([])

    result = {"choice": None, "keyword": None}

    class InputDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("入力方法選択")
            layout = QVBoxLayout()
            layout.addWidget(QLabel("入力方法を選択してください："))

            manual_button = QPushButton("キーワードを手入力")
            csv_button = QPushButton("CSVファイルから読込")

            layout.addWidget(manual_button)
            layout.addWidget(csv_button)

            manual_button.clicked.connect(self.handle_manual)
            csv_button.clicked.connect(self.handle_csv)

            self.setLayout(layout)

        def handle_manual(self):
            keyword, ok = QInputDialog.getText(self, "キーワード入力", "検索キーワードを入力：")
            if ok and keyword.strip():
                result["choice"] = "manual"
                result["keyword"] = keyword.strip()
                self.accept()

        def handle_csv(self):
            result["choice"] = "file"
            self.accept()

    dlg = InputDialog()
    dlg.exec_()
    return result

def run_keyword_check(keyword, driver):
    try:
        url = f"https://www.amazon.co.jp/s?k={quote(keyword)}"
        driver.get(url)

        input("🔍 拡張機能が表示されてからEnterを押してください...")

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

def batch_run_from_csv(review_threshold=20, sales_threshold=70):
    set_rival_criteria(review_threshold, sales_threshold)

    input_method = ask_input_method_qt()
    if input_method["choice"] == "file":
        csv_file, _ = QFileDialog.getOpenFileName(None, "CSVファイルを選択してください", "", "CSV Files (*.csv)")
        if not csv_file:
            print("❌ ファイルが選択されませんでした。")
            return
        df = pd.read_csv(csv_file, header=None)
        keywords = df.iloc[1:, 0].dropna().tolist()
    elif input_method["choice"] == "manual":
        keyword = input_method["keyword"]
        keywords = [keyword]
    else:
        print("❌ 入力方法が選択されませんでした。")
        return

    if not keywords:
        print("❌ キーワードが見つかりません。")
        return

    chrome_driver_path = r"C:\\Users\\SOICHIRO SAHARA\\Documents\\BizBright\\04 Script\\99 temp\\chromedriver-win64\\chromedriver.exe"
    extension_path = r"C:\\Users\\SOICHIRO SAHARA\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions\\lnbmbgocenenhhhdojdielgnmeflbnfb\\4.7.5_0"

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--load-extension=" + extension_path)

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    for keyword in keywords:
        run_keyword_check(keyword, driver)
        time.sleep(2)

    driver.quit()

if __name__ == "__main__":
    set_rival_criteria(review_threshold=20, sales_threshold=70)
    batch_run_from_csv()
