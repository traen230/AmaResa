from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont
import sys
import requests
from bs4 import BeautifulSoup

# ======= 最初に表示するHTML =======
html_content = """
<!DOCTYPE html>
<html lang='ja'>
<head>
<meta charset='UTF-8'>
<style>
body { font-family: メイリオ; font-size: 12px; }
</style>
</head>
<body>
<div class="_p13n-zg-nav-tree-all_style_zg-browse-root__-jwNv" role="tree" id="CardInstancetbHRHb74dUcZIXjg_RAorA" data-card-metrics-id="p13n-zg-nav-tree-all_zeitgeist-lists_1">
                                                    <div class="_p13n-zg-nav-tree-all_style_zg-root-browse-item__2WmBB _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL" role="treeitem">
                                                        <span class="_p13n-zg-nav-tree-all_style_zg-selected__1SfhQ">すべてのカテゴリー</span>
                                                    </div>
                                                    <div role="group" class="_p13n-zg-nav-tree-all_style_zg-browse-group__88fbz">
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/amazon-devices/ref=zg_bs_nav_amazon-devices_0">Amazonデバイス・アクセサリ</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/amazon-renewed/ref=zg_bs_nav_amazon-renewed_0">Amazon整備済み品</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/diy/ref=zg_bs_nav_diy_0">DIY・工具・ガーデン</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/dvd/ref=zg_bs_nav_dvd_0">DVD</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/digital-text/ref=zg_bs_nav_digital-text_0">Kindleストア</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/software/ref=zg_bs_nav_software_0">PCソフト</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/instant-video/ref=zg_bs_nav_instant-video_0">Prime Video</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/mobile-apps/ref=zg_bs_nav_mobile-apps_0">アプリ＆ゲーム</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/toys/ref=zg_bs_nav_toys_0">おもちゃ</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/gift-cards/ref=zg_bs_nav_gift-cards_0">ギフトカード</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/videogames/ref=zg_bs_nav_videogames_0">ゲーム</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/sports/ref=zg_bs_nav_sports_0">スポーツ＆アウトドア</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/dmusic/ref=zg_bs_nav_dmusic_0">デジタルミュージック</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/hpc/ref=zg_bs_nav_hpc_0">ドラッグストア</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/computers/ref=zg_bs_nav_computers_0">パソコン・周辺機器</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/beauty/ref=zg_bs_nav_beauty_0">ビューティー</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/fashion/ref=zg_bs_nav_fashion_0">ファッション</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/pet-supplies/ref=zg_bs_nav_pet-supplies_0">ペット用品</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/baby/ref=zg_bs_nav_baby_0">ベビー＆マタニティ</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0">ホーム＆キッチン</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/hobby/ref=zg_bs_nav_hobby_0">ホビー</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/music/ref=zg_bs_nav_music_0">ミュージック</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/appliances/ref=zg_bs_nav_appliances_0">大型家電</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0">家電＆カメラ</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/office-products/ref=zg_bs_nav_office-products_0">文房具・オフィス用品</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/books/ref=zg_bs_nav_books_0">本</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/musical-instruments/ref=zg_bs_nav_musical-instruments_0">楽器・音響機器</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/english-books/ref=zg_bs_nav_english-books_0">洋書</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/industrial/ref=zg_bs_nav_industrial_0">産業・研究開発用品</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/automotive/ref=zg_bs_nav_automotive_0">車＆バイク</a>
                                                        </div>
                                                        <div role="treeitem" class="_p13n-zg-nav-tree-all_style_zg-browse-item__1rdKf _p13n-zg-nav-tree-all_style_zg-browse-height-small__nleKL">
                                                            <a href="/gp/bestsellers/food-beverage/ref=zg_bs_nav_food-beverage_0">食品・飲料・お酒</a>
                                                        </div>
                                                    </div>
                                                </div>
</body>
</html>
"""

# ======= Webページのカスタムクラス =======
class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            self.parent.fetch_and_update_category(url.toString())
            return False
        return True

# ======= カテゴリ選択ウィンドウクラス =======
class CategoryWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.browser = QWebEngineView()
        self.page = CustomWebEnginePage(self)
        self.browser.setPage(self.page)
        self.history = []
        self.selected_url = ""
        self.selected_text = ""

        self.back_button = QPushButton("戻る")
        self.back_button.setFont(QFont("メイリオ", 12))
        self.back_button.clicked.connect(self.go_back)

        self.ok_button = QPushButton("OK")
        self.ok_button.setFont(QFont("メイリオ", 12))
        self.ok_button.clicked.connect(self.confirm_selection)

        layout = QVBoxLayout()
        layout.addWidget(self.back_button)
        layout.addWidget(self.browser)
        layout.addWidget(self.ok_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.browser.setHtml(html_content, QUrl("https://www.amazon.co.jp"))
        self.setWindowTitle("Amazonカテゴリ選択ツール")
        self.visited_urls = set()

    def fetch_and_update_category(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        if url.startswith("/"):
            url = "https://www.amazon.co.jp" + url

        if url in self.visited_urls:
            self.browser.setHtml("<h2 style='font-family: メイリオ; font-size: 12px;'>これ以上子カテゴリはありません（ループ検出）。</h2>", QUrl("https://www.amazon.co.jp"))
            return

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, "html.parser")

            links = soup.select("div[role='group'] a")

            html = "<h2 style='font-family: メイリオ; font-size: 12px;'>子カテゴリを選択してください</h2><form>"
            for idx, link in enumerate(links):
                href = link.get('href')
                text = link.get_text(strip=True)
                if href:
                    full_url = href if href.startswith("http") else "https://www.amazon.co.jp" + href
                    html += f'<input type="radio" name="category" value="{full_url}" id="cat{idx}">' \
                            f'<label for="cat{idx}" style="font-family: メイリオ; font-size: 12px;">{text}</label> ' \
                            f'<a href="{full_url}" target="_self" style="font-family: メイリオ; font-size: 12px;">▶︎ ドリルダウン</a><br>'
            html += "</form>"

            self.history.append((url, html))
            self.visited_urls.add(url)
            self.browser.setHtml(html, QUrl("https://www.amazon.co.jp"))

        except Exception as e:
            print("エラー発生:", e)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            url, html = self.history[-1]
            self.browser.setHtml(html, QUrl("https://www.amazon.co.jp"))
        else:
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
            print("選択されたURL (OKボタンで確定):", result[0])
            self.selected_url = result[0]
            self.selected_text = result[1]
            self.main_window.update_selected_category(self.selected_text)
            self.close()
        else:
            print("何も選択されていません。")

# ======= メインウィンドウクラス =======
class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("メインメニュー")
        self.resize(600, 400)

        self.category_button = QPushButton("カテゴリ選択")
        self.category_button.setFont(QFont("メイリオ", 10))
        self.category_button.clicked.connect(self.open_category_window)

        self.message_label = QLabel("")
        self.message_label.setFont(QFont("メイリオ", 10))

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.category_button)
        h_layout.addWidget(self.message_label)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)

        container = QWidget()
        container.setLayout(v_layout)
        self.setCentralWidget(container)

    def open_category_window(self):
        self.category_window = CategoryWindow(self)
        self.category_window.resize(600, 400)
        self.category_window.show()

    def update_selected_category(self, category_name):
        self.message_label.setText(f"『{category_name}』")

# ======= アプリケーション起動部分 =======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("メイリオ", 10))
    window = MainAppWindow()
    window.show()
    sys.exit(app.exec_())
