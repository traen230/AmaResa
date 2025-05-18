# keyword_research.py
# このスクリプトは、ユーザーがPyQt5インターフェースを通じてキーワード分析を実行できる画面を提供します。
# 評価数と販売数のクライテリアを設定し、それに基づいたSellerSprite経由のAmazonキーワード分析を実施します。

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QSpinBox, QVBoxLayout, QGridLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os

from keyword_check import batch_run_from_csv
import rival_check

class Keyword_ResearchWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # アイコン画像
        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")
        layout.addWidget(self.image_label, alignment=Qt.AlignLeft)

        # タイトル
        self.title_label = QLabel("キーワードリサーチ")
        self.title_label.setFont(QFont("メイリオ", 12, QFont.Bold))
        layout.addWidget(self.title_label)

        # クライテリア設定
        criteria_grid = QGridLayout()

        self.review_spin = QSpinBox()
        self.review_spin.setFont(QFont("メイリオ", 10))
        self.review_spin.setRange(0, 999)
        self.review_spin.setValue(20)
        self.review_spin.setFixedHeight(30)
        criteria_grid.addWidget(self.review_spin, 0, 0)

        self.review_label = QLabel("評価数以下")
        self.review_label.setFont(QFont("メイリオ", 10))
        criteria_grid.addWidget(self.review_label, 0, 1)

        self.sales_spin = QSpinBox()
        self.sales_spin.setFont(QFont("メイリオ", 10))
        self.sales_spin.setRange(0, 9999)
        self.sales_spin.setValue(70)
        self.sales_spin.setFixedHeight(30)
        criteria_grid.addWidget(self.sales_spin, 0, 2)

        self.sales_label = QLabel("販売数以上")
        self.sales_label.setFont(QFont("メイリオ", 10))
        criteria_grid.addWidget(self.sales_label, 0, 3)

        layout.addLayout(criteria_grid)

        # キーワード分析ボタン
        self.keyword_button = QPushButton("キーワード分析")
        self.keyword_button.setFont(QFont("メイリオ", 10))
        self.keyword_button.setFixedWidth(140)
        self.keyword_button.clicked.connect(self.run_keyword_analysis)
        layout.addWidget(self.keyword_button)

        # 戻るボタン
        self.back_button = QPushButton("◀ 戻る")
        self.back_button.setFont(QFont("メイリオ", 10))
        self.back_button.setFixedWidth(140)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        self.adjustSize()

    def run_keyword_analysis(self):
        review_val = self.review_spin.value()
        sales_val = self.sales_spin.value()
        rival_check.set_rival_criteria(review_val, sales_val)

        if hasattr(self.main_window, 'append_log'):
            self.main_window.append_log("🧠 キーワード分析を開始します...")

        try:
            filenames = batch_run_from_csv(review_threshold=review_val, sales_threshold=sales_val)
            if isinstance(filenames, list):
                for file in filenames:
                    self.main_window.append_log(f"✅ 出力ファイル: {file}")
            self.main_window.append_log("✅ キーワード分析が完了しました。")
        except Exception as e:
            self.main_window.append_log(f"❌ キーワード分析中にエラーが発生しました: {e}")

    def go_back(self):
        if hasattr(self.main_window, 'show_top_screen'):
            self.main_window.show_top_screen()
