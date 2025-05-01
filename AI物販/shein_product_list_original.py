import csv
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def kill_edge_processes():
    try:
        subprocess.run("taskkill /F /IM msedge.exe /T", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("taskkill /F /IM msedgedriver.exe /T", check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("🪟 Edge 関連プロセスをすべて強制終了しました")
    except Exception as e:
        print(f"[警告] Edge 強制終了に失敗: {e}")


def setup_webdriver():
    global driver

    EDGEDRIVER = r"C:\\Users\\SOICHIRO SAHARA\\Documents\\BizBright\\04 Script\\Amazon\\AI物販\\resources\\msedgedriver.exe"
    EDGEUSERDATA = r"C:\\Users\\SOICHIRO SAHARA\\AppData\\Local\\Microsoft\\Edge\\User Data"
    PROFILE = "Default"

    options = EdgeOptions()
    options.add_argument(f"--user-data-dir={EDGEUSERDATA}")
    options.add_argument(f"--profile-directory={PROFILE}")
    options.add_argument("--start-maximized")

    service = EdgeService(executable_path=EDGEDRIVER)
    driver = webdriver.Edge(service=service, options=options)


def get_search_results(keyword):
    search_url = f"https://jp.shein.com/pdsearch/{keyword}/"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='S-product-card__img-container']"))
        )
    except:
        print("⚠ 商品カードが表示されませんでした")
        return []

    for _ in range(10):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.5)

    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')
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

            # 画像取得
            try:
                img = card.select_one("img")
                image_url = img.get("src") or img.get("data-src")
            except:
                image_url = "N/A"

            # 販売数取得（soldを含むテキスト）
            try:
                sales_raw = sales_candidates[len(product_data)].strip() if len(sales_candidates) > len(product_data) else "N/A"
                import re
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
            print(f"[SKIP] 商品情報取得エラー: {e}")
            continue

    return product_data


def main():
    kill_edge_processes()
    keyword = input("検索キーワードを入力してください（例：笔箱）：").strip()
    setup_webdriver()
    print(f"🔍 キーワード「{keyword}」で検索中...")
    results = get_search_results(keyword)

    from datetime import datetime
    filename = datetime.now().strftime("%Y%m%d_%H%M%S_shein.csv")
    with open(filename, 'w', newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['商品名', '販売数', '商品URL', '画像URL'])
        writer.writerows(results)


    print(f"✅ 完了：{filename} に保存しました")
    driver.quit()  # Edgeブラウザを閉じる


if __name__ == "__main__":
    main()
