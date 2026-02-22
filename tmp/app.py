from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_keyword = request.form['search_keyword']
    count_keyword = request.form['count_keyword']

    url = f'https://html.duckduckgo.com/html/?q={search_keyword}'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        return f"Error during request: {e}"
    soup = BeautifulSoup(res.text, 'html.parser')
    count = soup.text.lower().count(count_keyword.lower())
    return f"検索結果ページ中の「{count_keyword}」の出現数: {count}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
