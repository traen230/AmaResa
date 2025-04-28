import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import requests
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity

# ===== モデル読み込み =====
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

# ===== 特徴ベクトル抽出関数 =====
def get_feature_vector(img_path_or_url):
    try:
        if img_path_or_url.startswith("http"):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }
            clean_url = img_path_or_url.strip()  # ← スペース除去
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
        listing_df = pd.read_csv(listing_path)
        amazon_df = pd.read_csv(amazon_path)

        listing_images = listing_df.iloc[:, 3].astype(str).tolist()     # 他販路 E列
        amazon_images = amazon_df.iloc[:, 2].astype(str).tolist()       # Amazon D列

        # 先にAmazon側の特徴量を取得
        amazon_vectors = [get_feature_vector(img) for img in amazon_images]

        similarities = []
        closest_urls = []
        similarity_flags = []

        for listing_img in listing_images:
            vec1 = get_feature_vector(listing_img)
            if vec1 is None:
                similarities.append("")
                closest_urls.append("")
                similarity_flags.append("")
                continue

            best_score = -1
            best_url = ""

            for i, vec2 in enumerate(amazon_vectors):
                if vec2 is None:
                    continue
                score = cosine_similarity([vec1], [vec2])[0][0]
                if score > best_score:
                    best_score = score
                    best_url = amazon_images[i]

            similarities.append(best_score)
            closest_urls.append(best_url)
            similarity_flags.append("類似画像の可能性あり" if best_score >= 0.8 else "")

        # 結果列を追加
        listing_df["cos類似度"] = similarities
        listing_df["最も類似した画像URL"] = closest_urls
        listing_df["類似画像判定"] = similarity_flags

        # 結果を保存
        output_path = "listing_cosine_results.csv"
        listing_df.to_csv(output_path, index=False)

        messagebox.showinfo("完了", f"比較が完了しました！\n結果ファイル: {output_path}")
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
