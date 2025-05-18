from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# 仮のインポート（必要に応じて実装済みのウィンドウに変更してください）
from ranking_research import Ranking_ResearchWindow
#from keyword_research import KeywordResearchWindow  # ←このファイルも用意してください

class MarketResearchScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # タイトルラベル
        title_label = QLabel("市場リサーチメニュー")
        title_label.setFont(QFont("メイリオ", 12, QFont.Bold))
        layout.addWidget(title_label)

        # カテゴリリサーチボタン
        self.category_button = QPushButton("カテゴリリサーチ")
        self.category_button.setFont(QFont("メイリオ", 10))
        self.category_button.clicked.connect(self.open_category_research)
        layout.addWidget(self.category_button)

        # キーワードリサーチボタン
        self.keyword_button = QPushButton("キーワードリサーチ")
        self.keyword_button.setFont(QFont("メイリオ", 10))
        self.keyword_button.clicked.connect(self.open_keyword_research)
        layout.addWidget(self.keyword_button)

        self.setLayout(layout)

    def open_category_research(self):
        if self.parent_window:
            self.parent_window.market_window = Ranking_ResearchWindow(parent=self.parent_window)
            self.parent_window.setCentralWidget(self.parent_window.market_window)
            self.parent_window.append_log("📊 カテゴリリサーチを開始しました。")

    def open_keyword_research(self):
        if self.parent_window:
            self.parent_window.market_window = KeywordResearchWindow(parent=self.parent_window)
            self.parent_window.setCentralWidget(self.parent_window.market_window)
            self.parent_window.append_log("🔍 キーワードリサーチを開始しました。")
