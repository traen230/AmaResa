# amaresa_startup.py

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
import sys
from top_screen import MainAppWindow  # ← ファイル名に合わせて変更

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setFont(QFont("メイリオ", 10))

        window = MainAppWindow()
        window.show()

        print("✅ アプリケーションを起動しました。")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"❌ アプリケーションの起動に失敗しました: {e}")
