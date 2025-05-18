# sellersprite_reverse_asin.py
# 逆引きリサーチの実態処理

import requests
import json
import csv

def reverse_keyword_search(asin: str, secret_key: str = "a8e88da3d9e84c0eb7824cf32d9b1848") -> str:
    """
    指定されたASINでSellerSpriteの逆引きキーワード検索を行い、
    上位5件をCSVに出力する。

    Args:
        asin (str): 検索対象のASIN
        secret_key (str): APIのシークレットキー（デフォルトは固定）

    Returns:
        str: 出力されたCSVファイル名
    """
    url = "https://api.sellersprite.com/v1/traffic/keyword"
    headers = {
        "secret-key": secret_key,
        "Content-Type": "application/json;charset=UTF-8"
    }
    payload = {
        "marketplace": "JP",
        "asin": asin
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        items = data["data"].get("items", [])

        # Noneを0に置き換えてトラフィック比率で降順ソート
        sorted_items = sorted(
            items,
            key=lambda x: x.get("trafficPercentage") or 0,
            reverse=True
        )

        # 上位5件に絞る
        top_items = sorted_items[:5]

        filename = f"keywords_top5_{asin}.csv"
        with open(filename, "w", encoding="utf-8-sig", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["キーワード", "検索数", "商品数", "購入数", "購入率", "トラフィック比率"])
            for item in top_items:
                writer.writerow([
                    item.get("keyword", ""),
                    item.get("searches", ""),
                    item.get("products", ""),
                    item.get("purchases", ""),
                    f"{(item.get('purchaseRate') or 0) * 100:.2f}%",
                    f"{(item.get('trafficPercentage') or 0) * 100:.2f}%"
                ])
        print(f"✅ トラフィック比率上位5件を '{filename}' に出力しました。")
        return filename
    else:
        print("❌ データ取得に失敗しました。")
        return ""
