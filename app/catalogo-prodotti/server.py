#!/usr/bin/env python3

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
PRODUCTS_PATH = BASE_DIR / "data" / "products.json"
STATIC_DIR = BASE_DIR / "static"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_config():
    config = load_json(CONFIG_PATH)

    required = {
        "host": str,
        "port": int,
        "api_prefix": str,
        "low_stock_threshold": int,
    }

    for key, expected_type in required.items():
        if key not in config:
            raise ValueError(f"Configurazione mancante: {key}")
        if not isinstance(config[key], expected_type):
            raise ValueError(
                f"Configurazione non valida: {key} deve essere {expected_type.__name__}"
            )

    if not config["api_prefix"].startswith("/"):
        raise ValueError("api_prefix deve iniziare con /")

    return config


def enrich_product(product, threshold):
    result = dict(product)
    result["stock_status"] = "LOW" if product["stock"] <= threshold else "OK"
    return result


class CatalogHandler(SimpleHTTPRequestHandler):
    server_version = "CatalogoProdotti/1.0"

    def _send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        config = load_config()
        api_prefix = config["api_prefix"].rstrip("/")
        path = urlparse(self.path).path

        if path == "/health":
            return self._send_json(
                {
                    "status": "ok",
                    "service": "catalogo-prodotti",
                    "version": "1.0"
                }
            )

        if path == f"{api_prefix}/products":
            products = [
                enrich_product(p, config["low_stock_threshold"])
                for p in load_json(PRODUCTS_PATH)
            ]
            return self._send_json(
                {
                    "count": len(products),
                    "products": products,
                }
            )

        product_prefix = f"{api_prefix}/products/"
        if path.startswith(product_prefix):
            product_id = path[len(product_prefix):]
            products = load_json(PRODUCTS_PATH)
            product = next(
                (p for p in products if p["id"] == product_id),
                None,
            )
            if product is None:
                return self._send_json(
                    {
                        "error": "product_not_found",
                        "product_id": product_id,
                    },
                    status=HTTPStatus.NOT_FOUND,
                )
            return self._send_json(
                enrich_product(product, config["low_stock_threshold"])
            )

        if path == "/":
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def translate_path(self, path):
        parsed = urlparse(path).path
        relative = parsed.lstrip("/")
        return str(STATIC_DIR / relative)

    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {format % args}")


def main():
    config = load_config()
    host = config["host"]
    port = config["port"]

    server = ThreadingHTTPServer((host, port), CatalogHandler)
    print(f"Catalogo prodotti in ascolto su http://{host}:{port}")
    print("Ctrl+C per terminare.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArresto server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
