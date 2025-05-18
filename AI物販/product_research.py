from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QDialog, QInputDialog
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os
import subprocess

import shein_research
import rakuten_research


class ProductResearchWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")

        self.title_label = QLabel("商品リサーチ")
        self.title_label.setFont(QFont("メイリオ", 12, QFont.Bold))

        self.shein_button = QPushButton("SHEINリサーチ")
        self.shein_button.setFont(QFont("メイリオ", 10))
        self.shein_button.setFixedWidth(200)
        self.shein_button.clicked.connect(self.show_shein_mode_dialog)

        self.rakuten_button = QPushButton("楽天リサーチ")
        self.rakuten_button.setFont(QFont("メイリオ", 10))
        self.rakuten_button.setFixedWidth(200)
        self.rakuten_button.clicked.connect(self.show_rakuten_mode_dialog)

        self.temu_button = QPushButton("TEMUリサーチ（未実装）")
        self.temu_button.setFont(QFont("メイリオ", 10))
        self.temu_button.setFixedWidth(200)

        self.unique_button = QPushButton("独自商品チェック")
        self.unique_button.setFont(QFont("メイリオ", 10))
        self.unique_button.setFixedWidth(200)
        self.unique_button.clicked.connect(self.run_unique_checker_subprocess)

        self.back_button = QPushButton("◀ 戻る")
        self.back_button.setFont(QFont("メイリオ", 10))
        self.back_button.setFixedWidth(200)
        self.back_button.clicked.connect(self.go_back)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.shein_button)
        button_layout.addWidget(self.rakuten_button)
        button_layout.addWidget(self.temu_button)
        button_layout.addWidget(self.unique_button)
        button_layout.addWidget(self.back_button)
        button_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label, alignment=Qt.AlignLeft)
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.adjustSize()

    # ✅ SHEIN リサーチ モード選択
    def show_shein_mode_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("SHEINリサーチモード選択")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("リサーチ方法を選択してください"))

        manual_btn = QPushButton("キーワードを手入力して検索")
        csv_btn = QPushButton("CSVからキーワード読み込み")

        layout.addWidget(manual_btn)
        layout.addWidget(csv_btn)

        manual_btn.clicked.connect(lambda: (dialog.accept(), self.run_shein_manual()))
        csv_btn.clicked.connect(lambda: (dialog.accept(), self.run_shein_csv()))

        dialog.setLayout(layout)
        dialog.exec_()

    def run_shein_manual(self):
        keyword, ok = QInputDialog.getText(self, "SHEINリサーチ", "検索キーワードを入力：")
        if ok and keyword.strip():
            if hasattr(self.parent, 'append_log'):
                self.parent.append_log(f"SHEINリサーチ: {keyword.strip()}")
                shein_research.set_log_callback(self.parent.append_log)
            shein_research.run_shein_scraper_from_keyword(keyword.strip())

    def run_shein_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSVファイル選択", "", "CSV Files (*.csv)")
        if path:
            if hasattr(self.parent, 'append_log'):
                self.parent.append_log(f"SHEIN CSV実行: {path}")
                shein_research.set_log_callback(self.parent.append_log)
            shein_research.run_shein_scraper_from_csv(path)

    # ✅ 楽天リサーチ モード選択
    def show_rakuten_mode_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("楽天リサーチモード選択")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("リサーチ方法を選択してください"))

        manual_btn = QPushButton("キーワードを手入力して検索")
        csv_btn = QPushButton("CSVからキーワード読み込み")

        layout.addWidget(manual_btn)
        layout.addWidget(csv_btn)

        manual_btn.clicked.connect(lambda: (dialog.accept(), self.run_rakuten_manual()))
        csv_btn.clicked.connect(lambda: (dialog.accept(), self.run_rakuten_csv()))

        dialog.setLayout(layout)
        dialog.exec_()

    def run_rakuten_manual(self):
        keyword, ok = QInputDialog.getText(self, "楽天リサーチ", "検索キーワードを入力：")
        if ok and keyword.strip():
            if hasattr(self.parent, 'append_log'):
                self.parent.append_log(f"楽天リサーチ: {keyword.strip()}")
            rakuten_research.run_rakuten_scraper(keyword.strip())

    def run_rakuten_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSVファイル選択", "", "CSV Files (*.csv)")
        if path:
            if hasattr(self.parent, 'append_log'):
                self.parent.append_log(f"楽天 CSV実行: {path}")
            rakuten_research.run_rakuten_scraper_from_csv(path)

    def run_unique_checker_subprocess(self):
        script_path = os.path.join(os.path.dirname(__file__), "unique_product_candidate_selector.py")
        subprocess.Popen(["python", script_path])

    def go_back(self):
        if hasattr(self.parent, 'show_top_screen'):
            self.parent.show_top_screen()
