import csv
import time
from datetime import datetime
from tkinter import simpledialog, messagebox, Tk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

driver = None

def setup_webdriver():
    global driver
    CHROMEDRIVER = r"C:\Users\SOICHIRO SAHARA\Documents\BizBright\04 Script\99 temp\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    EXTENSION_PATH = r"C:\Users\SOICHIRO SAHARA\AppData\Local\Google\Chrome\User Data\Default\Extensions\lnbmbgocenenhhhdojdielgnmeflbnfb\4.7.5_0"

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--load-extension={EXTENSION_PATH}")

    chrome_service = Service(executable_path=CHROMEDRIVER)
    driver = webdriver.Chrome(service=chrome_service, options=options)

def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(5):  # 多めにスクロール
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_product_info_list():
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
    )

    scroll_to_bottom()
    time.sleep(5)  # SellerSpriteの描画待ち

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.select("div.s-main-slot div[data-component-type='s-search-result']")

    product_info_list = []

    for i, card in enumerate(product_cards, 1):
        try:
            print(f"\n--- 商品 {i} ---")

            # 商品名・URL
            title_tag = card.select_one("a.a-link-normal.s-line-clamp-4")
            product_name = title_tag.get_text(strip=True) if title_tag else "N/A"
            product_url = "https://www.amazon.co.jp" + title_tag["href"] if title_tag else "N/A"

            # 画像URL
            img_tag = card.select_one("img.s-image")
            image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

            # 評価数・評価値
            rating = "N/A"
            review_count = "N/A"
            rating_el = card.select_one("span.a-icon-alt")
            if rating_el:
                rating = rating_el.get_text(strip=True).replace("5つ星のうち", "").strip()

            review_el = card.select_one("span.a-size-base.s-underline-text")
            if review_el:
                review_count = review_el.get_text(strip=True).replace(",", "").strip()

            # 販売数（親）を商品内から取得
            sales_count = "N/A"
            divs = card.select("div.font-ext-13")
            for div in divs:
                if "直近30日販売数（親）" in div.get_text(strip=True):
                    span = div.select_one("span.exts-color-border-black.grade-hover")
                    if span:
                        sales_count = span.get_text(strip=True).replace(",", "")
                        break

            # ライバル候補条件：販売数80以上 かつ 評価数20以下
            is_rival = ""
            try:
                if sales_count.isdigit() and review_count.isdigit():
                    if int(sales_count) >= 80 and int(review_count) <= 20:
                        is_rival = "ライバル候補"
            except:
                is_rival = ""

            # 結果をリストに追加（G列：備考）
            product_info_list.append([
                product_name,
                product_url,
                image_url,
                sales_count,
                review_count,
                rating,
                is_rival
            ])

        except Exception as e:
            print(f"[エラー] 商品情報の取得失敗: {e}")
            continue

    return product_info_list

# --- 実行 ---
if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    keyword = simpledialog.askstring("キーワード入力", "Amazonで検索したいキーワードを入力してください：")
    if not keyword:
        print("検索キーワードが入力されなかったため終了します。")
        exit()

    setup_webdriver()

    # Amazon検索ページを表示
    search_url = f"https://www.amazon.co.jp/s?k={keyword}"
    driver.get(search_url)

    # OKが押されたらスクレイピング開始
    messagebox.showinfo("ログイン確認", "🔐 SellerSprite にログインが完了したら『OK』を押してください。")

    try:
        product_list = get_product_info_list()
        product_list = product_list[:50]  # 最大50件

        # 日時入りのファイル名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"amazon_listing_{timestamp}.csv"

        with open(csv_filename, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['商品名', '商品URL', '画像URL', '直近30日販売数（親）', '評価数', '評価値', '備考'])
            writer.writerows(product_list)

        print(f"\n✅ 商品情報を {csv_filename} に保存しました。（{len(product_list)}件）")

    finally:
        driver.quit()
