from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# --- 環境に合わせて設定 ---
CHROMEDRIVER = r"C:\Users\SOICHIRO SAHARA\Documents\BizBright\04 Script\99 temp\chromedriver-win64\chromedriver-win64\chromedriver.exe"
EXTENSION_PATH = r"C:\Users\SOICHIRO SAHARA\AppData\Local\Google\Chrome\User Data\Default\Extensions\lnbmbgocenenhhhdojdielgnmeflbnfb\4.7.5_0"

# --- Selenium起動設定 ---
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f"--load-extension={EXTENSION_PATH}")

service = Service(executable_path=CHROMEDRIVER)
driver = webdriver.Chrome(service=service, options=options)

# ✅ 検索キーワード指定（自由に変更OK）
keyword = "USB ハブ"
url = f"https://www.amazon.co.jp/s?k={keyword}"
driver.get(url)

input("🔐 拡張機能が表示されたら Enter を押してください...")

# ✅ 「直近30日販売数（親）」を含むDIVから販売数を抽出
try:
    boxes = driver.find_elements(By.XPATH, "//div[span[contains(text(), '直近30日販売数（親）')]]")
    print(f"\n🟢 発見した販売数ブロック数: {len(boxes)} 件\n")

    for i, box in enumerate(boxes, 1):
        try:
            value_span = box.find_element(By.CSS_SELECTOR, "span.exts-color-border-black.grade-hover")
            sales = value_span.text.strip().replace(",", "")
            print(f"商品{i}: {sales} 件")
        except Exception as e:
            print(f"商品{i}: ❌ 販売数の取得失敗 - {e}")
except Exception as e:
    print(f"❌ 全体エラー: {e}")

# ※ 終了は手動確認後
# driver.quit()
