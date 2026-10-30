FROM python:3.13-slim

WORKDIR /app

COPY server.py /app/server.py

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

ENV APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    APP_VERSION=ci-v1

EXPOSE 8000

CMD ["python", "/app/server.py"]
