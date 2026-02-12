from flask import Flask, request, render_template
from scraper import search_google_news

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        keyword = request.form["keyword"]
        results = search_google_news(keyword)
    return render_template("index.html", results=results)
