# product_page_builder.py
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os

class ProductPageBuilderWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.image_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("画像なし")
        layout.addWidget(self.image_label)

        self.persona_button = QPushButton("ペルソナ作成")
        self.persona_button.setFont(QFont("メイリオ", 10))
        self.persona_button.setFixedWidth(140)
        layout.addWidget(self.persona_button)

        self.image_button = QPushButton("画像素材作成")
        self.image_button.setFont(QFont("メイリオ", 10))
        self.image_button.setFixedWidth(140)
        layout.addWidget(self.image_button)

        self.page_asset_button = QPushButton("商品ページ（素材）")
        self.page_asset_button.setFont(QFont("メイリオ", 10))
        self.page_asset_button.setFixedWidth(140)
        layout.addWidget(self.page_asset_button)

        self.back_button = QPushButton("◀ 戻る")
        self.back_button.setFont(QFont("メイリオ", 10))
        self.back_button.setFixedWidth(140)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        self.adjustSize()

    def go_back(self):
        if hasattr(self.parent, 'show_top_screen'):
            self.parent.show_top_screen()