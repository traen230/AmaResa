# ✅ 再設計版 top_screen.py（市場リサーチボタン縦配置）
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QTextEdit, QWidget,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os

from ranking_research import Ranking_ResearchWindow
from product_research import ProductResearchWindow
from product_page_builder import ProductPageBuilderWindow
from keyword_research import Keyword_ResearchWindow  # ← 追加

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("アマリサ（Amazon x AIリサーチ）")
        self.resize(800, 600)

        self.log_box = QTextEdit()
        self.log_box.setFont(QFont("メイリオ", 10))
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(150)
        self.log_box.setStyleSheet("background-color: white;")

        self.show_top_screen()

    def show_top_screen(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # アイコン
        icon_layout = QHBoxLayout()
        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")
        icon_layout.addWidget(self.image_label)
        icon_layout.setAlignment(Qt.AlignLeft)
        layout.addLayout(icon_layout)

        # 市場リサーチボタン（縦配置）
        market_column = QVBoxLayout()
        market_column.setSpacing(10)

        self.category_button = QPushButton("市場リサーチ（カテゴリリサーチ）")
        self.category_button.setFont(QFont("メイリオ", 10))
        self.category_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.category_button.clicked.connect(self.open_ranking_window)

        self.keyword_button = QPushButton("市場リサーチ（キーワードリサーチ）")
        self.keyword_button.setFont(QFont("メイリオ", 10))
        self.keyword_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.keyword_button.clicked.connect(self.open_keyword_window)  # ← 呼び出し先変更

        market_column.addWidget(self.category_button)
        market_column.addWidget(self.keyword_button)
        layout.addLayout(market_column)

        # 線1
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line1)

        # 商品リサーチボタン
        self.product_button = QPushButton("商品リサーチ")
        self.product_button.setFont(QFont("メイリオ", 10))
        self.product_button.clicked.connect(self.open_product_window)
        layout.addWidget(self.product_button)

        # 線2
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # 商品ページ作成ボタン
        self.page_button = QPushButton("商品ページ作成")
        self.page_button.setFont(QFont("メイリオ", 10))
        self.page_button.clicked.connect(self.open_page_builder_window)
        layout.addWidget(self.page_button)

        # ログ出力エリア
        layout.addStretch()
        layout.addWidget(self.log_box)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.append_log("🏠 トップ画面に戻りました。")

    def open_ranking_window(self):
        self.ranking_window = Ranking_ResearchWindow(parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.ranking_window)
        layout.addWidget(self.log_box)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.append_log("📊 ランキングリサーチ画面を開きました。")

    def open_keyword_window(self):  # ← 新規追加
        self.keyword_window = Keyword_ResearchWindow(parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.keyword_window)
        layout.addWidget(self.log_box)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.append_log("🔍 キーワードリサーチ画面を開きました。")

    def open_product_window(self):
        self.product_window = ProductResearchWindow(parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.product_window)
        layout.addWidget(self.log_box)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.append_log("📦 商品リサーチ画面を開きました。")

    def open_page_builder_window(self):
        self.page_window = ProductPageBuilderWindow(parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.page_window)
        layout.addWidget(self.log_box)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.append_log("📝 商品ページ作成画面を開きました。")

    def append_log(self, text):
        if hasattr(self, "log_box"):
            self.log_box.append(text)

    def update_selected_category(self, category_name, category_url):
        if hasattr(self, 'ranking_window'):
            self.ranking_window.update_selected_category(category_name, category_url)
        self.append_log(f"📂 カテゴリ選択: 『{category_name}』 → {category_url}")
