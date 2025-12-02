FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# КЛЮЧЕВОЙ МОМЕНТ: используем gunicorn + uvicorn.worker
CMD ["gunicorn", "--bind", "0.0.0.0:8080", \
     "--workers", "1", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "600", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "main_bot:app"]