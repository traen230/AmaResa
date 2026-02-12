import csv
import time
from datetime import datetime
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# 出力先ディレクトリ
OUTPUT_DIR = "rival_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_reverse_lookup_scraping(url):
    print("[INFO] 逆引きキーワード取得処理を開始します...")

    # Seleniumのオプション設定
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)

        #root = Tk()
        #root.withdraw()
        #root.attributes('-topmost', True)
        #messagebox.showinfo("ログイン確認", "🔐 SellerSprite にログインして逆引きキーワードの画面を開いてください。その後OKを押してください。")
        #root.destroy()

        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.select("tbody tr.vxe-body--row")

        output = []
        for row in rows:
            try:
                keyword = row.select_one("td.col_4 .keyword").get_text(strip=True)
                exposure_rate = row.select_one("td.col_5 div:nth-of-type(1)").get_text(strip=True)
                weekly_exposure = row.select_one("td.col_5 div:nth-of-type(2)").get_text(strip=True)
                traffic_type = row.select_one("td.col_5 div:nth-of-type(3)").get_text(strip=True)
                ad_type = row.select_one("td.col_6").get_text(strip=True)
                natural_pct = row.select_one("td.col_7 .inline:nth-of-type(1) span").get_text(strip=True)
                ad_pct = row.select_one("td.col_7 .inline:nth-of-type(2) span").get_text(strip=True)
                last_rank = row.select_one("td.col_8 div.rank-wrap div:nth-of-type(1)").get_text(strip=True)
                last_page_rank = row.select_one("td.col_8 div.rank-wrap div:nth-of-type(2)").get_text(strip=True)
                search_volume = row.select_one("td.col_10 span").get_text(strip=True)

                output.append([
                    keyword, exposure_rate, weekly_exposure, traffic_type,
                    ad_type, natural_pct, ad_pct, last_rank,
                    last_page_rank, search_volume
                ])
            except Exception as e:
                print(f"[WARN] スキップされた行があります: {e}")
                continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(OUTPUT_DIR, f"reverse_keywords_{timestamp}.csv")

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["キーワード", "露出率", "週間露出", "流入種別", "広告タイプ", "自然割合", "広告割合", "最新順位", "ページ内順位", "検索数"])
            writer.writerows(output)

        print(f"[SUCCESS] ✅ 出力ファイル: {csv_path}")
        return csv_path, len(output), output

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None, 0, []

    finally:
        driver.quit()
        print("[INFO] ChromeDriverを終了しました。")

# 🔍 HTMLをパースして逆引きデータを抽出
def parse_reverse_lookup_soup(soup):
    def safe_text(selector):
        return selector.get_text(strip=True) if selector else "N/A"

    rows = soup.select("tbody tr.vxe-body--row")
    #rows = soup.select("tbody tr.vxe-body--row")[:10]

    output = []

    for row in rows:
        try:
            keyword = safe_text(row.select_one("td.col_4 .keyword"))
            exposure_rate = safe_text(row.select_one("td.col_5 div:nth-of-type(1)"))
            weekly_exposure = safe_text(row.select_one("td.col_5 div:nth-of-type(2)"))
            traffic_type = safe_text(row.select_one("td.col_5 div:nth-of-type(3)"))
            ad_type = safe_text(row.select_one("td.col_6"))
            natural_pct = safe_text(row.select_one("td.col_7 .inline:nth-of-type(1) span"))
            ad_pct = safe_text(row.select_one("td.col_7 .inline:nth-of-type(2) span"))
            last_rank = safe_text(row.select_one("td.col_8 div.rank-wrap div:nth-of-type(1)"))
            last_page_rank = safe_text(row.select_one("td.col_8 div.rank-wrap div:nth-of-type(2)"))
            search_volume = safe_text(row.select_one("td.col_10 span"))

            output.append([
                keyword, exposure_rate, weekly_exposure, traffic_type,
                ad_type, natural_pct, ad_pct, last_rank,
                last_page_rank, search_volume
            ])
        except Exception as e:
            print(f"[WARN] スキップされた行があります: {e}")
            continue

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(OUTPUT_DIR, f"reverse_keywords_{timestamp}.csv")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["キーワード", "露出率", "週間露出", "流入種別", "広告タイプ", "自然割合", "広告割合", "最新順位", "ページ内順位", "検索数"])
        writer.writerows(output)

    return csv_path, len(output), output

def set_rival_criteria(review_threshold=20, sales_threshold=70):
    pass

def run_rival_check_ranking(url):
    pass
