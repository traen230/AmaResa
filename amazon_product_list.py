import csv
import time
import requests
from tkinter import simpledialog, Tk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import imagehash

driver = None

def setup_webdriver():
    global driver
    CHROMEDRIVER = r"C:\Users\SOICHIRO SAHARA\Documents\BizBright\04 Script\99 temp\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    CHROMEUSERDATA = r"C:\Users\SOICHIRO SAHARA\Documents\BizBright\04 Script\01 Amazonスクレイピング\99 cash"

    chrome_service = Service(executable_path=CHROMEDRIVER)
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={CHROMEUSERDATA}')
    options.add_argument('--profile-directory=Default')
    driver = webdriver.Chrome(service=chrome_service, options=options)

def scroll_to_bottom():
    SCROLL_PAUSE_TIME = 1
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_highest_res_image(img_tag):
    if img_tag and img_tag.has_attr("srcset"):
        srcset = img_tag["srcset"]
        last_entry = srcset.split(",")[-1].strip()
        return last_entry.split(" ")[0]
    elif img_tag and img_tag.has_attr("src"):
        return img_tag["src"]
    return ""

def get_phash_from_image_url(image_url):
    try:
        print(f"[画像URL] {image_url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117 Safari/537.36"
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        phash = imagehash.phash(img)
        print(f"[pHash] {phash}")
        return str(phash)
    except Exception as e:
        print(f"[エラー] pHash取得失敗: {e}")
        return "pHash取得失敗"

def get_product_info_list(search_keyword):
    search_url = f"https://www.amazon.co.jp/s?k={search_keyword}"
    driver.get(search_url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
    )

    scroll_to_bottom()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.select("div.s-main-slot div[data-component-type='s-search-result']")

    product_info_list = []

    for i, card in enumerate(product_cards, 1):
        try:
            print(f"\n--- 商品 {i} ---")

            # 商品名・URL
            title_tag = card.select_one("a.a-link-normal.s-line-clamp-4")
            product_name = title_tag.get_text(strip=True) if title_tag else "N/A"
            product_url = "https://www.amazon.co.jp" + title_tag["href"] if title_tag and title_tag.has_attr("href") else "N/A"

            # 画像URL
            img_tag = card.select_one("img.s-image")
            image_url = extract_highest_res_image(img_tag)

            # pHash取得
            phash = get_phash_from_image_url(image_url) if image_url else "画像なし"

            product_info_list.append([product_name, product_url, image_url, phash])
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
    try:
        product_list = get_product_info_list(keyword)
        product_list = product_list[:50]  # 最大50件に制限

        with open('amazon_listing.csv', 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['商品名', '商品URL', '画像URL', '画像pHash'])
            writer.writerows(product_list)

        print(f"\n✅ 商品情報を amazon_listing.csv に保存しました。（{len(product_list)}件）")
    finally:
        driver.quit()
