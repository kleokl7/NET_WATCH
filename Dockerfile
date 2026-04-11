FROM python:3.12-slim

WORKDIR /app

# Install system deps for lxml and trafilatura
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data directory for SQLite DB (mount as volume for persistence)
RUN mkdir -p /app/data
ENV DATA_DIR=/app/data

EXPOSE 8080

CMD ["python", "bot.py"]
