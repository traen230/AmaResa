import csv
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromedriver_autoload import get_driver  # 共通ドライバ呼び出しを使用


def run_keyword_check(keyword, review_threshold=20, sales_threshold=70):
    print(f"[INFO] キーワード: {keyword} でチェック開始")
    output = []  # 最終的にCSV・HTMLに出力する結果リスト
    rival_count = 0  # 条件を満たしたライバル候補数

    # ==== デバッグ用Chrome接続設定（既存デバッグポートに接続） ====
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    try:
        # ==== 現在開いているAmazonページのHTMLを取得 ====
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # ==== 検索結果件数を取得 ====
        search_count = "N/A"
        try:
            # 検索結果数はh2要素内のspanから取得
            search_count_el = soup.select_one("h2.a-size-base.a-spacing-small.a-spacing-top-small.a-text-normal span")
            if search_count_el:
                search_text = search_count_el.get_text(strip=True)
                # "検索結果 10,000 以上 のうち 1-48件" → "10,000 以上"
                search_count = search_text.split("のうち")[0].replace("検索結果", "").strip()
        except Exception as e:
            print(f"[WARN] 検索件数取得失敗: {e}")

        # ==== SellerSpriteの月間検索数を取得 ====
        monthly_search_volume = "N/A"
        try:
            # 月間検索数はspan.search-volume-borderから取得
            monthly_el = soup.select_one("span.search-volume-border")
            if monthly_el:
                monthly_search_volume = monthly_el.get_text(strip=True)
        except Exception as e:
            print(f"[WARN] 月間検索数取得失敗: {e}")

        # ==== Amazon検索結果の商品一覧を取得 ====
        items = soup.select("div.s-main-slot > div[data-asin]")
        display_rank = 1  # 表示用の順位カウント（スポンサーなど除外後）

        for i, item in enumerate(items):
            if display_rank > 20:
                break  # 20件取得で終了

            # ==== スポンサー商品は除外 ====
            sponsor_tag = item.select_one("span.a-color-base")
            if sponsor_tag and sponsor_tag.get_text(strip=True) == "スポンサー":
                continue

            # ==== ASINを取得（商品IDがない場合はスキップ） ====
            asin = item.get("data-asin", "").strip()
            if not asin:
                continue

            # ==== 上位2件（広告枠など）を除外 ====
            if i < 2:
                continue

            # ==== 商品タイトルを取得 ====
            title = "N/A"
            title_el = item.select_one("h2.a-size-base-plus > span")
            if title_el:
                title = title_el.get_text(strip=True)

            # ==== 商品URLを取得（aタグのhrefから作成） ====
            product_url = "N/A"
            link_el = item.select_one("a.a-link-normal.s-link-style")
            if link_el and link_el.has_attr("href"):
                href = link_el["href"]
                product_url = "https://www.amazon.co.jp" + href

            # ==== 評価値（★の数）を取得 ====
            rating = "N/A"
            rating_el = item.select_one("span.a-icon-alt")
            if rating_el:
                rating = rating_el.get_text(strip=True).replace("5つ星のうち", "").replace("星5つ中", "").strip()

            # ==== 評価数を取得 ====
            review_count = "N/A"
            review_anchor = item.select_one("a[aria-label*='レーティング']")
            if review_anchor:
                review_label = review_anchor.get("aria-label", "")
                # 評価数部分のみ取得し数値だけに整形
                review_count = review_label.split(" ")[0].replace(",", "") if review_label.split(" ")[0].isdigit() else "N/A"

            # ==== 商品画像URLを取得 ====
            image_url = "N/A"
            image_tag = item.select_one("img.s-image")
            if image_tag and image_tag.has_attr("src"):
                image_url = image_tag["src"]

            # ==== SellerSprite拡張機能から直近30日販売数を取得 ====
            sales_parent = "N/A"
            sales_child = "N/A"
            try:
                sales_blocks = item.find_all("span", class_="word-title")
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
            except Exception as e:
                print(f"[WARN] 販売数取得失敗: {e}")

            # ==== ライバル候補判定（評価数が閾値以下、親販売数が閾値以上） ====
            remark = ""
            try:
                if review_count.isdigit() and sales_parent.replace('+', '').isdigit():
                    if int(review_count) <= review_threshold and int(sales_parent.replace('+', '')) >= sales_threshold:
                        remark = "ライバル候補"
                        rival_count += 1
            except:
                pass

            # ==== 結果をリストに追加 ====
            output.append([
                display_rank, asin, title, product_url, review_count, rating,
                sales_parent, sales_child, image_url, remark
            ])
            display_rank += 1

        # ==== 結果をCSVファイルに保存 ====
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("rival_outputs", exist_ok=True)
        csv_path = os.path.join("rival_outputs", f"keyword_check_{timestamp}.csv")

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "順位", "ASIN", "商品名", "商品URL", "評価数", "評価値",
                "直近30日販売数（親）", "直近30日販売数（子）", "画像URL", "ライバル候補"
            ])
            writer.writerows(output)

        print(f"[SUCCESS] CSV出力: {csv_path}")

        # ==== テンプレート用にHTML表示用データを整形して返却 ====
        html_output = [
            [r[0], r[1], r[3], r[4], r[5], r[6], r[7], r[8], r[9]] for r in output
        ]
        return csv_path, rival_count, html_output, search_count, monthly_search_volume

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None, 0, [], "N/A", "N/A"

    finally:
        # ==== 最後にChromeドライバを終了 ====
        driver.quit()
        print("[INFO] ChromeDriver終了")
