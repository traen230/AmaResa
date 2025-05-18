# ✅ 再設計版 top_screen.py（ウィジェット破棄エラー完全回避）
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QTextEdit, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer
import os

from market_screen import MarketResearchScreen
from product_research import ProductResearchWindow
from product_page_builder import ProductPageBuilderWindow

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("アマリサ（Amazon x AIリサーチ）")
        self.resize(800, 600)

        # ログ出力エリア（常時表示）
        self.log_box = QTextEdit()
        self.log_box.setFont(QFont("メイリオ", 10))
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(150)
        self.log_box.setStyleSheet("background-color: white;")

        # 動的に差し替える領域
        self._content_container = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setAlignment(Qt.AlignTop)
        self._content_container.setLayout(self._content_layout)

        # 全体レイアウト構築
        self._main_layout = QVBoxLayout()
        self._main_layout.addWidget(self._content_container)
        self._main_layout.addWidget(self.log_box)

        self._container = QWidget()
        self._container.setLayout(self._main_layout)
        self.setCentralWidget(self._container)

        self._content_container_is_valid = True
        self.show_top_screen()

    def show_screen(self, widget, log_message=""):
        QTimer.singleShot(0, lambda: self._safe_swap_screen(widget, log_message))

    def _safe_swap_screen(self, widget, log_message=""):
        try:
            if not self._content_container_is_valid:
                print("⚠️ _content_container は無効です。画面切替中止")
                return

            for i in reversed(range(self._content_layout.count())):
                old_widget = self._content_layout.itemAt(i).widget()
                if old_widget is not None:
                    old_widget.setParent(None)

            self._content_layout.addWidget(widget)

            if log_message:
                self.append_log(log_message)

        except RuntimeError as e:
            print(f"⚠️ show_screen内で例外発生: {e}")
            self._content_container_is_valid = False
        except Exception as e:
            print(f"⚠️ show_screenで予期しない例外: {e}")
            self._content_container_is_valid = False

    def show_top_screen(self):
        top_widget = self.create_top_screen_widget()
        self.show_screen(top_widget, "🏠 トップ画面に戻りました。")

    def create_top_screen_widget(self):
        grid = QGridLayout()
        grid.setAlignment(Qt.AlignTop)

        image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("画像なし")
        grid.addWidget(image_label, 0, 0)

        market_button = QPushButton("市場リサーチ")
        market_button.setFont(QFont("メイリオ", 10))
        market_button.setFixedWidth(140)
        market_button.clicked.connect(self.open_market_window)
        grid.addWidget(market_button, 1, 0)

        product_button = QPushButton("商品リサーチ")
        product_button.setFont(QFont("メイリオ", 10))
        product_button.setFixedWidth(140)
        product_button.clicked.connect(self.open_product_window)
        grid.addWidget(product_button, 2, 0)

        page_button = QPushButton("商品ページ作成")
        page_button.setFont(QFont("メイリオ", 10))
        page_button.setFixedWidth(140)
        page_button.clicked.connect(self.open_page_builder_window)
        grid.addWidget(page_button, 3, 0)

        h_layout = QHBoxLayout()
        h_layout.addLayout(grid)
        h_layout.setAlignment(Qt.AlignLeft)

        wrapper = QWidget()
        wrapper.setLayout(h_layout)
        return wrapper

    def open_market_window(self):
        self.market_window = MarketResearchScreen(parent=self)
        self.show_screen(self.market_window, "🧭 市場リサーチ画面を開きました。")

    def open_product_window(self):
        self.product_window = ProductResearchWindow(parent=self)
        self.show_screen(self.product_window, "📦 商品リサーチ画面を開きました。")

    def open_page_builder_window(self):
        self.page_window = ProductPageBuilderWindow(parent=self)
        self.show_screen(self.page_window, "📝 商品ページ作成画面を開きました。")

    def append_log(self, text):
        try:
            if hasattr(self, "log_box") and self.log_box:
                self.log_box.append(text)
        except RuntimeError as e:
            print(f"⚠️ ログ出力エラー: {e}")

    def update_selected_category(self, category_name, category_url):
        if hasattr(self, 'market_window'):
            self.market_window.update_selected_category(category_name, category_url)
        self.append_log(f"📂 カテゴリ選択: 『{category_name}』 → {category_url}")