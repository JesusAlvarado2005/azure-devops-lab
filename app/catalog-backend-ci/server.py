#!/usr/bin/env python3

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

APP_VERSION = os.getenv("APP_VERSION", "ci-v2")
HOST = os.getenv("APP_HOST", "0.0.0.0")
PORT = int(os.getenv("APP_PORT", "8000"))

PRODUCTS = [
    {"id": "P001", "name": "Notebook Pro 14", "stock": 8},
    {"id": "P002", "name": "Monitor 27 UHD", "stock": 4},
    {"id": "P003", "name": "Dock USB-C", "stock": 15},
    {"id": "P004", "name": "Keyboard Business", "stock": 2},
]


def health_payload():
    return {
        "status": "ok",
        "service": "catalog-backend",
        "version": APP_VERSION,
    }


def products_payload():
    return {
        "version": APP_VERSION,
        "count": len(PRODUCTS),
        "products": PRODUCTS,
    }


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/health":
            return self.send_json(health_payload())

        if path == "/api/products":
            return self.send_json(products_payload())

        return self.send_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def log_message(self, fmt, *args):
        print(f"[catalog {APP_VERSION}] {fmt % args}", flush=True)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Catalog backend {APP_VERSION} listening on {HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
