import subprocess
import os
import sys
import time

# Chromeのパス（必要に応じて調整）
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# 拡張機能のパス（展開済みのSellerSprite拡張ディレクトリ）
extension_dir = r"C:\extensions\SellerSprite"  # ★ここを実際の拡張パスに変更

# ユーザーデータディレクトリ（他と被らないよう専用に）
user_data_dir = r"C:\selenium\ChromeProfile"

# ✅ コマンドライン引数からURLを受け取る（なければ "about:blank" を開く）
url = sys.argv[1] if len(sys.argv) > 1 else "about:blank"

# 起動コマンドを構築
command = [
    chrome_path,
    f"--remote-debugging-port=9222",
    f"--user-data-dir={user_data_dir}",
    f"--load-extension={extension_dir}",
    url  # ← ここでURLを指定する
]

# 実行
print("[INFO] Chrome（SellerSprite拡張付き）を起動します...")
subprocess.Popen(command)
