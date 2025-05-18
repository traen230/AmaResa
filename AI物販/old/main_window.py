from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QTextEdit, QSpinBox,
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os

from category_window import CategoryWindow
import rival_checker_ranking  # ライバルチェック処理
import shein_product_list  # SHEIN 処理用

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("アマリサ（Amazon x AIリサーチ）")
        self.adjustSize()

        self.selected_url = ""

        # ------------------------
        # ボタンなどのウィジェット
        # ------------------------
        self.category_button = QPushButton("カテゴリ選択")
        self.category_button.setFont(QFont("メイリオ", 10))
        self.category_button.setFixedWidth(120)
        self.category_button.clicked.connect(self.open_category_window)

        self.rival_button = QPushButton("ライバル調査")
        self.rival_button.setFont(QFont("メイリオ", 10))
        self.rival_button.setFixedHeight(30)
        self.rival_button.setFixedWidth(120)
        self.rival_button.clicked.connect(self.run_rival_check)

        self.other_market_label = QLabel("他販路商品リサーチ：")
        self.other_market_label.setFont(QFont("メイリオ", 10))

        self.similar_check_button = QPushButton("類似チェック")
        self.similar_check_button.setFont(QFont("メイリオ", 10))
        self.similar_check_button.setFixedWidth(120)
        self.similar_check_button.clicked.connect(self.run_similar_check)

        self.similar_result_label = QLabel("候補件数：0 件")
        self.similar_result_label.setFont(QFont("メイリオ", 10))

        self.review_spin = QSpinBox()
        self.review_spin.setFont(QFont("メイリオ", 10))
        self.review_spin.setRange(0, 999)
        self.review_spin.setValue(20)
        self.review_spin.setFixedHeight(30)
        self.review_label = QLabel("評価数以下")
        self.review_label.setFont(QFont("メイリオ", 10))

        self.sales_spin = QSpinBox()
        self.sales_spin.setFont(QFont("メイリオ", 10))
        self.sales_spin.setRange(0, 9999)
        self.sales_spin.setValue(70)
        self.sales_spin.setFixedHeight(30)
        self.sales_label = QLabel("販売数以上")
        self.sales_label.setFont(QFont("メイリオ", 10))

        self.rival_hit_label = QLabel("")
        self.rival_hit_label.setFont(QFont("メイリオ", 10))

        self.shein_button = QPushButton("SHEIN")
        self.shein_button.setFont(QFont("メイリオ", 10))
        self.shein_button.clicked.connect(shein_product_list.run_shein_scraper)

        self.rakuten_button = QPushButton("楽天（工事中）")
        self.rakuten_button.setFont(QFont("メイリオ", 10))

        self.temu_button = QPushButton("TEMU（工事中）")
        self.temu_button.setFont(QFont("メイリオ", 10))

        self.message_label = QLabel("")
        self.message_label.setFont(QFont("メイリオ", 10))

        # ------------------------
        # アイコン画像
        # ------------------------
        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")

        # ------------------------
        # ログ出力欄
        # ------------------------
        self.log_box = QTextEdit()
        self.log_box.setFont(QFont("メイリオ", 10))
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(140)
        self.log_box.setStyleSheet("background-color: white;")

        # ------------------------
        # メインレイアウト
        # ------------------------
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.category_button, 0, 0, alignment=Qt.AlignVCenter)
        layout.addWidget(self.rival_button, 1, 0, alignment=Qt.AlignVCenter)
        layout.addWidget(self.other_market_label, 2, 0, alignment=Qt.AlignVCenter)

        layout.addWidget(self.review_spin, 1, 1)
        layout.addWidget(self.review_label, 1, 2)
        layout.addWidget(self.sales_spin, 1, 3)
        layout.addWidget(self.sales_label, 1, 4)
        layout.addWidget(self.rival_hit_label, 1, 5)

        layout.addWidget(self.shein_button, 2, 1)
        layout.addWidget(self.rakuten_button, 2, 2)
        layout.addWidget(self.temu_button, 2, 3)

        layout.addWidget(self.similar_check_button, 3, 0)
        layout.addWidget(self.similar_result_label, 3, 1, 1, 2)

        layout.addWidget(self.message_label, 0, 1, 1, 6)
        layout.addWidget(self.image_label, 0, 6, 3, 1, alignment=Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(self.log_box, 5, 0, 1, 7)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_category_window(self):
        self.category_window = CategoryWindow(self)
        self.category_window.resize(600, 400)
        self.category_window.show()

    def update_selected_category(self, category_name, category_url):
        self.message_label.setText(f"『{category_name}』のカテゴリが選択されました。")
        self.selected_url = category_url
        self.append_log(f"カテゴリ選択: {category_name} → {category_url}")

    def run_rival_check(self):
        if not self.selected_url:
            self.append_log("⚠️ カテゴリが選択されていません。まずカテゴリを選んでください。")
            return

        review_threshold = self.review_spin.value()
        sales_threshold = self.sales_spin.value()
        rival_checker_ranking.set_rival_criteria(review_threshold, sales_threshold)

        self.append_log("🔍 ライバル調査を開始します...")

        try:
            result = rival_checker_ranking.run_rival_check_ranking(self.selected_url)
            if isinstance(result, tuple) and len(result) == 2:
                file_name, rival_count = result
                self.rival_hit_label.setText(f" 候補商品ヒット: {rival_count}件")
                self.append_log(f"✅ ライバル調査完了。結果を {file_name} に保存しました。")
            else:
                self.rival_hit_label.setText(" 候補商品ヒット: 0件")
                self.append_log("❌ ライバル調査に失敗しました。")
        except Exception as e:
            self.rival_hit_label.setText("ヒット: エラー")
            self.append_log(f"❌ ライバル調査中にエラーが発生しました: {str(e)}")

    def run_similar_check(self):
        try:
            similar_count = 5  # 仮のヒット数。今後処理を実装。
            self.similar_result_label.setText(f"候補件数：{similar_count} 件")
            self.append_log("✅ 類似チェックが完了しました。")
        except Exception as e:
            self.similar_result_label.setText("エラー発生")
            self.append_log(f"❌ 類似チェック中にエラーが発生しました: {e}")

    def run_shein_search(self):
        try:
            shein_product_list.setup_webdriver()

            from tkinter import simpledialog, Tk
            root = Tk()
            root.withdraw()
            keyword = simpledialog.askstring("キーワード入力", "検索キーワードを入力してください：")
            root.destroy()

            if not keyword:
                self.append_log("⚠️ キーワードが入力されませんでした。")
                return

            product_list = shein_product_list.get_product_info_list(keyword)
            product_list = product_list[:50]

            import csv
            with open('amazon_listing.csv', 'w', newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(['商品名', 'URL', '画像URL', '画像pHash'])
                writer.writerows(product_list)

            self.append_log(f"✅ SHEIN検索完了。{keyword} の商品情報を amazon_listing.csv に保存しました。")
        except Exception as e:
            self.append_log(f"❌ SHEIN検索中にエラーが発生しました: {e}")
        finally:
            if shein_product_list.driver:
                shein_product_list.driver.quit()

    def append_log(self, text):
        self.log_box.append(text)
