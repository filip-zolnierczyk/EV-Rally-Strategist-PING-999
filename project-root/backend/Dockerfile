FROM python:3.11-slim

# Instalujemy curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p /tmp/data && \
    curl -L https://raw.githubusercontent.com/chargeprice/open-ev-data/data-update/data/ev-data.json \
    -o /tmp/data/ev-data.json

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD sh -c "mkdir -p ./app/data && cp /tmp/data/ev-data.json ./app/data/ev-data.json && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"