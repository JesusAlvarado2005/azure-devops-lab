import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

# Importing this backend creates RUNTIME_DIR; give the test its own temporary directory.
runtime = tempfile.TemporaryDirectory()
os.environ["RUNTIME_DIR"] = runtime.name
os.environ["LOW_STOCK_THRESHOLD"] = "5"
spec = importlib.util.spec_from_file_location("catalog", Path(__file__).parents[1] / "backend/server.py")
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)

class CatalogTests(unittest.TestCase):
    def test_four_products(self):
        self.assertEqual(len(catalog.PRODUCTS), 4)

    def test_stock_threshold(self):
        self.assertEqual(catalog.enrich(catalog.PRODUCTS[1])["stock_status"], "LOW")
        self.assertEqual(catalog.enrich(catalog.PRODUCTS[0])["stock_status"], "OK")

    def test_counter_persistence(self):
        self.assertEqual(catalog.increment_counter(), 1)
        self.assertEqual(catalog.increment_counter(), 2)
        self.assertEqual(catalog.COUNTER_FILE.read_text(), "2")
