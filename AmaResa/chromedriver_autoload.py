"""
chromedriver_autoload.py

このモジュールは、アプリケーションに同梱された `chromedriver.exe` を使って、
環境に依存せずに Selenium Chrome WebDriver を起動するためのユーティリティです。

主な用途:
- PyInstaller等でEXE化したFlaskアプリからのドライバ起動
- ヘッドレスChromeの安全な自動起動
- 相対パスでのchromedriver読込によるパスエラー防止
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def resource_path(relative_path):
    """PyInstaller環境に対応したリソースパス解決"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_driver():
    try:
        driver_path = resource_path("driver/chromedriver.exe")
        print(f"[DEBUG] driver_path={driver_path}")  # パス解決結果を確認
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        print("[DEBUG] Selenium driver init start")
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
        print("[INFO] Chrome（SellerSprite拡張付き）を起動します...")
        return driver
    except Exception as e:
        print(f"[ERROR] Selenium driver起動失敗: {e}")
        raise

