from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import requests
from bs4 import BeautifulSoup
import os
import uuid
import subprocess
import time
from werkzeug.utils import secure_filename


# ==== 外部スクリプトの読み込み ====
from keyword_check import run_keyword_check
import reverse_lookup
import rival_check
import shein_scraper
import rakuten_scraper
import psutil  # ファイル上部で1回だけ追加
from resnet_compare import load_amazon_images, compare_images_with_resnet
from google_trends_collector import GoogleTrendsCollector
from datetime import datetime



app = Flask(__name__)
selected_category = {"url": "", "label": ""}
output_dir = os.path.join(os.getcwd(), "rival_outputs")
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FOCUS_MARKETS_CACHE = {
    "markets": [],
    "trend_keywords": [],
    "updated_at": None,
}


def build_focus_markets_from_trends(trend_keywords, limit=4):
    if not trend_keywords:
        return []

    markets = []
    seen = set()
    for kw in trend_keywords:
        if not isinstance(kw, str):
            continue
        clean_kw = kw.strip()
        if not clean_kw:
            continue
        key = clean_kw.lower()
        if key in seen:
            continue
        seen.add(key)
        markets.append(clean_kw)

    return markets[:limit]


def clear_home_trends_cache():
    FOCUS_MARKETS_CACHE["markets"] = []
    FOCUS_MARKETS_CACHE["trend_keywords"] = []
    FOCUS_MARKETS_CACHE["updated_at"] = None


def get_cached_home_data():
    return (
        FOCUS_MARKETS_CACHE["trend_keywords"],
        FOCUS_MARKETS_CACHE["markets"],
        FOCUS_MARKETS_CACHE["updated_at"],
    )


def fetch_home_trends():
    try:
        collector = GoogleTrendsCollector()
        trend_keywords = collector.get_amazon_single_keywords(limit=20)
    except Exception as e:
        print(f"[WARN] Google Trends 取得失敗: {e}")
        trend_keywords = []

    FOCUS_MARKETS_CACHE["trend_keywords"] = trend_keywords
    FOCUS_MARKETS_CACHE["markets"] = build_focus_markets_from_trends(trend_keywords, limit=4)
    FOCUS_MARKETS_CACHE["updated_at"] = datetime.now()

# =========================================================
# 🏠 ホーム（母艦）
# =========================================================
@app.route("/")
def index():
    # バージョン情報
    version_info = ""
    try:
        with open("version.txt", "r", encoding="utf-8") as f:
            version_info = f.read().strip()
    except Exception as e:
        print(f"[WARN] version.txt 読み取り失敗: {e}")

    trend_keywords, focus_markets, updated_at = get_cached_home_data()
    last_updated_text = updated_at.strftime("%Y-%m-%d %H:%M") if updated_at else "未取得"

    return render_template(
        "index.html",
        version_info=version_info,
        trend_keywords=trend_keywords,
        focus_markets=focus_markets,
        last_updated=last_updated_text
    )


@app.route("/trends/fetch", methods=["POST"])
def fetch_trends():
    clear_home_trends_cache()
    fetch_home_trends()
    return redirect(url_for("index"))

# ==== カテゴリ選択と表示 ====
@app.route("/market/category", methods=["GET", "POST"])
def market_category():
    global selected_category
    if request.method == "POST":
        category_url = request.form.get("category_url")
        category_label = request.form.get("category_label")
        selected_category["url"] = category_url
        selected_category["label"] = category_label
        return redirect(url_for("market_category"))

    return render_template("market_category.html", selected_category=selected_category)

# ==== Amazonカテゴリをドリルダウンで表示 ====
@app.route("/category/select")
def category_select():
    url = request.args.get("url", "https://www.amazon.co.jp/gp/bestsellers")
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "html.parser")
        links = soup.select("ul[role='group'] li a") or soup.select("div[role='group'] a")

        if not links:
            return render_template("category_confirm.html", url=url, label=soup.title.string.strip())

        category_list = []
        for link in links:
            href = link.get('href')
            text = link.get_text(strip=True)
            if href and text:
                full_url = href if href.startswith("http") else "https://www.amazon.co.jp" + href
                category_list.append((text, full_url))

        return render_template("category_select.html", category_list=category_list)

    except Exception as e:
        return f"<h2>エラー: {e}</h2>"

# ==== 最終カテゴリの確認画面 ====
@app.route("/category/confirm", methods=["POST"])
def category_confirm():
    url = request.form.get("category_url")
    label = request.form.get("category_label")
    return render_template("category_confirm_result.html", label=label, url=url)

# ==== ランキングリサーチ ====
@app.route("/ranking/research", methods=["GET", "POST"])
def ranking_research():
    if request.method == "POST":
        url = request.form.get("ranking_url")
        if not url:
            return render_template("ranking_research.html", logs=["❌ URLが入力されていません。"])

        # ✅ Chrome（SellerSprite拡張付き）をGoogleで起動（URLは.py内に任せる）
        # subprocess.Popen(["python", "start_chrome_with_extension.py"])
        # time.sleep(3)

        # ✅ Googleログイン完了後、POSTでAmazonランキングURLへ遷移 → SellerSpriteログインへ
        return render_template("google_login_wait.html", url=url, next_action="/ranking/research/login", keyword="", review=20, sales=70)

    # GET時は初期画面表示
    return render_template("ranking_research.html", logs=[])

# ==== ランキングリサーチ実行処理 ====
@app.route("/ranking/research/execute", methods=["POST"])
def execute_ranking_research():
    logs = []
    csv_filename = None
    url = request.form.get("ranking_url")
    output_data = []

    try:
        logs.append("🚀 既存のChromeからHTMLを取得しています...")

        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from bs4 import BeautifulSoup
        import os

        # ✅ 既存のデバッグセッションに接続
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)

        # ✅ 現在のページ（＝ランキングURL）をそのまま取得
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # ✅ スクレイピング関数に soup を渡してデータ抽出
        csv_path, rival_count, output_data = rival_check.parse_ranking_soup(soup)

        if csv_path:
            csv_filename = os.path.basename(csv_path)
            logs.append("✅ ライバルチェックが完了しました。")
            logs.append(f"👥 ライバル候補数: {rival_count} 件")
        else:
            logs.append("❌ CSVファイルが作成されませんでした。")

    except Exception as e:
        logs.append(f"❌ エラー: {e}")

    return render_template("ranking_research.html", logs=logs, csv_filename=csv_filename, results=output_data)

# ==== Googleログイン完了後 → ランキングページへ遷移してSellerSpriteログインを促す ====
@app.route("/ranking/research/login", methods=["POST"])
def ranking_google_login():
    url = request.form.get("url")  # 前ページで入力されたランキングURL
    keyword = request.form.get("keyword", "")
    review = int(request.form.get("review", 20))
    sales = int(request.form.get("sales", 70))

    try:
        # ✅ 既存のChromeセッションに接続
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)

        # ✅ Amazonランキングページへ遷移
        driver.get(url)
        time.sleep(3)
        driver.quit()
    except Exception as e:
        print(f"❌ Chrome制御エラー: {e}")

    # ✅ SellerSpriteログイン待機画面へ（次は /ranking/research/execute にPOST）
    return render_template("sellersprite_wait_login.html", url=url, next_action="/ranking/research/execute", keyword=keyword, review=review, sales=sales)


# ==== 逆引きキーワードリサーチ：初期画面 ====
@app.route("/reverse/research", methods=["GET", "POST"])
def reverse_research():
    if request.method == "POST":
        url = request.form.get("ranking_url")
        if not url:
            return render_template("reverse_lookup.html", logs=["❌ URLが入力されていません。"])

        # ✅ Chromeの起動＋Googleログイン待ち画面へ遷移
        return render_template("google_login_wait.html", url=url, next_action="/reverse/research/login", keyword="", review=20, sales=70)

    return render_template("reverse_lookup.html", logs=[])

# ==== 逆引きキーワード取得実行 ====
@app.route("/reverse/research/execute", methods=["POST"])
def execute_reverse_research():
    logs = []
    csv_filename = None
    output_data = []

    try:
        logs.append("🚀 既存のChromeからHTMLを取得しています...")

        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from bs4 import BeautifulSoup

        # ✅ デバッグモードのChromeセッションに接続
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)

        # ✅ 現在のページ（＝SellerSpriteの逆引き画面）をそのまま取得
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # ✅ データ解析処理
        csv_path, keyword_count, output_data = reverse_lookup.parse_reverse_lookup_soup(soup)

        if csv_path:
            csv_filename = os.path.basename(csv_path)
            logs.append(f"✅ 完了: {keyword_count} 件")
        else:
            logs.append("❌ CSVファイル作成失敗")
    except Exception as e:
        logs.append(f"❌ エラー: {e}")

    return render_template("reverse_lookup.html", logs=logs, csv_filename=csv_filename, results=output_data)

# ==== 逆引きキーワードリサーチ：Googleログイン完了後 ====
@app.route("/reverse/research/login", methods=["POST"])
def reverse_google_login():
    url = request.form.get("url")
    keyword = request.form.get("keyword", "")
    review = int(request.form.get("review", 20))
    sales = int(request.form.get("sales", 70))

    try:
        # ✅ Chromeで指定されたページへ遷移（URLはSellerSpriteの逆引き画面）
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)
        driver.quit()
    except Exception as e:
        print(f"❌ エラー: {e}")

    # ✅ 次にSellerSpriteログインを促す画面へ遷移
    return render_template("sellersprite_wait_login.html", url=url, next_action="/reverse/research/execute", keyword=keyword, review=review, sales=sales)


# ==== 商品リサーチ（SHEIN / 楽天） ====
@app.route("/product/research", methods=["GET", "POST"])
def product_research():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        if not keyword:
            return render_template("product_research.html", error="❌ キーワードが入力されていません。")

        # ★ 追加：thresholdの取得・正規化（初期値0.7）
        raw_threshold = request.form.get("threshold", "0.7")
        try:
            threshold = float(str(raw_threshold).replace(",", "."))
        except ValueError:
            threshold = 0.7
        threshold = max(0.0, min(1.0, threshold))

        # ==== Amazon CSVファイル読み込み ====
        uploaded_csv = request.files.get("amazon_csv")
        if not uploaded_csv or uploaded_csv.filename == "":
            return render_template(
                "product_research.html",
                error="❌ Amazon検索結果CSVがアップロードされていません。",
                keyword=keyword,
                threshold=threshold
            )

        filename = secure_filename(uploaded_csv.filename)
        csv_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
        uploaded_csv.save(csv_path)

        # 共通：Amazon画像のロードは1回だけ
        amazon_images = load_amazon_images(csv_path)

        if "shein" in request.form:
            subprocess.Popen(["python", "start_chrome_with_extension.py", f"https://jp.shein.com/pdsearch/{keyword}/"])
            time.sleep(3)
            shein_csv_path, shein_data = shein_scraper.scrape_shein(keyword)
            # ★ 修正：フォームからのthresholdを使用
            unique_items = compare_images_with_resnet(shein_data, amazon_images, threshold=threshold)
            return render_template("product_result.html", results=unique_items, threshold=threshold, keyword=keyword)

        elif "rakuten" in request.form:
            subprocess.Popen(["python", "start_chrome_with_extension.py", f"https://search.rakuten.co.jp/search/mall/{keyword}/"])
            time.sleep(3)
            rakuten_csv_path, rakuten_data = rakuten_scraper.run_rakuten_scraper(keyword)
            # ★ 修正：フォームからのthresholdを使用
            unique_items = compare_images_with_resnet(rakuten_data, amazon_images, threshold=threshold)
            return render_template("product_result.html", results=unique_items, threshold=threshold, keyword=keyword)

    # GET
    return render_template("product_research.html")


# ==== 商品リサーチ実行（SHEIN） ====
@app.route("/shein/research/execute", methods=["POST"])
def shein_research_execute():
    keyword = request.form.get("keyword", "").strip()
    raw_threshold = request.form.get("threshold", "0.7")
    logs = []

    # thresholdの正規化
    try:
        threshold = float(str(raw_threshold).replace(",", "."))
    except ValueError:
        threshold = 0.7
        logs.append("エラー: thresholdが不正だったため 0.70 を適用しました。")
    threshold = max(0.0, min(1.0, threshold))

    try:
        logs.append(f"🔍 SHEINで「{keyword}」を検索開始...（抽出条件：最大類似度 < {threshold:.2f}）")
        csv_path, results = shein_scraper.scrape_shein(keyword)  # ※ ここは既存のまま
        csv_filename = os.path.basename(csv_path)
        logs.append(f"✅ {keyword}で検索結果を取得しました。")

        # 類似度比較まで行うパイプラインが後段にあるなら、そこで full_csv / candidate_csv を作成し、
        # ここに渡してください（無ければこの2つは渡さなくてOK）
        return render_template(
            "shein_research.html",
            keyword=keyword,
            results=results,
            csv_filename=csv_filename,
            logs=logs,
            threshold=threshold,
            # full_csv=full_csv, candidate_csv=candidate_csv  # 必要なら
        )
    except Exception as e:
        logs.append(f"❌ エラー: {e}")
        return render_template(
            "shein_research.html",
            error="❌ エラーが発生しました。",
            logs=logs,
            keyword=keyword,
            threshold=threshold
        )


# ==== 商品リサーチ実行（楽天） ====
@app.route("/rakuten/research/execute", methods=["POST"])
def rakuten_research_execute():
    keyword = request.form.get("keyword", "").strip()
    raw_threshold = request.form.get("threshold", "0.7")
    logs = []

    # thresholdの正規化
    try:
        threshold = float(str(raw_threshold).replace(",", "."))
    except ValueError:
        threshold = 0.7
        logs.append("エラー: thresholdが不正だったため 0.70 を適用しました。")
    threshold = max(0.0, min(1.0, threshold))

    try:
        logs.append(f"🔍 楽天で「{keyword}」を検索開始...（抽出条件：最大類似度 < {threshold:.2f}）")
        csv_path, results = rakuten_scraper.run_rakuten_scraper(keyword)  # ※ ここは既存のまま
        csv_filename = os.path.basename(csv_path)
        logs.append(f"✅ {keyword} の結果を取得しました。")

        # 類似度比較CSV（full/candidate）を生成している場合はテンプレに渡してください
        return render_template(
            "rakuten_research.html",
            keyword=keyword,
            results=results,
            csv_filename=csv_filename,
            logs=logs,
            threshold=threshold,
            # full_csv=full_csv, candidate_csv=candidate_csv  # 必要なら
        )
    except Exception as e:
        logs.append(f"❌ エラー: {e}")
        return render_template(
            "rakuten_research.html",
            error="❌ エラーが発生しました。",
            logs=logs,
            keyword=keyword,
            threshold=threshold
        )


# ==== Googleログイン用ブラウザを別ウィンドウで起動 ====
@app.route("/open/google", methods=["POST"])
def open_google_browser():
    try:
        subprocess.Popen(["python", "start_chrome_with_extension.py", "https://www.google.co.jp/"])
        return "✅ Google起動OK", 200
    except Exception as e:
        return f"❌ 起動失敗: {e}", 500

# ==== Googleログイン確認画面を表示 ====
@app.route("/browser/login", methods=["POST"])
def browser_login():
    keyword = request.form.get("keyword", "").strip()
    review = int(request.form.get("review_threshold", 20))
    sales = int(request.form.get("sales_threshold", 70))

    # 🔁 今のウィンドウで「Googleログイン済みですか？」の画面を表示
    return render_template("google_login_wait.html", keyword=keyword, review=review, sales=sales)

# ==== Googleログイン完了後 → 同一タブでAmazon検索ページに遷移し、ログインを促す ====
@app.route("/browser/amazon", methods=["POST"])
def browser_amazon():
    keyword = request.form.get("keyword", "").strip()
    review = int(request.form.get("review_threshold", 20))
    sales = int(request.form.get("sales_threshold", 70))

    # 🔄 Seleniumから既存セッションのChromeに接続して、Amazonを同一ウィンドウで開く
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)
        driver.get(f"https://www.amazon.co.jp/s?k={keyword}")
        time.sleep(3)
        driver.quit()
    except Exception as e:
        print(f"❌ Chrome制御エラー: {e}")

    return render_template("sellersprite_wait_login.html", keyword=keyword, review=review, sales=sales, next_action="/keyword/research/execute", url="")

# ==== キーワードリサーチフォーム画面 ====
@app.route("/keyword/research", methods=["GET", "POST"])
def keyword_research():
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        review = int(request.form.get("review_threshold", 20))
        sales = int(request.form.get("sales_threshold", 70))

        if not keyword:
            return render_template("keyword_research.html", logs=["❌ キーワードが入力されていません。"])

        # 🔧 Amazon検索URLを構築
        search_url = f"https://www.amazon.co.jp/s?k={keyword}"

        # ✅ Googleログイン画面を表示（キーワードやURLを渡す）
        return render_template("google_login_wait.html", keyword=keyword, review=review, sales=sales, url=search_url, next_action="/browser/amazon")

    return render_template("keyword_research.html", logs=[])


# ==== キーワードリサーチ実行処理 ====
@app.route("/keyword/research/execute", methods=["POST"])
def execute_keyword_research():
    logs = []
    keyword = request.form.get("keyword")
    review = int(request.form.get("review_threshold", 20))
    sales = int(request.form.get("sales_threshold", 70))
    output_data = []
    csv_filename = ""
    search_count = "N/A"
    monthly_search_volume = "N/A"
    ai_judgement = ""  # 常に初期化しておく

    try:
        logs.append("🚀 スクレイピングを開始しています...")
        # run_keyword_check() から5つの戻り値を受け取る
        csv_path, rival_count, output_data, search_count, monthly_search_volume = run_keyword_check(
            keyword, review_threshold=review, sales_threshold=sales
        )

        if csv_path:
            csv_filename = os.path.basename(csv_path)
            logs.append("✅ キーワードチェックが完了しました。")
            logs.append(f"👥 ライバル候補数: {rival_count} 件")

            try:
                # 商品数を数値に変換（例: "10,000 以上" → 10000）
                product_count = 0
                if isinstance(search_count, str) and search_count != "N/A":
                    product_count_clean = search_count.replace(",", "").replace("以上", "").strip()
                    product_count = int(product_count_clean)

                # output_dataから上位4件の販売数を抽出
                top_sales = []
                for row in output_data[:4]:
                    try:
                        sale = int(row[5].replace("+", ""))
                        top_sales.append(sale)
                    except:
                        top_sales.append(0)

                # output_dataから弱セラー候補を抽出
                weak_sellers = []
                for row in output_data:
                    try:
                        review_count = int(row[3])
                        sales_parent = int(row[5].replace("+", ""))
                        rank = int(row[0])
                        weak_sellers.append({"sale": sales_parent, "rank": rank, "reviews": review_count})
                    except:
                        continue

                # monthly_search_volumeをintに変換してAI判定へ渡す
                monthly_search_int = 0
                try:
                    if isinstance(monthly_search_volume, str) and monthly_search_volume != "N/A":
                        monthly_clean = monthly_search_volume.replace(",", "").replace("+", "").replace("以上", "").strip()
                        monthly_search_int = int(monthly_clean)
                except:
                    monthly_search_int = 0

                # AI判定を呼び出す
                ai_judgement = ai_market_judgement(
                    product_count,
                    top_sales,
                    weak_sellers,
                    monthly_search_int
                )

            except Exception as e:
                logs.append(f"⚠️ AI判定エラー: {e}")
                ai_judgement = ""

        else:
            logs.append("❌ CSVファイルが作成されませんでした。")
            ai_judgement = ""

    except Exception as e:
        logs.append(f"❌ エラー: {e}")
        ai_judgement = ""

    return render_template(
        "keyword_research.html",
        logs=logs,
        csv_filename=csv_filename,
        results=output_data,
        search_count=search_count,
        monthly_search_volume=monthly_search_volume,
        ai_judgement=ai_judgement
    )



# ==== AI市場判定機能 ====
def ai_market_judgement(product_count, top_sales, weak_sellers, monthly_search_volume):
    """
    次の市場のAI判定を実行する関数
    :param product_count: int, Amazon検索結果件数
    :param top_sales: list of int, 上位セラーの販売数（1〜10位程度）
    :param weak_sellers: list of dict, 弱セラー情報 [{"sale":int, "rank":int, "reviews":int}, ...]
    :param monthly_search_volume: int, 月間検索数
    :return: str, AI判定結果文
    """

    # === 条件1: 商品数 ===
    # 5000以下 → 🔵、5001-20000 → 🔼、20001以上 → ❌
    if product_count <= 5000:
        mark1 = "🔵"
    elif product_count <= 20000:
        mark1 = "🔼"
    else:
        mark1 = "❌"

    # === 条件2: 上位セラー・弱セラーの状況 ===
    # 上位セラー全員70以上 → 🔵、上位10件中10件以上70以上 → 🔼、弱セラーで70以上がいれば即🔵
    mark2 = "❌"
    cond2_met = False  # 条件2を満たしているか

    # 上位セラー全員70以上なら🔵
    if top_sales and all(s >= 70 for s in top_sales):
        mark2 = "🔵"
        cond2_met = True
    else:
        # 上位10件で70以上が10件以上なら🔼
        top10_sales_over70 = sum(1 for s in top_sales[:10] if s >= 70)
        if top10_sales_over70 >= 10:
            mark2 = "🔼"

        # 弱セラーに70以上がいれば即🔵
        for ws in weak_sellers:
            if ws["sale"] >= 70:
                mark2 = "🔵"
                cond2_met = True
                break

    # === 条件3: 弱セラー（評価20以下＆販売数70以上） ===
    cond3 = False
    mark3 = "❌"
    is_top_ranked = False  # 弱セラーが上位3位以内にいるか
    for ws in weak_sellers:
        weak_ok = ws["reviews"] <= 20 and ws["sale"] >= 70
        if weak_ok:
            cond3 = True
            is_top_ranked = ws["rank"] <= 3
            mark3 = "🔵" if is_top_ranked else "🔼"
            break

    # === 条件4: 月間検索数200以上 ===
    # 200以上 → 🔵、それ未満 → ❌
    mark4 = "❌"
    if monthly_search_volume >= 200:
        mark4 = "🔵"

    # === 条件印スコア計算 ===
    # 条件ごとにスコアを設定：🔵=1.0点、🔼=0.5点、❌=0.0点
    score1 = 1.0 if mark1 == "🔵" else 0.5 if mark1 == "🔼" else 0.0
    score2 = 1.0 if mark2 == "🔵" else 0.5 if mark2 == "🔼" else 0.0
    score3 = 1.0 if cond3 else 0.0
    score4 = 1.0 if mark4 == "🔵" else 0.0

    total_score = score1 + score2 + score3 + score4  # 条件達成度の合計スコア

    # === 総合ランク判定 ===
    # A：3.0以上、B：2.0以上、C：1.0以上、D：それ未満
    rank = "D"
    if total_score >= 3.0:
        rank = "A"
    elif total_score >= 2.0:
        rank = "B"
    elif total_score >= 1.0:
        rank = "C"

    # === アドバイス文生成 ===
    advice = ""
    # 商品数についてのアドバイス
    if mark1 == "🔵":
        advice += "商品数が少なく、ブルーオーシャンの可能性があります。\n"
    elif mark1 == "🔼":
        advice += "商品数は中程度で、競合の多さには注意が必要です。\n"
    else:
        advice += "商品数が非常に多く、競争が激しい可能性があります。\n"

    # 上位セラー状況についてのアドバイス
    if mark2 == "🔵":
        advice += "市場の上位セラーは安定して売れており、全体の需要が高いと判断できます。\n"
    elif mark2 == "🔼":
        advice += "上位セラーの一定数が売れていますが、全体の安定性には注意が必要です。\n"
    else:
        advice += "上位セラーに十分な販売が見られず、市場全体の需要にばらつきがあります。\n"

    # 弱セラー状況についてのアドバイス
    if not cond3:
        advice += "弱セラーの成功事例が見られないため、参入には慎重な判断が必要です。\n"
    else:
        if is_top_ranked:
            advice += "弱セラーが上位に位置しており、非常に再現性の高い可能性のある市場です。\n"
        else:
            advice += "弱セラーも成果を出していますが、逆引き順位は中位であり工夫は必要です。\n"

    # 月間検索数が少ない場合のアドバイス
    if mark4 != "🔵":
        advice += "月間検索数が少ないため、ライバル商品の逆引き順位でこの市場がトップにあるか確認してください。"

    # === 出力まとめ ===
    output = (
        f"【判定】：{rank}判定\n"
        f"【条件達成状況】\n"
        f"商品数（競合）：{mark1}\n"
        f"上位セラー・ライバル状況：{mark2}\n"
        f"弱セラー（評価数20以下）が販売数70以上：{mark3}\n"
        f"月間検索数200以上：{mark4}\n\n"
        f"【条件スコア概要】\n"
        f"商品数スコア：{score1}点、上位セラースコア：{score2}点、弱セラースコア：{score3}点、月間検索数スコア：{score4}点\n"
        f"合計スコア：{total_score}点\n\n"
        f"【アドバイス】\n{advice}"
    )

    return output





# ==== ファイルダウンロード ====
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(output_dir, filename, as_attachment=True)

# ==== カテゴリURLからのライバルチェック（簡易API） ====
@app.route("/rival/check", methods=["POST"])
def rival_check_route():
    url = request.form.get("category_url")
    if not url:
        return "URL指定ありません", 400

    try:
        csv_path, rival_count, _ = reverse_lookup.run_rival_check_ranking(url)
        return f"""
            <h2>✅ ライバルチェック完了</h2>
            <p>CSV: {csv_path}</p>
            <p>候補数: {rival_count} 件</p>
            <a href="/market/category">← 戻る</a>
        """
    except Exception as e:
        return f"<h2>❌ エラー: {e}</h2><a href='/market/category'>← 戻る</a>"


# ==== アプリ起動（自動ブラウザ起動付き） ====
from threading import Timer
import webbrowser

def open_browser():
    webbrowser.open_new("http://127.0.0.1:10000")

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=10000)
