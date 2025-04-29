# main_window.py
# アプリのメイン画面クラス

from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QFont
from category_window import CategoryWindow

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("メインメニュー")
        self.resize(600, 400)

        # 「カテゴリ選択」ボタン作成
        self.category_button = QPushButton("カテゴリ選択")
        self.category_button.setFont(QFont("メイリオ", 10))
        self.category_button.clicked.connect(self.open_category_window)

        # 選択結果表示用ラベル作成
        self.message_label = QLabel("")
        self.message_label.setFont(QFont("メイリオ", 10))

        # 横並びレイアウト
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.category_button)
        h_layout.addWidget(self.message_label)

        # 縦並びレイアウトに追加
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)

        # ウィジェットセット
        container = QWidget()
        container.setLayout(v_layout)
        self.setCentralWidget(container)

    def open_category_window(self):
        # カテゴリ選択ウィンドウを開く
        self.category_window = CategoryWindow(self)
        self.category_window.resize(600, 400)
        self.category_window.show()

    def update_selected_category(self, category_name):
        # カテゴリが選択されたときにラベルに表示
        self.message_label.setText(f"『{category_name}』")
