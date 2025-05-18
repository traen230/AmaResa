import csv
import time
from datetime import datetime
from urllib.parse import quote
from tkinter import messagebox, filedialog, Tk, Toplevel, Label, Button
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QSpinBox, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os

from category_selection import CategoryWindow
import rival_check
from sellersprite_reverse_asin import reverse_keyword_search
# 循環インポートを避けるため keyword_check は後でインポート

class Ranking_ResearchWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.selected_url = ""

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")
        layout.addWidget(self.image_label, alignment=Qt.AlignLeft)

        # タイトル
        self.title_label = QLabel("ランキングリサーチ")
        self.title_label.setFont(QFont("メイリオ", 12, QFont.Bold))
        layout.addWidget(self.title_label)

        grid = QGridLayout()
        grid.setAlignment(Qt.AlignTop)

        self.category_button = QPushButton("カテゴリ選択")
        self.category_button.setFont(QFont("メイリオ", 10))
        self.category_button.setFixedWidth(140)
        self.category_button.clicked.connect(self.open_category_window)
        grid.addWidget(self.category_button, 0, 0)

        self.message_label = QLabel("")
        self.message_label.setFont(QFont("メイリオ", 10))
        grid.addWidget(self.message_label, 0, 1, 1, 5)

        self.rival_button = QPushButton("ライバルチェック")
        self.rival_button.setFont(QFont("メイリオ", 10))
        self.rival_button.setFixedWidth(140)
        self.rival_button.clicked.connect(self.run_rival_check)
        grid.addWidget(self.rival_button, 1, 0)

        self.review_spin = QSpinBox()
        self.review_spin.setFont(QFont("メイリオ", 10))
        self.review_spin.setRange(0, 999)
        self.review_spin.setValue(20)
        self.review_spin.setFixedHeight(30)
        grid.addWidget(self.review_spin, 1, 1)

        self.review_label = QLabel("評価数以下")
        self.review_label.setFont(QFont("メイリオ", 10))
        grid.addWidget(self.review_label, 1, 2)

        self.sales_spin = QSpinBox()
        self.sales_spin.setFont(QFont("メイリオ", 10))
        self.sales_spin.setRange(0, 9999)
        self.sales_spin.setValue(70)
        self.sales_spin.setFixedHeight(30)
        grid.addWidget(self.sales_spin, 1, 3)

        self.sales_label = QLabel("販売数以上")
        self.sales_label.setFont(QFont("メイリオ", 10))
        grid.addWidget(self.sales_label, 1, 4)

        self.result_label = QLabel("")
        self.result_label.setFont(QFont("メイリオ", 10))
        grid.addWidget(self.result_label, 1, 5)

        self.niche_button = QPushButton("逆引きリサーチ")
        self.niche_button.setFont(QFont("メイリオ", 10))
        self.niche_button.setFixedWidth(140)
        self.niche_button.clicked.connect(self.run_reverse_keyword_search)
        grid.addWidget(self.niche_button, 2, 0)

        self.asin_input = QLineEdit()
        self.asin_input.setPlaceholderText("ASINを入力")
        self.asin_input.setFont(QFont("メイリオ", 10))
        self.asin_input.setFixedWidth(200)
        grid.addWidget(self.asin_input, 2, 1, 1, 2)

        self.keyword_button = QPushButton("キーワード分析")
        self.keyword_button.setFont(QFont("メイリオ", 10))
        self.keyword_button.setFixedWidth(140)
        self.keyword_button.clicked.connect(self.run_keyword_analysis)
        grid.addWidget(self.keyword_button, 3, 0)

        self.review_spin_keyword = QSpinBox()
        self.review_spin_keyword.setFont(QFont("メイリオ", 10))
        self.review_spin_keyword.setRange(0, 999)
        self.review_spin_keyword.setValue(20)
        self.review_spin_keyword.setFixedHeight(30)
        grid.addWidget(self.review_spin_keyword, 3, 1)

        self.review_label_keyword = QLabel("評価数以下")
        self.review_label_keyword.setFont(QFont("メイリオ", 10))
        grid.addWidget(self.review_label_keyword, 3, 2)

        self.sales_spin_keyword = QSpinBox()
        self.sales_spin_keyword.setFont(QFont("メイリオ", 10))
        self.sales_spin_keyword.setRange(0, 9999)
        self.sales_spin_keyword.setValue(70)
        self.sales_spin_keyword.setFixedHeight(30)
        grid.addWidget(self.sales_spin_keyword, 3, 3)

        self.sales_label_keyword = QLabel("販売数以上")
        self.sales_label_keyword.setFont(QFont("メイリオ", 10))
        grid.addWidget(self.sales_label_keyword, 3, 4)

        self.back_button = QPushButton("◀ 戻る")
        self.back_button.setFont(QFont("メイリオ", 10))
        self.back_button.setFixedWidth(140)
        self.back_button.clicked.connect(self.go_back)
        grid.addWidget(self.back_button, 4, 0)

        layout.addLayout(grid)
        self.setLayout(layout)
        self.adjustSize()

    def open_category_window(self):
        self.category_window = CategoryWindow(self)
        self.category_window.resize(600, 400)
        self.category_window.show()

    def update_selected_category(self, category_name, category_url):
        self.selected_url = category_url
        self.message_label.setText(f"『{category_name}』を選択しました。")

    def run_rival_check(self):
        if not self.selected_url:
            if hasattr(self.main_window, 'append_log'):
                self.main_window.append_log("⚠️ カテゴリが選択されていません。")
            return

        review_val = self.review_spin.value()
        sales_val = self.sales_spin.value()
        rival_check.set_rival_criteria(review_val, sales_val)

        if hasattr(self.main_window, 'append_log'):
            self.main_window.append_log("🔍 ライバルチェックを開始します...")

        try:
            file_name, rival_count = rival_check.run_rival_check_ranking(self.selected_url)
            if file_name:
                self.result_label.setText(f"ヒット: {rival_count}件")
                self.main_window.append_log(f"✅ {rival_count} 件のライバル候補を発見し、{file_name} に保存しました。")
            else:
                self.result_label.setText("ヒット: 0件")
                self.main_window.append_log("❌ ライバルチェックに失敗しました。")
        except Exception as e:
            self.result_label.setText("エラー発生")
            self.main_window.append_log(f"❌ ライバルチェック中にエラーが発生しました: {e}")

    def run_reverse_keyword_search(self):
        asin = self.asin_input.text().strip()
        if not asin:
            self.main_window.append_log("⚠️ ASINを入力してください。")
            return

        self.main_window.append_log(f"🔍 ASIN '{asin}' の逆引きキーワードを取得中...")
        try:
            filename = reverse_keyword_search(asin)
            if filename:
                self.main_window.append_log(f"✅ トラフィック比率上位5件を '{filename}' に出力しました。")
            else:
                self.main_window.append_log("❌ データ取得に失敗しました。")
        except Exception as e:
            self.main_window.append_log(f"❌ エラー発生: {e}")

    def run_keyword_analysis(self):
        from keyword_check import batch_run_from_csv, set_rival_criteria

        review_val = self.review_spin_keyword.value()
        sales_val = self.sales_spin_keyword.value()
        set_rival_criteria(review_val, sales_val)

        self.main_window.append_log("🧠 キーワード分析を開始します...")
        try:
            filenames = batch_run_from_csv(mode="auto_file")
            if isinstance(filenames, list):
                for file in filenames:
                    self.main_window.append_log(f"✅ 出力ファイル: {file}")
            self.main_window.append_log("✅ キーワード分析が完了しました。")
        except Exception as e:
            self.main_window.append_log(f"❌ キーワード分析中にエラーが発生しました: {e}")

    def go_back(self):
        if hasattr(self.main_window, 'show_top_screen'):
            self.main_window.show_top_screen()
