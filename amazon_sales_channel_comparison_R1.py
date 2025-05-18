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

# ===== モデル読み込み =====
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

# ===== 特徴ベクトル抽出関数 =====
def get_feature_vector(img_path_or_url):
    try:
        if img_path_or_url.startswith("http"):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            clean_url = img_path_or_url.strip()
            response = requests.get(clean_url, headers=headers, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            img = Image.open(img_path_or_url.strip()).convert("RGB")
        img = img.resize((224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        features = model.predict(x)
        return features[0]
    except Exception as e:
        print(f"画像取得エラー: {img_path_or_url} - {e}")
        return None

# ===== CSV比較処理関数 =====
def process_files():
    if not listing_path or not amazon_path:
        messagebox.showerror("エラー", "両方のCSVファイルを選択してください。")
        return

    try:
        # 販路名をファイル名から取得（拡張子除去）
        hanro_name = os.path.splitext(os.path.basename(listing_path))[0]

        listing_df = pd.read_csv(listing_path)
        amazon_df = pd.read_csv(amazon_path)

        listing_urls = listing_df.iloc[:, 0].astype(str).tolist()       # 他販路 商品URL → A列 (index=0)
        listing_images = listing_df.iloc[:, 3].astype(str).tolist()     # 他販路 画像URL → D列 (index=3)
        amazon_images = amazon_df.iloc[:, 4].astype(str).tolist()       # Amazon 画像URL → E列 (index=4)
        amazon_sales = amazon_df.iloc[:, 5].astype(str).tolist()        # Amazon 販売数 → F列 (index=5)

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
                hanro_name,  # ファイル名から取得した販路名
                best_score,
                best_url,
                best_sales
            ])

        # データフレーム化
        output_df = pd.DataFrame(output_rows, columns=[
            "商品URL（他販路）",
            "商品画像URL（他販路）",
            "販路",
            "類似度",
            "最も類似したAmazon画像URL",
            "販売数"
        ])

        # 全体結果
        output_df.to_csv("listing_cosine_results.csv", index=False)

        # 類似度80%以上のみ
        candidate_df = output_df[pd.to_numeric(output_df["類似度"], errors='coerce') < 0.8]
        candidate_df.to_csv("listing_cosine_candidates.csv", index=False)

        messagebox.showinfo(
            "完了",
            "比較が完了しました！\n結果ファイル: listing_cosine_results.csv\n候補リスト: listing_cosine_candidates.csv"
        )
    except Exception as e:
        messagebox.showerror("処理エラー", str(e))

# ===== GUI構築 =====
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

# 初期化
listing_path = ""
amazon_path = ""

root = tk.Tk()
root.title("画像比較ツール")

tk.Label(root, text="他販路情報の選択:").grid(row=0, column=0, sticky="e")
tk.Button(root, text="参照", command=browse_listing).grid(row=0, column=1)
listing_label = tk.Label(root, text="未選択", wraplength=400, anchor="w")
listing_label.grid(row=0, column=2, sticky="w")

tk.Label(root, text="Amazon情報の選択:").grid(row=1, column=0, sticky="e")
tk.Button(root, text="参照", command=browse_amazon).grid(row=1, column=1)
amazon_label = tk.Label(root, text="未選択", wraplength=400, anchor="w")
amazon_label.grid(row=1, column=2, sticky="w")

tk.Button(root, text="OK", command=process_files, width=20).grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()
