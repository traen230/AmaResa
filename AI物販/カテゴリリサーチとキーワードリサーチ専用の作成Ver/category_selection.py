from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QUrl
import requests
from bs4 import BeautifulSoup
import os

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            self.parent.fetch_and_update_category(url.toString())
            return False
        return True

class CategoryWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.browser = QWebEngineView()
        self.page = CustomWebEnginePage(self)
        self.browser.setPage(self.page)
        self.history = []
        self.visited_urls = set()
        self.selected_url = ""
        self.selected_text = ""

        # 戻るボタン
        self.back_button = QPushButton("戻る")
        self.back_button.setFont(QFont("メイリオ", 10))
        self.back_button.clicked.connect(self.go_back)

        # OKボタン
        self.ok_button = QPushButton("OK")
        self.ok_button.setFont(QFont("メイリオ", 10))
        self.ok_button.clicked.connect(self.confirm_selection)

        # レイアウト構成
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.back_button)
        btn_layout.addWidget(self.ok_button)
        layout.addLayout(btn_layout)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 初期HTML読み込み
        html_path = os.path.join(os.path.dirname(__file__), "resources", "category.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            self.browser.setHtml(html_content, QUrl("https://www.amazon.co.jp"))
        else:
            self.browser.setHtml("<h2>カテゴリHTMLが見つかりません</h2>", QUrl("about:blank"))

        self.setWindowTitle("Amazonカテゴリ選択ツール")

    def fetch_and_update_category(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        if url.startswith("/"):
            url = "https://www.amazon.co.jp" + url

        if url in self.visited_urls:
            self.browser.setHtml("<h2 style='font-family: メイリオ; font-size: 10px;'>これ以上子カテゴリはありません（ループ検出）。</h2>", QUrl("about:blank"))
            return

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, "html.parser")
            links = soup.select("div[role='group'] a")

            if not links:
                html = "<h2 style='font-family: メイリオ; font-size: 10px;'>これ以上子カテゴリはありません。</h2>"
            else:
                html = "<h2 style='font-family: メイリオ; font-size: 10px;'>子カテゴリを選択してください</h2><form>"
                for idx, link in enumerate(links):
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if href:
                        full_url = href if href.startswith("http") else "https://www.amazon.co.jp" + href
                        html += f'<input type="radio" name="category" value="{full_url}" id="cat{idx}">' \
                                f'<label for="cat{idx}" style="font-family: メイリオ; font-size: 10px;">{text}</label> ' \
                                f'<a href="{full_url}" target="_self" style="font-family: メイリオ; font-size: 10px;">▶︎ ドリルダウン</a><br>'
                html += "</form>"

            self.history.append((url, html))
            self.visited_urls.add(url)
            self.browser.setHtml(html, QUrl("https://www.amazon.co.jp"))

        except Exception as e:
            self.browser.setHtml(f"<h2>エラー: {e}</h2>", QUrl("about:blank"))

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            url, html = self.history[-1]
            self.browser.setHtml(html, QUrl("https://www.amazon.co.jp"))
        else:
            html_path = os.path.join(os.path.dirname(__file__), "resources", "category.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                self.browser.setHtml(html_content, QUrl("https://www.amazon.co.jp"))

    def confirm_selection(self):
        script = """
        var radios = document.getElementsByName('category');
        var selected = '';
        var labelText = '';
        for (var i = 0; i < radios.length; i++) {
            if (radios[i].checked) {
                selected = radios[i].value;
                labelText = document.querySelector('label[for="' + radios[i].id + '"]').innerText;
                break;
            }
        }
        [selected, labelText];
        """
        self.browser.page().runJavaScript(script, self.handle_selection)

    def handle_selection(self, result):
        if result and result[0]:
            self.selected_url = result[0]
            self.selected_text = result[1]
            self.main_window.update_selected_category(self.selected_text, self.selected_url)
            self.close()
        else:
            print("何も選択されていません。")
