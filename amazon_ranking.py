from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import tkinter as tk
from tkinter import simpledialog, messagebox
import time
from bs4 import BeautifulSoup
import csv

# ChromeDriver・拡張機能パス（ご自身の環境に合わせて変更）
chrome_driver_path = r"C:\Users\SOICHIRO SAHARA\Documents\BizBright\04 Script\99 temp\chromedriver-win64\chromedriver-win64\chromedriver.exe"
extension_path = r"C:\Users\SOICHIRO SAHARA\AppData\Local\Google\Chrome\User Data\Default\Extensions\lnbmbgocenenhhhdojdielgnmeflbnfb\4.7.5_0"

# Chromeオプション設定
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--load-extension=" + extension_path)

# Chrome起動
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# ✅ tkinterでAmazonランキングURLを入力させる
input_root = tk.Tk()
input_root.withdraw()  # メインウィンドウを非表示
url = simpledialog.askstring("AmazonランキングURL", "ランキングページのURLを入力してください：")

if not url:
    print("❌ URLが入力されませんでした。スクリプトを終了します。")
    driver.quit()
    exit()

# 入力されたURLにアクセス
driver.get(url)

# ✅ SellerSpriteログイン完了待ちポップアップ（OKボタン）
messagebox.showinfo(
    title="ログイン確認",
    message="🔐 SellerSprite にログインが完了したら『OK』を押してください。"
)

# BeautifulSoupでHTML解析
soup = BeautifulSoup(driver.page_source, "html.parser")

# 商品ブロックを取得
items = soup.select("div.p13n-sc-uncoverable-faceout")

# 販売数ブロックを取得
sales_blocks = soup.find_all("div", class_="font-ext-13")
sales_data = []
for div in sales_blocks:
    if "直近30日販売数（親）" in div.get_text(strip=True):
        value_span = div.find("span", class_="exts-color-border-black")
        if value_span:
            sales_data.append(value_span.get_text(strip=True))

# データ格納用
output = []

# 商品ごとにループ
for i, item in enumerate(items):
    rank = i + 1

    # 商品名
    title_el = item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
    title = title_el.get_text(strip=True) if title_el else "N/A"

    # 商品URL
    link_el = item.find("a", href=True)
    product_url = "https://www.amazon.co.jp" + link_el["href"] if link_el else "N/A"

    # 評価値・評価数
    rating_block = item.select_one("a.a-link-normal[title*='5つ星のうち']")
    rating = "N/A"
    review_count = "N/A"
    if rating_block:
        rating_el = rating_block.select_one("span.a-icon-alt")
        if rating_el:
            rating = rating_el.get_text(strip=True).replace("5つ星のうち", "")
        review_el = rating_block.select_one("span.a-size-small")
        if review_el:
            review_count = review_el.get_text(strip=True).replace(",", "")

    # 販売数
    sales = sales_data[i] if i < len(sales_data) else "N/A"

    # 出力データに追加
    output.append([rank, title, product_url, review_count, rating, sales])

# CSV出力
csv_path = "amazon_ranking_with_sales.csv"
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["順位", "商品名", "商品URL", "評価数", "評価値", "直近30日販売数（親）"])
    writer.writerows(output)

print(f"\n✅ データ取得完了！ {csv_path} に保存しました。")

# driver.quit()  # 必要に応じてブラウザを閉じる
