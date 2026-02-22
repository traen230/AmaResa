FROM python:3.11-slim

# 環境変数
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリ作成
WORKDIR /app

# 必要なファイルコピー
COPY requirements.txt .

# 依存関係インストール + gunicornも含める
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# アプリケーションコードをコピー
COPY . .

# ポート開放（Render用）
EXPOSE 10000

# スタートコマンド
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
