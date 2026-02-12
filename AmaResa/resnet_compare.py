# resnet_compare.py
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import requests
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image

# ResNet50モデルをグローバルで読み込み（重複防止）
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def get_feature_vector(img_url):
    """画像URLからResNet特徴量(2048次元)を抽出"""
    try:
        if img_url.startswith("//"):
            img_url = "https:" + img_url

        response = requests.get(img_url.strip(), timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = img.resize((224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        return model.predict(x, verbose=1)[0]
    except Exception as e:
        print(f"画像取得エラー: {img_url} - {e}")
        return None

def load_amazon_images(csv_path):
    """Amazon検索結果CSVから画像URLと商品名を読み出す（列名: 画像URL, 商品名 を想定）"""
    df = pd.read_csv(csv_path)
    image_urls = df['画像URL'].astype(str).tolist()
    titles = df['商品名'].astype(str).tolist()
    return [{"title": title, "image_url": url} for title, url in zip(titles, image_urls)]

def compare_images_with_resnet(other_items, amazon_items, threshold=0.7):
    """
    他販路アイテムとAmazonアイテムの画像類似度を比較し、
    「最大コサイン類似度 < threshold」のみを抽出して返す。
    threshold: 0.0～1.0（デフォルト0.7）
    """
    # 閾値のガード
    try:
        threshold = float(threshold)
    except Exception:
        threshold = 0.7
    threshold = max(0.0, min(1.0, threshold))

    result = []
    for item in other_items:
        try:
            # データ形式に応じて柔軟に分解
            if len(item) == 5:
                title, _, sales, product_url, image_url = item
                rating = "N/A"
                review = "N/A"
                rank = "N/A"
            elif len(item) == 4:
                title, sales, product_url, image_url = item
                rating = "N/A"
                review = "N/A"
                rank = "N/A"
            elif len(item) == 6:
                title, review, product_url, image_url, rating, rank = item
                sales = "N/A"  # 楽天には販売数の概念がないため仮値
            else:
                print(f"[SKIP] データ形式不正: {item}")
                continue

            vec1 = get_feature_vector(image_url)
            if vec1 is None:
                continue

            max_score = -1.0
            for a_item in amazon_items:
                vec2 = get_feature_vector(a_item['image_url'])
                if vec2 is None:
                    continue
                score = cosine_similarity([vec1], [vec2])[0][0]
                if score > max_score:
                    max_score = score

            if max_score < threshold:
                result.append({
                    "商品名": title,
                    "商品URL": product_url,
                    "画像URL": image_url,
                    "販売数": sales,
                    "評価数": review,
                    "評価値": rating,
                    "ランキング": rank,
                    "類似度": round(float(max_score), 3) if max_score >= 0 else ""
                })
        except Exception as e:
            print(f"[SKIP] 処理失敗: {e}")
            continue
    return result
