# custom_web_page.py
# Webリンククリック制御クラス

from PyQt5.QtWebEngineWidgets import QWebEnginePage

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # リンクがクリックされたときにのみ動作する
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            self.parent.fetch_and_update_category(url.toString())
            return False  # デフォルトの遷移は止める（自分で制御する）
        return True
