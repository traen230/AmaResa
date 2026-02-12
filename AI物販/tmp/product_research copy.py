# product_research.py
# このスクリプトは、SHEIN・楽天・TEMUなどの他販路リサーチをGUI上で実行するPyQt5インターフェースを提供します。
# それぞれのリサーチ機能はボタンで起動し、ログ出力連携も可能です。

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os
import subprocess
import shein_research

class ProductResearchWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # アイコン画像
        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")

        # タイトル
        self.title_label = QLabel("商品リサーチ")
        self.title_label.setFont(QFont("メイリオ", 12, QFont.Bold))

        # 各ボタン
        self.shein_button = QPushButton("SHEINリサーチ")
        self.shein_button.setFont(QFont("メイリオ", 10))
        self.shein_button.setFixedWidth(140)
        self.shein_button.clicked.connect(self.run_shein_with_log)

        self.rakuten_button = QPushButton("楽天リサーチ")
        self.rakuten_button.setFont(QFont("メイリオ", 10))
        self.rakuten_button.setFixedWidth(140)

        self.temu_button = QPushButton("TEMUリサーチ")
        self.temu_button.setFont(QFont("メイリオ", 10))
        self.temu_button.setFixedWidth(140)

        self.unique_button = QPushButton("独自商品チェック")
        self.unique_button.setFont(QFont("メイリオ", 10))
        self.unique_button.setFixedWidth(140)
        self.unique_button.clicked.connect(self.run_unique_checker_subprocess)

        self.back_button = QPushButton("◀ 戻る")
        self.back_button.setFont(QFont("メイリオ", 10))
        self.back_button.setFixedWidth(140)
        self.back_button.clicked.connect(self.go_back)

        # ボタンの縦レイアウト
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.shein_button)
        button_layout.addWidget(self.rakuten_button)
        button_layout.addWidget(self.temu_button)
        button_layout.addWidget(self.unique_button)
        button_layout.addWidget(self.back_button)
        button_layout.addStretch()

        # メインレイアウト
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label, alignment=Qt.AlignLeft)
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.adjustSize()

    def run_shein_with_log(self):
        if hasattr(self.parent, 'append_log'):
            shein_research.set_log_callback(self.parent.append_log)
        shein_research.run_shein_scraper()

    def go_back(self):
        if hasattr(self.parent, 'show_top_screen'):
            self.parent.show_top_screen()

    # ✅ 独自商品チェックを別プロセスで起動
    def run_unique_checker_subprocess(self):
        script_path = os.path.join(os.path.dirname(__file__), "unique_product_candidate_selector.py")
        subprocess.Popen(["python", script_path])
