# app.py
# アプリケーションの起動スクリプト

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
import sys
from main_window import MainAppWindow

if __name__ == "__main__":
    # PyQtアプリケーションを初期化
    app = QApplication(sys.argv)

    # 全体フォントを設定
    app.setFont(QFont("メイリオ", 10))

    # メインウィンドウを作成して表示
    window = MainAppWindow()
    window.show()

    # アプリケーション実行
    sys.exit(app.exec_())
