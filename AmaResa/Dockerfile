FROM python:3.11-slim

# 必要なLinuxパッケージをインストール
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# ChromeとChromedriverのパスを明示
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# 作業ディレクトリを作成
WORKDIR /app

# 必要ファイルをコピー
COPY requirements.txt requirements.txt

# Python依存をインストール
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーション全体をコピー
COPY . /app

# ポート開放（Flaskアプリ用）
EXPOSE 10000

# Gunicornで本番起動
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
