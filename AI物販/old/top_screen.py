from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QTextEdit, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os

from market_research import MarketResearchWindow
from product_research import ProductResearchWindow
from product_page_builder import ProductPageBuilderWindow

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("アマリサ（Amazon x AIリサーチ）")
        self.resize(800, 600)

        # ログ出力エリア（共通）
        self.log_box = QTextEdit()
        self.log_box.setFont(QFont("メイリオ", 10))
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(150)
        self.log_box.setStyleSheet("background-color: white;")

        self.show_top_screen()

    def show_top_screen(self):
        # グリッドレイアウト（画像とボタン）
        grid = QGridLayout()
        grid.setAlignment(Qt.AlignTop)

        # アイコン画像（左上）
        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")
        grid.addWidget(self.image_label, 0, 0)

        # ボタン：市場リサーチ
        self.market_button = QPushButton("市場リサーチ")
        self.market_button.setFont(QFont("メイリオ", 10))
        self.market_button.setFixedWidth(140)
        self.market_button.clicked.connect(self.open_market_window)
        grid.addWidget(self.market_button, 1, 0)

        # ボタン：商品リサーチ
        self.product_button = QPushButton("商品リサーチ")
        self.product_button.setFont(QFont("メイリオ", 10))
        self.product_button.setFixedWidth(140)
        self.product_button.clicked.connect(self.open_product_window)
        grid.addWidget(self.product_button, 2, 0)

        # ボタン：商品ページ作成
        self.page_button = QPushButton("商品ページ作成")
        self.page_button.setFont(QFont("メイリオ", 10))
        self.page_button.setFixedWidth(140)
        self.page_button.clicked.connect(self.open_page_builder_window)
        grid.addWidget(self.page_button, 3, 0)

        # HBox で左寄せ明示
        h_layout = QHBoxLayout()
        h_layout.addLayout(grid)
        h_layout.setAlignment(Qt.AlignLeft)  # ★ これが中央寄り解消のポイント

        # VBox 全体レイアウト（上詰め + ログ表示）
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addLayout(h_layout)
        layout.addStretch()
        layout.addWidget(self.log_box)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.append_log("🏠 トップ画面に戻りました。")

    def open_market_window(self):
        self.market_window = MarketResearchWindow(parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.market_window)
        layout.addWidget(self.log_box)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.append_log("🧭 市場リサーチ画面を開きました。")

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
        if hasattr(self, 'market_window'):
            self.market_window.update_selected_category(category_name, category_url)
        self.append_log(f"📂 カテゴリ選択: 『{category_name}』 → {category_url}")
