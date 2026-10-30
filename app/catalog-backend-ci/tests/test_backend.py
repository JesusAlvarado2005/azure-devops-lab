import importlib.util
from pathlib import Path
import unittest

SERVER = Path(__file__).resolve().parents[1] / "server.py"

spec = importlib.util.spec_from_file_location("catalog_server", SERVER)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class CatalogTests(unittest.TestCase):

    def test_health_status(self):
        payload = server.health_payload()
        self.assertEqual(payload["status"], "ok")

    def test_health_version(self):
        payload = server.health_payload()
        self.assertEqual(payload["version"], "ci-v1")

    def test_product_count(self):
        payload = server.products_payload()
        self.assertEqual(payload["count"], 4)


if __name__ == "__main__":
    unittest.main()
