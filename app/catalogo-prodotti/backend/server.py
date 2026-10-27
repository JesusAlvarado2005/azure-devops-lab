#!/usr/bin/env python3

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PRODUCTS = [
    {"id": "P001", "name": "Notebook Pro 14", "category": "Notebook", "price": 1299.0, "stock": 8},
    {"id": "P002", "name": "Monitor 27 UHD", "category": "Monitor", "price": 349.0, "stock": 4},
    {"id": "P003", "name": "Dock USB-C", "category": "Accessori", "price": 119.0, "stock": 15},
    {"id": "P004", "name": "Keyboard Business", "category": "Accessori", "price": 59.0, "stock": 2},
]


def read_int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} deve essere un intero, ricevuto: {raw!r}") from exc


HOST = os.getenv("APP_HOST", "0.0.0.0")
PORT = read_int_env("APP_PORT", 8000)
LOW_STOCK_THRESHOLD = read_int_env("LOW_STOCK_THRESHOLD", 5)
RUNTIME_DIR = Path(os.getenv("RUNTIME_DIR", "/runtime"))
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
COUNTER_FILE = RUNTIME_DIR / "counter.txt"


def enrich(product):
    result = dict(product)
    result["stock_status"] = (
        "LOW" if product["stock"] <= LOW_STOCK_THRESHOLD else "OK"
    )
    return result


def increment_counter():
    current = 0
    if COUNTER_FILE.exists():
        try:
            current = int(COUNTER_FILE.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            current = 0

    current += 1
    COUNTER_FILE.write_text(str(current), encoding="utf-8")
    return current


class Handler(BaseHTTPRequestHandler):
    server_version = "CatalogBackend/2.0"

    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/health":
            return self.send_json(
                {"status": "ok", "service": "catalog-backend", "version": "2.0"}
            )

        if path == "/api/products":
            products = [enrich(p) for p in PRODUCTS]
            return self.send_json({"count": len(products), "products": products})

        if path.startswith("/api/products/"):
            product_id = path.rsplit("/", 1)[-1]
            product = next((p for p in PRODUCTS if p["id"] == product_id), None)
            if product is None:
                return self.send_json(
                    {"error": "product_not_found", "product_id": product_id},
                    HTTPStatus.NOT_FOUND,
                )
            return self.send_json(enrich(product))

        if path == "/api/counter":
            value = increment_counter()
            return self.send_json({"counter": value})

        return self.send_json(
            {"error": "not_found", "path": path},
            HTTPStatus.NOT_FOUND,
        )

    def log_message(self, fmt, *args):
        print(f"[backend] {self.address_string()} - {fmt % args}", flush=True)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(
        f"Catalog backend listening on http://{HOST}:{PORT} "
        f"threshold={LOW_STOCK_THRESHOLD} runtime={RUNTIME_DIR}",
        flush=True,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutdown requested.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
