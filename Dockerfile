FROM python:3.15-slim

ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY models ./models

RUN useradd --create-home app && chown -R app /app
USER app

EXPOSE 8000
CMD ["sh", "-c", "uvicorn lysis.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
