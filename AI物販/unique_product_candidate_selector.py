# ===============================================================
# スクリプト名: unique_product_candidate_selector.py
# 説明:
#   本スクリプトは、Amazonの商品画像と他販路（例: SHEIN）の商品画像を比較し、
#   ResNet50 によって抽出した画像特徴量のコサイン類似度を計算します。
# 
#   類似度が 0.8 未満の商品は「類似していない＝独自性が高い」と判定され、
#   独自商品候補としてCSVに出力されます。
#
# 機能:
#   - '//' から始まる画像URLを 'https://' に自動補完
#   - WebP形式の画像に対応（PillowがWebP対応であることが前提）
#   - User-AgentとRefererを設定してCDN制限を回避（SHEIN対策）
#   - 出力ファイル:
#       - 類似商品比較リスト.csv: 全件の比較結果
#       - 独自商品候補リスト.csv: 類似度0.8未満の独自商品候補のみ
#
# 使い方:
#   1. 他販路の商品CSVファイルを選択（画像URLはD列、商品URLはA列）
#   2. Amazonの商品CSVファイルを選択（画像URLはE列、販売数はF列）
#   3. 「OK」ボタンを押すと処理が実行され、CSVが出力されます
# ===============================================================

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import requests
import os
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity

# ===== モデル読み込みと変数定義 =====
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
listing_path = ""
amazon_path = ""

# ===== 特徴ベクトル抽出関数 =====
def get_feature_vector(img_path_or_url):
    try:
        if img_path_or_url.startswith("//"):
            img_path_or_url = "https:" + img_path_or_url

        if img_path_or_url.startswith("http"):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Referer': 'https://www.shein.com/'
            }
            response = requests.get(img_path_or_url.strip(), headers=headers, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            img = Image.open(img_path_or_url.strip()).convert("RGB")

        img = img.resize((224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        return model.predict(x)[0]
    except Exception as e:
        print(f"画像取得エラー: {img_path_or_url} - {e}")
        return None

# ===== メイン処理関数（類似度計算＆CSV出力） =====
def process_files():
    if not listing_path or not amazon_path:
        messagebox.showerror("エラー", "両方のCSVファイルを選択してください。")
        return False

    try:
        hanro_name = os.path.splitext(os.path.basename(listing_path))[0]
        listing_df = pd.read_csv(listing_path)
        amazon_df = pd.read_csv(amazon_path)

        listing_urls = listing_df.iloc[:, 0].astype(str).tolist()
        listing_images = listing_df.iloc[:, 3].astype(str).tolist()
        amazon_images = amazon_df.iloc[:, 4].astype(str).tolist()
        amazon_sales = amazon_df.iloc[:, 5].astype(str).tolist()

        amazon_vectors = [get_feature_vector(img) for img in amazon_images]
        output_rows = []

        for idx, (listing_url, listing_img) in enumerate(zip(listing_urls, listing_images)):
            vec1 = get_feature_vector(listing_img)
            if vec1 is None:
                output_rows.append([listing_url, listing_img, hanro_name, "", "", ""])
                continue

            best_score = -1
            best_url = ""
            best_sales = ""

            for i, vec2 in enumerate(amazon_vectors):
                if vec2 is None:
                    continue
                score = cosine_similarity([vec1], [vec2])[0][0]
                if score > best_score:
                    best_score = score
                    best_url = amazon_images[i]
                    best_sales = amazon_sales[i]

            output_rows.append([
                listing_url,
                listing_img,
                hanro_name,
                best_score,
                best_url,
                best_sales
            ])

        output_df = pd.DataFrame(output_rows, columns=[
            "商品URL（他販路）",
            "商品画像URL（他販路）",
            "販路",
            "類似度",
            "最も類似したAmazon画像URL",
            "販売数"
        ])

        output_df.to_csv("類似商品比較リスト.csv", index=False)
        candidate_df = output_df[pd.to_numeric(output_df["類似度"], errors='coerce') < 0.8]
        candidate_df.to_csv("独自商品候補リスト.csv", index=False)

        messagebox.showinfo("完了", "比較が完了しました！\n結果がCSVファイルに出力されました。")
        return True

    except Exception as e:
        messagebox.showerror("処理エラー", str(e))
        return False

# ===== ファイル選択ダイアログ用の関数 =====
def browse_listing():
    global listing_path
    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if path:
        listing_path = path
        listing_label.config(text=path)

def browse_amazon():
    global amazon_path
    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if path:
        amazon_path = path
        amazon_label.config(text=path)

# ===== 処理してウィンドウを閉じる =====
def process_and_close():
    success = process_files()
    if success:
        root.destroy()

# ===== 外部 or main 実行用エントリーポイント =====
def run_unique_checker():
    global root, listing_label, amazon_label
    root = tk.Tk()
    root.title("画像比較ツール")
    FONT = ("メイリオ", 10)

    tk.Label(root, text="他販路情報の選択:", font=FONT).grid(row=0, column=0)
    tk.Button(root, text="参照", command=browse_listing, font=FONT).grid(row=0, column=1)
    listing_label = tk.Label(root, text="未選択", wraplength=300, font=FONT, anchor="w", justify="left")
    listing_label.grid(row=0, column=2, sticky="w")

    tk.Label(root, text="Amazon情報の選択:", font=FONT).grid(row=1, column=0)
    tk.Button(root, text="参照", command=browse_amazon, font=FONT).grid(row=1, column=1)
    amazon_label = tk.Label(root, text="未選択", wraplength=300, font=FONT, anchor="w", justify="left")
    amazon_label.grid(row=1, column=2, sticky="w")

    tk.Button(root, text="OK", command=process_and_close, width=20, font=FONT).grid(row=2, column=0, columnspan=3, pady=10)

    root.update()
    root.mainloop()

# ✅ スクリプト単体で実行された場合に Tk ウィンドウを起動
if __name__ == "__main__":
    run_unique_checker()
