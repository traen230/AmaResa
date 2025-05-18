# ================================================================
# keyword_research.py
#
# 概要:
# このスクリプトは、PyQt5で構築されたキーワード分析用GUI画面です。
# ユーザーが評価数および販売数のクライテリア（関数値）を設定し、
# SellerSprite APIを通じて、Amazonでの有望なキーワードを抽出することができます。
#
# 主な機能:
# - 評価数以下 / 販売数以上 の条件をスピンボックスで指定可能
# - 「キーワード分析」ボタンでCSV一括処理を実行（batch_run_from_csv）
# - 結果ログは親ウィンドウ（main_window）側のログ領域に出力可能
# - 「戻る」ボタンで親画面に戻る
# - ウィンドウの×ボタンでクラッシュせず正しく非表示に戻るよう対策済
#
# 他のスクリプトとの連携:
# - keyword_check.py : 実際のキーワードCSV読み込みと判定処理
# - rival_check.py   : 評価数・販売数の基準設定
# ================================================================

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QSpinBox, QVBoxLayout, QGridLayout, QFileDialog
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

        self.setWindowFlag(Qt.WindowCloseButtonHint, True)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")
        main_layout.addWidget(self.image_label, alignment=Qt.AlignLeft)

        self.title_label = QLabel("キーワードリサーチ")
        self.title_label.setFont(QFont("メイリオ", 12, QFont.Bold))
        main_layout.addWidget(self.title_label)

        criteria_layout = QGridLayout()

        self.review_spin = QSpinBox()
        self.review_spin.setFont(QFont("メイリオ", 10))
        self.review_spin.setRange(0, 999)
        self.review_spin.setValue(20)
        self.review_spin.setFixedHeight(30)
        criteria_layout.addWidget(self.review_spin, 0, 0)

        review_label = QLabel("評価数以下")
        review_label.setFont(QFont("メイリオ", 10))
        criteria_layout.addWidget(review_label, 0, 1)

        self.sales_spin = QSpinBox()
        self.sales_spin.setFont(QFont("メイリオ", 10))
        self.sales_spin.setRange(0, 9999)
        self.sales_spin.setValue(70)
        self.sales_spin.setFixedHeight(30)
        criteria_layout.addWidget(self.sales_spin, 0, 2)

        sales_label = QLabel("販売数以上")
        sales_label.setFont(QFont("メイリオ", 10))
        criteria_layout.addWidget(sales_label, 0, 3)

        main_layout.addLayout(criteria_layout)

        self.keyword_button = QPushButton("キーワード分析")
        self.keyword_button.setFont(QFont("メイリオ", 10))
        self.keyword_button.setFixedWidth(200)
        self.keyword_button.clicked.connect(self.run_keyword_analysis)
        main_layout.addWidget(self.keyword_button)

        self.back_button = QPushButton("◀ 戻る")
        self.back_button.setFont(QFont("メイリオ", 10))
        self.back_button.setFixedWidth(200)
        self.back_button.clicked.connect(self.go_back)
        main_layout.addWidget(self.back_button)

        self.setLayout(main_layout)
        self.adjustSize()

    def run_keyword_analysis(self):
        review_val = self.review_spin.value()
        sales_val = self.sales_spin.value()
        rival_check.set_rival_criteria(review_val, sales_val)

        if hasattr(self.main_window, 'append_log'):
            self.main_window.append_log("🧐 キーワード分析を開始します...")

        try:
            filenames = batch_run_from_csv(review_threshold=review_val, sales_threshold=sales_val)
            if isinstance(filenames, list):
                for file in filenames:
                    self.main_window.append_log(f"✅ 出力ファイル: {file}")
            self.main_window.append_log("✅ キーワード分析が完了しました。")
        except Exception as e:
            self.main_window.append_log(f"❌ エラー: {e}")

    def go_back(self):
        self.hide()
        if hasattr(self.main_window, 'show_top_screen'):
            self.main_window.show_top_screen()

    def closeEvent(self, event):
        event.ignore()
        self.go_back()
