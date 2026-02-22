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

REVIEW_THRESHOLD = 20
SALES_THRESHOLD = 70

def set_rival_criteria(review_threshold=20, sales_threshold=70):
    global REVIEW_THRESHOLD, SALES_THRESHOLD
    REVIEW_THRESHOLD = review_threshold
    SALES_THRESHOLD = sales_threshold

def run_reverse_lookup_scraping():
    print("[INFO] 逆引きキーワード取得処理を開始します...")

    # 既存のChromeセッションに接続
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    try:
        print("[INFO] SellerSpriteの画面が既に開かれていることを想定し、解析を開始します")

        # 現在表示されているページのHTMLを取得
        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.select("tbody tr.vxe-body--row")

        output = []

        # テーブルの各行を解析し、必要なデータを抽出
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

        # タイムスタンプ付きで出力ファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(OUTPUT_DIR, f"reverse_keywords_{timestamp}.csv")

        # 出力CSVに書き込む
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

def run_rival_check_ranking(url):
    print("[INFO] ライバルチェック処理を開始します...")

    # 既存のChromeセッションに接続
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    try:
        # 指定されたAmazonランキングURLにアクセス
        print(f"[INFO] ランキングURLへアクセス: {url}")
        driver.get(url)
        time.sleep(3)

        # ランキングページのHTMLを取得
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.select("div.p13n-sc-uncoverable-faceout")

        output = []
        rival_count = 0

        # 各商品を解析
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

            rating = "N/A"
            rating_block = item.select_one("i.a-icon-star-small")
            if rating_block:
                rating_span = rating_block.select_one("span.a-icon-alt")
                if rating_span:
                    rating = rating_span.get_text(strip=True).replace("5つ星のうち", "")

            review_count = "N/A"
            review_el = item.select_one("span.a-size-small")
            if review_el:
                review_count = review_el.get_text(strip=True).replace(",", "")

            sales_parent = "N/A"
            sales_child = "N/A"
            try:
                ext_section = item.find_parent("div")
                if ext_section:
                    sales_blocks = ext_section.select("div.font-ext-13 span.word-title")
                    for s in sales_blocks:
                        label = s.get_text(strip=True)
                        if "直近30日販売数（親）" in label:
                            value = s.find_next("span", class_="exts-color-border-black")
                            if value:
                                sales_parent = value.get_text(strip=True)
                        elif "直近30日販売数(子)" in label:
                            value = s.find_next("span", class_="exts-color-border-black")
                            if value:
                                sales_child = value.get_text(strip=True)
            except:
                pass

            image_url = "N/A"
            image_tag = item.select_one("img.p13n-product-image")
            if image_tag:
                image_url = image_tag.get("src")

            remark = ""
            try:
                if review_count.isdigit() and sales_parent.replace('+','').isdigit():
                    if int(review_count) <= REVIEW_THRESHOLD and int(sales_parent.replace('+','')) >= SALES_THRESHOLD:
                        remark = "ライバル候補"
                        rival_count += 1
            except:
                pass

            output.append([
                rank, asin, title, product_url, review_count, rating,
                sales_parent, sales_child, image_url, remark
            ])

        # 出力ファイルの作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(OUTPUT_DIR, f"amazon_rival_check_{timestamp}.csv")

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "順位", "ASIN", "商品名", "商品URL", "評価数", "評価値",
                "直近30日販売数（親）", "直近30日販売数（子）", "画像URL", "ライバル候補"
            ])
            writer.writerows(output)

        print(f"[SUCCESS] ✅ 出力ファイル: {csv_path}")
        print(f"[SUCCESS] ✅ ライバル候補数: {rival_count} 件")

        return csv_path, rival_count, output

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None, 0, []

    finally:
        driver.quit()
        print("[INFO] ChromeDriverを終了しました。")


def parse_ranking_soup(soup):
    items = soup.select("div.p13n-sc-uncoverable-faceout")
    output = []
    rival_count = 0

    for i, item in enumerate(items):
        rank = i + 1

        # 商品名
        title_el = item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
        title = title_el.get_text(strip=True) if title_el else "N/A"

        # 商品URLとASIN
        link_el = item.find("a", href=True)
        product_url = "https://www.amazon.co.jp" + link_el["href"] if link_el else "N/A"
        asin = "N/A"
        if link_el and "dp/" in link_el["href"]:
            parts = link_el["href"].split("dp/")
            if len(parts) > 1:
                asin = parts[1].split("/")[0]

        # 評価値
        rating = "N/A"
        rating_block = item.select_one("i.a-icon-star-small")
        if rating_block:
            rating_span = rating_block.select_one("span.a-icon-alt")
            if rating_span:
                rating = rating_span.get_text(strip=True).replace("5つ星のうち", "")

        # 評価数
        review_count = "N/A"
        review_el = item.select_one("span.a-size-small")
        if review_el:
            review_count = review_el.get_text(strip=True).replace(",", "")

        # 販売数（SellerSprite拡張）
        sales_parent = "N/A"
        sales_child = "N/A"
        try:
            ext_section = item.find_parent("div")
            if ext_section:
                sales_blocks = ext_section.select("div.font-ext-13 span.word-title")
                for s in sales_blocks:
                    label = s.get_text(strip=True)
                    if "直近30日販売数（親）" in label:
                        value = s.find_next("span", class_="exts-color-border-black")
                        if value:
                            sales_parent = value.get_text(strip=True)
                    elif "直近30日販売数(子)" in label:
                        value = s.find_next("span", class_="exts-color-border-black")
                        if value:
                            sales_child = value.get_text(strip=True)
        except:
            pass

        # 画像URL
        image_url = "N/A"
        image_tag = item.select_one("img.p13n-product-image")
        if image_tag:
            image_url = image_tag.get("src")

        # ライバル判定
        remark = ""
        try:
            if review_count.isdigit() and sales_parent.replace('+', '').isdigit():
                if int(review_count) <= REVIEW_THRESHOLD and int(sales_parent.replace('+', '')) >= SALES_THRESHOLD:
                    remark = "ライバル候補"
                    rival_count += 1
        except:
            pass

        # 結果に追加
        output.append([
            rank, asin, title, product_url, review_count, rating,
            sales_parent, sales_child, image_url, remark
        ])

    # CSV出力
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(OUTPUT_DIR, f"amazon_ranking_check_{timestamp}.csv")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "順位", "ASIN", "商品名", "商品URL", "評価数", "評価値",
            "直近30日販売数（親）", "直近30日販売数（子）", "画像URL", "ライバル候補"
        ])
        writer.writerows(output)

    return csv_path, rival_count, output