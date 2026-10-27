FROM python:3.13-slim

WORKDIR /app

COPY backend/server.py /app/server.py

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /runtime \
    && chown -R appuser:appuser /app /runtime

USER appuser

ENV APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    LOW_STOCK_THRESHOLD=5 \
    RUNTIME_DIR=/runtime

EXPOSE 8000

CMD ["python", "/app/server.py"]
