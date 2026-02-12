FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    chromium chromium-driver curl unzip gnupg \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
