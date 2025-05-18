# rival_check.py(ランキングチェックボタンと連動)
# このスクリプトは、AmazonカテゴリランキングのURLをもとに、
# 拡張機能から表示される販売数と評価数を用いて、ライバル候補をCSVに出力するためのものです。
# SellerSprite拡張機能による確認メッセージを常に前面で表示します。

import csv
import time
from datetime import datetime
from tkinter import Tk, Toplevel, Label, Button, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# -----------------------------------
# 最前面に出す処理
# -----------------------------------
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

# -----------------------------------
# ライバル候補の初期条件（評価数20以下、販売数70以上）
# -----------------------------------
REVIEW_THRESHOLD = 20
SALES_THRESHOLD = 70

def set_rival_criteria(review_threshold=20, sales_threshold=70):
    global REVIEW_THRESHOLD, SALES_THRESHOLD
    REVIEW_THRESHOLD = review_threshold
    SALES_THRESHOLD = sales_threshold

def run_rival_check_ranking(url):
    driver = None
    try:
        chrome_driver_path = r"C:\Users\SOICHIRO SAHARA\Documents\BizBright\04 Script\99 temp\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        extension_path = r"C:\Users\SOICHIRO SAHARA\AppData\Local\Google\Chrome\User Data\Default\Extensions\lnbmbgocenenhhhdojdielgnmeflbnfb\4.7.5_0"

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--load-extension=" + extension_path)

        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        if not url:
            show_topmost_message("エラー", "❌ URLが空です。")
            return None, 0

        driver.get(url)

        # --- SellerSpriteログイン確認（常に前面表示） ---
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo("ログイン確認", "🔐 SellerSprite にログインが完了したら『OK』を押してください。", parent=root)
        root.destroy()
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.select("div.p13n-sc-uncoverable-faceout")

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
            title_el = item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
            title = title_el.get_text(strip=True) if title_el else "N/A"

            link_el = item.find("a", href=True)
            product_url = "https://www.amazon.co.jp" + link_el["href"] if link_el else "N/A"

            asin = "N/A"
            if link_el and "dp/" in link_el["href"]:
                parts = link_el["href"].split("dp/")
                if len(parts) > 1:
                    asin = parts[1].split("/")[0]

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

            sales = sales_data[i] if i < len(sales_data) else "N/A"

            remark = ""
            try:
                if review_count.isdigit() and sales.isdigit():
                    if int(review_count) <= REVIEW_THRESHOLD and int(sales) >= SALES_THRESHOLD:
                        remark = "ライバル候補"
                        rival_count += 1
            except:
                pass

            output.append([rank, asin, title, product_url, review_count, rating, sales, remark])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"amazon_ranking_with_sales_{timestamp}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["順位", "ASIN", "商品名", "商品URL", "評価数", "評価値", "直近30日販売数（親）", "ライバル候補"])
            writer.writerows(output)

        message = f"✅ データ取得完了！\n{csv_path} に保存しました。\nライバル候補：{rival_count} 件"
        show_topmost_message("完了", message)
        return csv_path, rival_count

    except Exception as e:
        show_topmost_message("エラー", f"❌ ライバル調査中にエラーが発生しました:\n{e}")
        return None, 0

    finally:
        if driver:
            driver.quit()
