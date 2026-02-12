from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def keyword_page():
    result = None
    if request.method == "POST":
        rival_review_max = request.form.get("rival_review_max")
        rival_sales_min = request.form.get("rival_sales_min")
        reverse_asin = request.form.get("reverse_asin")
        keyword_review_max = request.form.get("keyword_review_max")
        keyword_sales_min = request.form.get("keyword_sales_min")
        # 仮の処理（本来は keyword_research.py の処理呼び出し）
        result = f"ライバルチェック: 評価数≤{rival_review_max}, 販売数≥{rival_sales_min}<br>" + \
                 f"逆引きリサーチ: ASIN={reverse_asin}<br>" + \
                 f"キーワード分析: 評価数≤{keyword_review_max}, 販売数≥{keyword_sales_min}"
    return render_template("keyword_form.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
